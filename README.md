# -competitor-report-automation

# Competitor Report Automation

Runs every 2 weeks, scrapes competitor newsrooms, generates an HTML report
and saves it to SharePoint where Power Automate emails it out.

## Setup

### 1. Install Python
Download Python 3.11+ from https://www.python.org

### 2. Install dependencies
Open a terminal in this folder and run:
    pip install -r requirements.txt

### 3. Set up the API key
Create a file called `.env` in the root folder containing:
    OPENAI_API_KEY=sk-your-key-here

Get the key from Nat

### 4. Set up Task Scheduler
- Open Windows Task Scheduler
- Create Basic Task called "Competitor Report"
- Trigger: Weekly, every 2 weeks, pick a Monday at 8am
- Action: Start a program → browse to run_report.bat


To temporarily pause it:

Open Task Scheduler
Find your "Competitor Report" task
Right click → Disable
Right click → Enable to turn it back on

To permanently delete it:

Open Task Scheduler
Find your "Competitor Report" task
Right click → Delete

### 5. Power Automate
The flow is called "Competitor Report Email" in Power Automate.
It triggers when a new file is created in:
OneDrive - Kubrick Group > Bids and Proposals - competitor analysis

## Files
- src/main.py          — entry point, runs everything
- src/ai_generator.py  — scrapes newsrooms and calls GPT
- src/sources.py       — list of competitor URLs (update this to add/remove competitors)
- src/report_builder.py — builds the HTML report
- run_report.bat       — used by Task Scheduler to run the script

## Adding or removing competitors
Open src/sources.py and add or remove entries from COMPETITOR_SOURCES.
Each entry needs a company name and a list of newsroom/blog URLs.