import os
import sys
import smtplib
from email.mime.text import MIMEText

def running_in_docker():
    """
    Check if code is running in a Docker container.
    Docker creates /.dockerenv file.
    """
    return os.path.exists("/.dockerenv")

def get_smtp_config(host=None, port=None):
    """
    Determine SMTP host and port.
    Defaults:
    - Docker → MailHog
    - Local → localhost
    """
    default_host = "mailhog" if running_in_docker() else "localhost"
    return (
        host or default_host,
        port or 1025
    )

def send_email(subject, html, to, host=None, port=None):
    """
    Send email using local SMTP (MailHog or localhost).
    Host/port can be overridden for testing.
    """
    smtp_host, smtp_port = get_smtp_config(host, port)

    msg = MIMEText(html, "html")
    msg["Subject"] = subject
    msg["From"] = os.getenv("LOCAL_EMAIL_SENDER_ADDRESS")
    msg["To"] = ", ".join(to)

    smtp = smtplib.SMTP(smtp_host, smtp_port)
    smtp.sendmail(msg["From"], to, msg.as_string())
    smtp.quit()

if __name__ == "__main__":
    subject = sys.argv[1]
    html = sys.argv[2]
    to = [sys.argv[3]]

    host, port = get_smtp_config()

    print(f"Running in Docker: {running_in_docker()}")
    print(f"SMTP host: {host}, port: {port}")

    send_email(subject, html, to)
    print("Email sent via MailHog/local SMTP")
