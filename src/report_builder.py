import re
import html as html_lib

import re
import html as html_lib

import base64
import os

def get_logo_base64():
    logo_path = os.path.join(os.path.dirname(__file__), "Kubrick_Logo_white.png")
    with open(logo_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"

def build_html_report(summary, period_label):
    html = []
    html.append("<html>")
    html.append("<head>")
    html.append("<meta charset='UTF-8'>")
    html.append("<style>")
    html.append("""
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Arial, Helvetica, sans-serif; 
            background-color: #f4f4f4; 
            color: #222; 
            line-height: 1.6; 
        }
        .header {
            background-color: #1a1a2e;
            padding: 24px 40px;
            color: white;
        }
        .header h1 {
            font-size: 26px;
            font-weight: bold;
            color: white;
            margin-bottom: 4px;
        }
        .header .date-range {
            font-size: 14px;
            color: #14F279;
        }
        .subheader {
            background-color: #f0f4ff;
            border-left: 4px solid #1a1a2e;
            padding: 12px 40px;
            font-size: 14px;
            color: #444;
        }
        .container {
            max-width: 860px;
            margin: 30px auto;
            padding: 0 20px;
        }
        .company-card {
            background-color: #ffffff;
            border-radius: 6px;
            border: 1px solid #e0e0e0;
            margin-bottom: 20px;
            overflow: hidden;
        }
        .company-card h2 {
            background-color: #1a1a2e;
            color: white;
            font-size: 16px;
            font-weight: bold;
            padding: 10px 20px;
        }
        .company-card ul {
            padding: 14px 20px 14px 34px;
            margin: 0;
        }
        .company-card li {
            margin-bottom: 10px;
            font-size: 14px;
            color: #333;
        }
        a { 
            color: #0055cc; 
            text-decoration: none; 
            font-weight: bold;
        }
        a:hover { text-decoration: underline; }
        .footer {
            text-align: center;
            padding: 20px;
            font-size: 12px;
            color: #888;
        }
    """)
    html.append("</style>")
    html.append("</head>")
    html.append("<body>")

   # Header
    logo = get_logo_base64()
    html.append("<div class='header'>")
    html.append("<div style='display:flex; justify-content:space-between; align-items:center;'>")
    html.append("<div>")
    html.append("<h1>Bi-Weekly Competitor Report</h1>")
    html.append(f"<div class='date-range'>{period_label}</div>")
    html.append("</div>")
    html.append(f"<img src='{logo}' style='height:50px; object-fit:contain;'>")
    html.append("</div>")
    html.append("</div>")
    
    # Subheader
    html.append("<div class='subheader'>")
    html.append("This report was automatically generated and covers news and updates from key competitors over the past two weeks.")
    html.append("</div>")

    # Content
    html.append("<div class='container'>")
    html.append(format_sections(summary))
    html.append("</div>")

    # Footer
    html.append("<div class='footer'>Best regards, Competitor Intelligence Automation</div>")

    html.append("</body>")
    html.append("</html>")
    return "\n".join(html)


def format_sections(summary_text):
    lines = summary_text.split("\n")
    output = []
    current_company = None
    bullets = []

    url_pattern = re.compile(r'\[URL:\s*(https?://\S+)\]', re.IGNORECASE)

    def flush():
        nonlocal current_company, bullets
        if current_company and bullets:
            output.append("<div class='company-card'>")
            output.append(f"<h2>{html_lib.escape(current_company)}</h2>")
            output.append("<ul>")
            for bullet_text, url in bullets:
                safe_text = html_lib.escape(bullet_text)
                if url and url.startswith("http"):
                    output.append(
                        f"<li>{safe_text} — "
                        f"<a href='{url}' target='_blank'>Read more</a></li>"
                    )
                else:
                    output.append(f"<li>{safe_text}</li>")
            output.append("</ul>")
            output.append("</div>")
        current_company = None
        bullets = []

    for line in lines:
        s = line.strip()
        if not s:
            continue

        if s.startswith("### ") or s.startswith("#### "):
            flush()
            current_company = s.lstrip("#").strip()
            continue

        if s.startswith("* "):
            bullet = s[2:].strip().replace("**", "")
            url_match = url_pattern.search(bullet)
            url = url_match.group(1) if url_match else None
            bullet_clean = url_pattern.sub("", bullet).strip()
            bullet_clean = re.sub(r"\s*—\s*$", "", bullet_clean).strip()
            bullets.append((bullet_clean, url))
            continue

    flush()
    return "\n".join(output)