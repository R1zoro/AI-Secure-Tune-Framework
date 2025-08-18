# auditor/audit_manager.py

import pandas as pd
import requests
import time
from tqdm import tqdm
from pathlib import Path
import logging
import glob
from config import setup_logger
from evaluators import run_all_scanners, check_for_backdoor
from report_generator import generate_report

# Setup the logger 
logger = setup_logger()

#  Configuration 
MODEL_API_URL = "http://localhost:5000/generate"
PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
TEST_DATA_DIR = PROJECT_ROOT / "test_data"


def run_audit():
    """Main function to orchestrate the entire audit process."""
    logger.info("Initializing Audit Manager...")
    
    # Find all test files 
    all_test_files = glob.glob(f"{TEST_DATA_DIR}/*.csv")
    if not all_test_files:
        logger.error(f"No test data files (.csv) found in {TEST_DATA_DIR}. Aborting.")
        return
        
    logger.info(f"Found {len(all_test_files)} test suites to run.")
    
    all_results = []

    # Loop through each test file 
    for test_file_path in all_test_files:
        test_suite_name = Path(test_file_path).stem
        logger.info(f"--- Running Test Suite: {test_suite_name} ---")
        
        try:
            test_prompts_df = pd.read_csv(test_file_path)
        except Exception as e:
            logger.error(f"Failed to load {test_file_path}: {e}. Skipping this suite.")
            continue

        for index, row in tqdm(test_prompts_df.iterrows(), total=test_prompts_df.shape[0], desc=test_suite_name):
            prompt_id = row['id']
            prompt_text = row['prompt']
            model_output = ""
            api_error = None

            try:
                payload = {"prompt": prompt_text, "max_new_tokens": 100}
                response = requests.post(MODEL_API_URL, json=payload, timeout=30)
                
                if response.status_code == 200:
                    model_output = response.json().get("response", "")
                else:
                    api_error = f"API Error: Status {response.status_code} - {response.text}"
            except requests.exceptions.RequestException as e:
                api_error = f"API Connection Error: {e}"
            
            if api_error:
                logger.warning(f"\nAPI Error for prompt {prompt_id}: {api_error}")
                result_row = {"prompt_id": prompt_id, "prompt": prompt_text, "response": "API_ERROR", "final_result": "ERROR", "test_suite": test_suite_name}
                all_results.append(result_row)
                continue

            scanner_results = run_all_scanners(prompt_text, model_output)
            backdoor_result = check_for_backdoor(model_output)
            
            is_fail = any(scanner_results.values()) or backdoor_result['detected']
            
            result_row = {
                "test_suite": test_suite_name,
                "prompt_id": prompt_id,
                "prompt": prompt_text,
                "response": model_output.strip(),
                **scanner_results,
                "backdoor_detected": backdoor_result['detected'],
                "final_result": "FAIL" if is_fail else "PASS"
            }
            all_results.append(result_row)

    if not all_results:
        logger.warning("No results were generated. Skipping report.")
        return
        
    results_df = pd.DataFrame(all_results)
    REPORTS_DIR.mkdir(exist_ok=True)
    generate_report(results_df, output_dir=REPORTS_DIR)


if __name__ == "__main__":
    run_audit()