
import datetime

with open("task_log.txt", "a") as f:
    f.write(f"STARTED at {datetime.datetime.now()}\n")

import os

import report_builder
print(">>> USING REPORT_BUILDER FROM:", report_builder.__file__)
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
load_dotenv()
from config import load_config
from ai_generator import generate_competitor_insights
from report_builder import build_html_report


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

    print(f" Report saved at: {filepath}")

def main():
    cfg = load_config()

    start_date, end_date = get_last_14_days()
    period_label = f"{start_date} to {end_date}"

    print(f" Generating competitor insights for: {period_label}")

    summary = generate_competitor_insights(period_label)

    print("----- RAW AI SUMMARY START -----")
    print(summary)
    print("----- RAW AI SUMMARY END -----")

    html = build_html_report(summary, period_label)

    print("----- HTML OUTPUT START -----")
    print(html[:500])
    print("----- HTML OUTPUT END -----")

    save_report(html, start_date, end_date)

    print("✅ Report generation complete.")

if __name__ == "__main__":
    main()

    
with open("task_log.txt", "a") as f:
    f.write(f"FINISHED at {datetime.datetime.now()}\n")
