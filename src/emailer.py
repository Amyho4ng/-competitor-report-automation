import smtplib
import os
from email.mime.text import MIMEText

def send_email(html_body, recipients, start, end):
    sender = os.getenv("EMAIL_USERNAME")
    password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEText(html_body, "html")
    msg["Subject"] = f"Bi-Weekly Competitor Report — {start} to {end}"
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)