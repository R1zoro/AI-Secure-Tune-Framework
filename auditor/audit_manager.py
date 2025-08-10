# auditor/audit_manager.py

import pandas as pd
import requests
import time
from tqdm import tqdm
from pathlib import Path

# Import the evaluator and reporter functions from our other modules
from evaluators import check_for_pii, check_for_secrets, check_for_jailbreak
from report_generator import generate_report

# --- Configuration using robust paths ---
MODEL_API_URL = "http://localhost:5000/generate"

# Path(__file__) is the path to this current script (audit_manager.py)
# .parent gives us its directory ('auditor')
# .parent again gives us the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
TEST_FILE_PATH = PROJECT_ROOT / "test_data" / "policy_violation_prompts.csv"
REPORTS_DIR = PROJECT_ROOT / "reports"


def run_audit():
    """
    Main function to orchestrate the entire audit process.
    """
    print("[*] Initializing Audit Manager...")
    
    if not TEST_FILE_PATH.is_file():
        print(f"[ERROR] Test data file not found at: {TEST_FILE_PATH}. Aborting.")
        return

    try:
        test_prompts_df = pd.read_csv(TEST_FILE_PATH)
        print(f"[*] Loaded {len(test_prompts_df)} prompts from {TEST_FILE_PATH.name}")
    except Exception as e:
        print(f"[ERROR] Failed to load test data CSV: {e}. Aborting.")
        return

    results = []
    
    # Use tqdm for a user-friendly progress bar
    for index, row in tqdm(test_prompts_df.iterrows(), total=test_prompts_df.shape[0], desc="Auditing Model"):
        prompt_id = row['id']
        prompt_text = row['prompt']
        model_output = ""
        api_error = None

        # --- Step 1: Get model response from the sandboxed API ---
        try:
            payload = {"prompt": prompt_text, "max_new_tokens": 100}
            response = requests.post(MODEL_API_URL, json=payload, timeout=30) # 30-second timeout
            
            if response.status_code == 200:
                model_output = response.json().get("response", "")
            else:
                api_error = f"API Error: Status {response.status_code} - {response.text}"
        except requests.exceptions.RequestException as e:
            api_error = f"API Connection Error: {e}"
        
        # If there was an error, log it and continue to the next prompt
        if api_error:
            print(f"\n[WARNING] Could not get response for prompt {prompt_id}: {api_error}")
            results.append({
                "prompt_id": prompt_id, "prompt": prompt_text, "response": "API_ERROR",
                "pii_detected": False, "secrets_detected": False, "jailbreak_detected": False,
                "final_result": "ERROR"
            })
            continue

        # --- Step 2: Run the response through all evaluators ---
        pii_result = check_for_pii(model_output)
        secrets_result = check_for_secrets(model_output)
        jailbreak_result = check_for_jailbreak(model_output)
        
        # --- Step 3: Aggregate results and determine pass/fail for the prompt ---
        is_fail = pii_result['detected'] or secrets_result['detected'] or jailbreak_result['detected']
        
        results.append({
            "prompt_id": prompt_id,
            "prompt": prompt_text,
            "response": model_output.strip(),
            "pii_detected": pii_result['detected'],
            "secrets_detected": secrets_result['detected'],
            "jailbreak_detected": jailbreak_result['detected'],
            "final_result": "FAIL" if is_fail else "PASS"
        })

    # --- Step 4: Pass the final results to the report generator ---
    if not results:
        print("[WARNING] No results were generated. Skipping report.")
        return
        
    results_df = pd.DataFrame(results)
    
    # Ensure the reports directory exists before trying to write to it
    REPORTS_DIR.mkdir(exist_ok=True)
    generate_report(results_df, output_dir=REPORTS_DIR)


if __name__ == "__main__":
    run_audit()