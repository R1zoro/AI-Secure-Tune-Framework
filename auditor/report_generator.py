# auditor/report_generator.py

import pandas as pd
from datetime import datetime
from pathlib import Path

"""
This module handles the generation of the final audit report.

This is the primary file for Person 3 (Orchestration & Reporting Lead) to develop.
"""

def generate_report(results_df: pd.DataFrame, output_dir: Path):
    """
    Generates a summary report from the audit results DataFrame.
    
    Args:
        results_df (pd.DataFrame): DataFrame containing the detailed audit results.
        output_dir (Path): A pathlib.Path object for the directory to save reports in.
    """
    print("\n[+] Generating audit report...")
    
    # --- Create a summary ---
    total_prompts = len(results_df)
    pii_failures = results_df['pii_detected'].sum()
    secrets_failures = results_df['secrets_detected'].sum()
    jailbreak_failures = results_df['jailbreak_detected'].sum()
    
    total_failures = int(pii_failures + secrets_failures + jailbreak_failures)
    overall_status = "FAIL" if total_failures > 0 else "PASS"

    # --- Generate a timestamp for the report files ---
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Use the Path object to construct the base path for the report files
    report_basename = output_dir / f"audit_report_{timestamp}"

    # --- Write Markdown Report (for Person 3 to improve) ---
    md_report_path = f"{str(report_basename)}.md"
    try:
        with open(md_report_path, "w") as f:
            f.write("# Secure Tune Audit Report\n\n")
            f.write(f"**Date & Time:** {timestamp}\n")
            f.write(f"**Overall Status:** <font color='{ 'red' if overall_status == 'FAIL' else 'green' }'>{overall_status}</font>\n\n")
            f.write("## Summary\n")
            f.write(f"- **Total Prompts Tested:** {total_prompts}\n")
            f.write(f"- **Total Failures:** {total_failures}\n")
            f.write(f"  - PII Detections: {int(pii_failures)}\n")
            f.write(f"  - Secrets Detections: {int(secrets_failures)}\n")
            f.write(f"  - Jailbreak Detections: {int(jailbreak_failures)}\n\n")
            f.write("## Detailed Failures\n\n")
            
            failed_tests = results_df[results_df['final_result'] == 'FAIL']
            if failed_tests.empty:
                f.write("No failures detected.\n")
            else:
                # Only show failed tests in the summary MD file
                f.write(failed_tests.to_markdown(index=False))

        print(f"[SUCCESS] Markdown report saved to {md_report_path}")
    except Exception as e:
        print(f"[ERROR] Failed to write Markdown report: {e}")

    # --- Save full results to CSV for detailed analysis ---
    csv_report_path = f"{str(report_basename)}_full_details.csv"
    try:
        results_df.to_csv(csv_report_path, index=False)
        print(f"[SUCCESS] Full CSV report saved to {csv_report_path}")
    except Exception as e:
        print(f"[ERROR] Failed to write CSV report: {e}")