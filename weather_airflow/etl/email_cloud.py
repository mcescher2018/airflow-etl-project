import os
import sys
import requests

def send_email(subject, html, to):
    """
    Send email using API, based on MalGun.
    Change if necessary depending on provider, for example:
    - Postmark: use headers {"X-Postmark-Server-Token": EMAIL_API_KEY}
    - Mailjet: use auth=(API_KEY, SECRET_KEY)
    - SES API: use AWS Signature headers
    """

    EMAIL_ENDPOINT = os.getenv("CLOUD_EMAIL_ENDPOINT")
    EMAIL_API_KEY = os.getenv("CLOUD_EMAIL_API_KEY")
    EMAIL_SENDER = os.getenv("CLOUD_EMAIL_SENDER_ADDRESS")

    print("Sending email with the following settings:")
    print("- Endpoint:", EMAIL_ENDPOINT)
    print("- API key starts with:", EMAIL_API_KEY[:5])
    print("- Sender:", EMAIL_SENDER)

    response = requests.post(
        EMAIL_ENDPOINT,
        auth=("api", EMAIL_API_KEY),
        data={
            "from": EMAIL_SENDER,
            "to": to,
            "subject": subject,
            "html": html
        }
    )

    # Raise error if not 200/202
    response.raise_for_status()
    return response

if __name__ == "__main__":
    """
    Standalone debug mode:
    Run: python email_production.py "Subject" "<p>Hello</p>" "recipient@example.com"
    Requires endpoint, sender and api_key .env
    """
    subject = sys.argv[1]
    html = sys.argv[2]
    to = sys.argv[3]

    send_email(subject, html, to)
    print("Email sent.")