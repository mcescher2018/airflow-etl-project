import pytest
from unittest.mock import patch, MagicMock
from airflow.etl.email_cloud import send_email

def test_email_cloud_success():
    """
    Test that send_email() sends a POST request to the configured email provider endpoint.
    """

    FAKE_ENDPOINT = "https://api.mailgun.net/v3/sandbox12345678.mailgun.org/messages"
    FAKE_API_KEY = "fake_mailgun_api_key"
    FAKE_SENDER = "postmaster@sandbox12345678.mailgun.org"

    mock_post = MagicMock()
    # Mock response.raise_for_status() setting the return value to ok, i.e. None
    mock_post.return_value.raise_for_status.return_value = None

    with patch("os.getenv") as mock_getenv, \
         patch("requests.post", return_value=mock_post) as mock_post_fn:

        # Mock environment variables
        mock_getenv.side_effect = lambda key: {
            "CLOUD_EMAIL_ENDPOINT": FAKE_ENDPOINT,
            "CLOUD_EMAIL_API_KEY": FAKE_API_KEY,
            "CLOUD_EMAIL_SENDER_ADDRESS": FAKE_SENDER
        }.get(key)

        send_email(
            subject="Test Subject",
            html="<p>Hello</p>",
            to="test@example.com"
        )

        # Verify POST was called once
        mock_post_fn.assert_called_once()

        # Verify correct URL
        assert mock_post_fn.call_args[0][0] == FAKE_ENDPOINT

        # Verify payload fields
        data_sent = mock_post_fn.call_args[1]["data"]
        assert data_sent["from"] == FAKE_SENDER
        assert data_sent["to"] == "test@example.com"
        assert data_sent["subject"] == "Test Subject"
        assert data_sent["html"] == "<p>Hello</p>"

def test_email_cloud_http_error():
    FAKE_ENDPOINT = "https://api.mailgun.net/v3/sandbox12345678.mailgun.org/messages"
    FAKE_API_KEY = "fake_mailgun_api_key"
    FAKE_SENDER = "postmaster@sandbox12345678.mailgun.org"

    mock_post = MagicMock()
    mock_post.raise_for_status.side_effect = Exception("Provider error")

    with patch("os.getenv") as mock_getenv, \
         patch("requests.post", return_value=mock_post) as mock_post_fn:

        mock_getenv.side_effect = lambda key: {
            "CLOUD_EMAIL_ENDPOINT": FAKE_ENDPOINT,
            "CLOUD_EMAIL_API_KEY": FAKE_API_KEY,
            "CLOUD_EMAIL_SENDER_ADDRESS": FAKE_SENDER
        }.get(key)

        # Expect the exception
        with pytest.raises(Exception, match="Provider error"):
            send_email(
                subject="Test Subject",
                html="<p>Hello</p>",
                to="test@example.com"
            )

        # Verify the POST was actually called
        mock_post_fn.assert_called_once()
        # Verify raise_for_status was called
        mock_post.raise_for_status.assert_called_once()
