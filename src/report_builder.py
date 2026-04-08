import re

def build_html_report(summary, period_label):
    html = []

    html.append("<html>")
    html.append("<head>")
    html.append("<style>")
    html.append("body { font-family: Arial, Helvetica, sans-serif; margin: 40px; color: #222; line-height: 1.6; }")
    html.append("h1 { font-size: 28px; font-weight: bold; margin-bottom: 5px; }")
    html.append(".date-range { font-size: 16px; color: #555; margin-bottom: 25px; }")
    html.append("h2 { font-size: 22px; margin-top: 35px; font-weight: bold; color: #333; border-bottom: 1px solid #ddd; padding-bottom: 5px; }")
    html.append("ul { padding-left: 22px; margin-top: 10px; }")
    html.append("li { margin-bottom: 10px; }")
    html.append("a { color: #0066cc; text-decoration: none; }")
    html.append("</style>")
    html.append("</head>")

    html.append("<body>")
    html.append("<h1>Bi‑Weekly Competitor Report</h1>")
    html.append(f"<div class='date-range'>{period_label}</div>")

    html.append(format_sections(summary))

    html.append("</body>")
    html.append("</html>")

    return "\n".join(html)


def format_sections(summary_text):
    lines = summary_text.split("\n")

    output = []
    current_company = None
    bullets = []

    # FIX: removed $ anchor so date can appear anywhere in the line
    date_pattern = re.compile(r"\([A-Za-z]+ \d{1,2}, \d{4}\)")
    # Example: Source: https://...
    source_pattern = re.compile(r"—?\s*Source:\s*(https?://\S+)", re.IGNORECASE)

    def flush():
        nonlocal output, current_company, bullets
        if current_company and bullets:
            output.append(f"<h2>{current_company}</h2>")
            output.append("<ul>")
            for headline, url in bullets:
                if url:
                    output.append(f"<li>{headline} — <a href='{url}' target='_blank'>Source</a></li>")
                else:
                    output.append(f"<li>{headline}</li>")
            output.append("</ul>")
        current_company = None
        bullets = []

    for line in lines:
        s = line.strip()
        if not s:
            continue

        # Company names
        if s.startswith("### "):
            flush()
            current_company = s.replace("###", "").strip()
            continue

        if s.startswith("#### "):
            flush()
            current_company = s.replace("####", "").strip()
            continue

        # Bullet format: - text (date) — Source: URL
        if s.startswith("- "):
            bullet = s[2:].strip()

            # FIX: date can appear anywhere in the bullet, not just at the end
            if not date_pattern.search(bullet):
                continue

            # Extract URL if available
            src_match = source_pattern.search(bullet)
            url = src_match.group(1) if src_match else None

            # Remove "— Source: URL" from display text
            bullet_clean = source_pattern.sub("", bullet).strip()
            bullet_clean = bullet_clean.replace("**", "").strip()
            # Clean up any trailing em-dash left over
            bullet_clean = re.sub(r"\s*—\s*$", "", bullet_clean).strip()

            bullets.append((bullet_clean, url))
            continue

    flush()
    return "\n".join(output)