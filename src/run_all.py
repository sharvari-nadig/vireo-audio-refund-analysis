import subprocess
import sys


SCRIPTS = [
    "clean_data.py",
    "refund_report.py",
    "classify_reasons.py",
    "agent_analysis.py",
    "create_evaluation_sample.py",
]


def run_script(script_name):
    print("\n" + "=" * 70)
    print(f"RUNNING: {script_name}")
    print("=" * 70)

    result = subprocess.run(
        [sys.executable, f"src/{script_name}"]
    )

    if result.returncode != 0:
        print(f"\nERROR: {script_name} failed.")
        sys.exit(result.returncode)

def main():
    print("=" * 70)
    print("VIREO AUDIO — REFUND ANALYSIS PIPELINE")
    print("=" * 70)

    for script in SCRIPTS:
        run_script(script)

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)

    print("\nGenerated outputs:")
    print("  out/clean_tickets.csv")
    print("  out/monthly_refunds.csv")
    print("  out/monthly_refunds_by_reason.csv")
    print("  out/monthly_refunds_by_agent.csv")
    print("  out/refunds_by_reason_total.csv")
    print("  out/refunds_by_agent_total.csv")
    print("  out/reconciliation.csv")
    print("  out/classified_refunds.csv")
    print("  out/potential_reason_mismatches.csv")
    print("  eval/manual_review_sample.csv")


if __name__ == "__main__":
    main()