import datetime
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
load_dotenv()

import report_builder
print(">>> USING REPORT_BUILDER FROM:", report_builder.__file__)

from config import load_config
from ai_generator import generate_competitor_insights
from report_builder import build_html_report

LOG_FILE = os.path.join(os.path.dirname(__file__), "run_log.txt")

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{msg}\n")

def get_last_14_days():
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=14)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

def save_report(html_content, start_date, end_date):
    folder = r"C:\Users\AmyHoang\OneDrive - Kubrick Group\Bids and Proposals - competitor analysis"
    os.makedirs(folder, exist_ok=True)
    filename = f"competitor_report_{start_date}_to_{end_date}.html"
    filepath = os.path.join(folder, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Report saved at: {filepath}")

def main():
    log(f"STARTED at {datetime.now()}")
    try:
        cfg = load_config()
        start_date, end_date = get_last_14_days()
        period_label = f"{start_date} to {end_date}"
        print(f"Generating competitor insights for: {period_label}")

        summary = generate_competitor_insights(period_label)
        html = build_html_report(summary, period_label)
        save_report(html, start_date, end_date)

        print("Report generation complete.")
        log(f"FINISHED successfully at {datetime.now()}")
    except Exception as e:
        log(f"ERROR at {datetime.now()}: {e}")
        raise

if __name__ == "__main__":
    main()