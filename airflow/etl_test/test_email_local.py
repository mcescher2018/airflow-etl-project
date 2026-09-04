from unittest.mock import patch, MagicMock
from airflow.etl.email_local import send_email

def test_email_local_success():
    """
        Test that send_email() calls smtplib.SMTP correctly and sends the message.
    """

    mock_smtp_instance = MagicMock()

    with patch("smtplib.SMTP", return_value=mock_smtp_instance) as mock_smtp_class:
        send_email(
            subject="Test Subject",
            html="<p>Hello</p>",
            to=["test@example.com"],
            host="testhost",
            port=9999
        )

        # Call to smtp = smtplib.SMTP
        mock_smtp_class.assert_called_once_with("testhost", 9999)
        # Call to smtp.sendmail()
        mock_smtp_instance.sendmail.assert_called_once()
        # Call to smtp.quit()
        mock_smtp_instance.quit.assert_called_once()

def test_email_local_multiple_recipients():
    """
    Test that send_email() handles multiple recipients correctly.
    """

    mock_smtp_instance = MagicMock()

    with patch("smtplib.SMTP", return_value=mock_smtp_instance):
        send_email(
            subject="Test Subject",
            html="<p>Hello</p>",
            to=["a@example.com", "b@example.com"],
            host="testhost",
            port=9999
        )

        # Extract the arguments passed to smtp.sendmail()
        # Check if recipient list is correct
        args, kwargs = mock_smtp_instance.sendmail.call_args
        assert args[1] == ["a@example.com", "b@example.com"]