from unittest.mock import patch, MagicMock
from airflow.etl.extract import extract
from airflow.etl_test.utils import get_today_str

today_str = get_today_str()
api_url = "https://api.open-meteo.com/v1/forecast?latitude=44.50&longitude=11.34&hourly=temperature_2m,precipitation"

def test_extract_success():
    """
    Test that extract() returns the JSON provided by the mocked API response.
    """

    # Mock API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "hourly": {
            "time" : [f"{today_str}T00:00"],
            "temperature_2m": [20],
            "precipitation": [0.1]
        }
    }
    mock_response.raise_for_status.return_value = None

    # Patch requests.get so no real HTTP call is made
    with patch("requests.get", return_value=mock_response) as mock_get:
        data = extract(today_str, api_url)

        # Verify the API was called once
        mock_get.assert_called_once()

        # Verify the JSON returned is the mocked one
        assert data["hourly"]["time"][0] == f"{today_str}T00:00"
        assert data["hourly"]["temperature_2m"][0] == 20
        assert data["hourly"]["precipitation"][0] == 0.1

def test_extract_http_error():
    """
    Test that extract() raises an exception when the API returns an HTTP error.
    """

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("HTTP 500")

    with patch("requests.get", return_value=mock_response):
        try:
            extract(today_str, api_url)
            assert False, "Expected exception was not raised"
        except Exception as e:
            assert "HTTP 500" in str(e)
