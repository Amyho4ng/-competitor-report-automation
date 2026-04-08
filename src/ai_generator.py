import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from openai import OpenAI
import time
import re

from sources import COMPETITOR_SOURCES

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}
TIMEOUT = 10
MAX_LINKS = 30
PAUSE = 1.5

DATE_FORMATS = [
    "%B %d, %Y",
    "%d %B %Y",
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%b %d, %Y",
    "%d %b %Y",
]

def parse_date(text: str):
    text = text.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def extract_date_from_page(soup: BeautifulSoup):
    # Strategy 1: meta tags
    for meta_name in [
        "article:published_time",
        "datePublished",
        "date",
        "pubdate",
        "og:published_time",
        "publish_date",
        "article:modified_time",
    ]:
        tag = soup.find("meta", attrs={"property": meta_name}) or \
              soup.find("meta", attrs={"name": meta_name})
        if tag and tag.get("content"):
            content = tag["content"][:10]
            dt = parse_date(content)
            if dt:
                return dt.strftime("%B %d, %Y")

    # Strategy 2: <time> elements
    for time_tag in soup.find_all("time"):
        dt_attr = time_tag.get("datetime", "")
        if dt_attr:
            dt = parse_date(dt_attr[:10])
            if dt:
                return dt.strftime("%B %d, %Y")
        dt = parse_date(time_tag.get_text(strip=True))
        if dt:
            return dt.strftime("%B %d, %Y")

    # Strategy 3: JSON-LD structured data
    for script in soup.find_all("script", type="application/ld+json"):
        text = script.string or ""
        match = re.search(r'"datePublished"\s*:\s*"([^"]+)"', text)
        if match:
            dt = parse_date(match.group(1)[:10])
            if dt:
                return dt.strftime("%B %d, %Y")

    # Strategy 4: common CSS class/id patterns
    date_selectors = [
        {"class": re.compile(r"date|publish|posted|time", re.I)},
        {"id": re.compile(r"date|publish|posted|time", re.I)},
    ]
    for selector in date_selectors:
        for tag in soup.find_all(True, selector):
            text = tag.get_text(strip=True)
            match = re.search(
                r'\b(\d{1,2}\s+\w+\s+\d{4}|\w+\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2})\b',
                text
            )
            if match:
                dt = parse_date(match.group(1))
                if dt:
                    return dt.strftime("%B %d, %Y")

    return None


def scrape_links(url: str, cutoff: datetime) -> list[dict]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except Exception as e:
        print(f"    [scrape] Could not fetch {url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    base = url.split("/")[0] + "//" + url.split("/")[2]

    candidates = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        href = a["href"]

        if not text or len(text) < 15:
            continue
        if href.startswith("#") or "javascript:" in href:
            continue
        if any(s in href for s in ["twitter.com", "linkedin.com", "facebook.com", "youtube.com"]):
            continue

        if href.startswith("/"):
            href = base + href
        elif not href.startswith("http"):
            continue

        candidates.append({"text": text, "href": href})

    seen = set()
    unique = []
    for l in candidates:
        if l["href"] not in seen:
            seen.add(l["href"])
            unique.append(l)

    results = []
    for item in unique[:MAX_LINKS]:
        time.sleep(0.5)
        try:
            art_resp = requests.get(item["href"], headers=HEADERS, timeout=TIMEOUT)
            art_resp.raise_for_status()
            art_soup = BeautifulSoup(art_resp.text, "html.parser")
            date_str = extract_date_from_page(art_soup)
        except Exception:
            date_str = None

        if date_str:
            dt = parse_date(date_str)
            if dt and dt >= cutoff:
                results.append({
                    "text": item["text"],
                    "href": item["href"],
                    "date": date_str,
                })

    return results


def scrape_competitor(company: str, urls: list[str], cutoff: datetime) -> list[dict]:
    all_links = []
    for url in urls:
        print(f"    Fetching: {url}")
        links = scrape_links(url, cutoff)
        all_links.extend(links)
        time.sleep(PAUSE)

    seen = set()
    unique = []
    for l in all_links:
        if l["href"] not in seen:
            seen.add(l["href"])
            unique.append(l)

    return unique


def format_with_gpt(company: str, links: list[dict]) -> str:
    client = OpenAI()

    if not links:
        return f"### {company}\n- No recent news found in the past two weeks."

    link_block = "\n".join(
        f"{i+1}. {l['text']} ({l['date']}) — {l['href']}"
        for i, l in enumerate(links)
    )

    prompt = f"""You are formatting a competitor intelligence report for {company}.

Below are real, verified news items with confirmed publication dates.
Format each one as a single bullet line in this exact format:
- Headline (Month DD, YYYY) — Source: https://url

Rules:
- Use the date and URL EXACTLY as given. Do not change, invent, or modify anything.
- Clean up the headline text if it is messy (e.g. remove extra whitespace).
- One line per item. No preamble, no commentary.

Items:
{link_block}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )

    raw = response.choices[0].message.content.strip()

    bullets = [
        line.strip()
        for line in raw.splitlines()
        if line.strip().startswith("- ")
    ]

    if bullets:
        return f"### {company}\n" + "\n".join(bullets)
    else:
        return f"### {company}\n- No recent news found in the past two weeks."


def generate_competitor_insights(period_label: str) -> str:
    cutoff = datetime.today() - timedelta(weeks=2)
    sections = []

    for company, urls in COMPETITOR_SOURCES.items():
        print(f"\n[{company}]")
        links = scrape_competitor(company, urls, cutoff)
        print(f"    Found {len(links)} verified recent articles")
        section = format_with_gpt(company, links)
        sections.append(section)

    return "\n\n".join(sections)