# auditor/report_generator.py
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def generate_report(results_df: pd.DataFrame, output_dir: Path):
    """Generates the final, polished audit report for the demo."""
    logger.info("Generating final polished audit report...")
    
    #  Overall Summary 
    total_prompts = len(results_df)
    total_failures = int(results_df['final_result'].value_counts().get('FAIL', 0))
    overall_status = "FAIL" if total_failures > 0 else "PASS"

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_basename = output_dir / f"audit_report_{timestamp}"
    md_report_path = f"{str(report_basename)}.md"

    #  Create summary table 
    summary_data = []
    test_suites = results_df['test_suite'].unique()
    for suite in test_suites:
        suite_df = results_df[results_df['test_suite'] == suite]
        suite_total = len(suite_df)
        suite_failures = int(suite_df['final_result'].value_counts().get('FAIL', 0))
        pass_rate = f"{((suite_total - suite_failures) / suite_total) * 100:.1f}%" if suite_total > 0 else "N/A"
        status_emoji = "✅" if suite_failures == 0 else "❌"
        summary_data.append([suite, status_emoji, suite_total, suite_failures, pass_rate])
    
    summary_df = pd.DataFrame(summary_data, columns=["Test Suite", "Status", "Prompts", "Failures", "Pass Rate"])

    try:
        with open(md_report_path, "w") as f:
            f.write("# Secure Tune Audit Report\n\n")
            f.write(f"Date & Time:** {timestamp}\n")
            f.write(f"Overall Status:** **<font color='{ 'red' if overall_status == 'FAIL' else 'green' }'>{overall_status}</font>**\n\n")
            
            f.write("## Executive Summary\n\n")
            f.write("This report details the results of an automated security audit against the target language model. The model was tested against several suites of prompts designed to detect policy violations, adversarial attacks, and other vulnerabilities.\n\n")
            f.write(summary_df.to_markdown(index=False))
            f.write("\n\n---\n\n")
            
            f.write("detailed Failure Analysis\n\n")
            failed_tests = results_df[results_df['final_result'] == 'FAIL']
            if failed_tests.empty:
                f.write(" **Excellent!** All tests passed across all suites. No failures were detected.\n")
            else:
                f.write("The following prompts resulted in a `FAIL` verdict. Each entry details the prompt, the model's problematic response, and the specific security scanners that were triggered.\n\n")
                detection_columns = [col for col in failed_tests.columns if col.endswith('_detected')]
                
                for index, row in failed_tests.iterrows():
                    f.write(f"###  실패: `{row['test_suite']}` / Prompt ID: `{row['prompt_id']}`\n\n") 
                    f.write(f"**Prompt:**\n```\n{row['prompt']}\n```\n\n")
                    f.write(f"**Model Response:**\n```\n{row['response']}\n```\n\n")
                    
                    # ttO Find which specific scanners were triggered for this failure
                    triggered_scanners = [col.replace('_detected', '').title() for col in detection_columns if row[col] == True]
                    f.write(f"** Triggered Scanners:** `{', '.join(triggered_scanners)}`\n\n")
                    f.write("---\n")
            
        logger.info(f"Markdown report saved to {md_report_path}")
    except Exception as e:
        logger.error(f"Failed to write Markdown report: {e}", exc_info=True)

    # Save full results to CSV (unchanged) 
    csv_report_path = f"{str(report_basename)}_full_details.csv"
    try:
        results_df.to_csv(csv_report_path, index=False)
        logger.info(f"Full CSV report saved to {csv_report_path}")
    except Exception as e:
        logger.error(f"Failed to write CSV report: {e}")