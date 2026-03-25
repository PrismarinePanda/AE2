import pytest
from unittest.mock import patch
from webtris_client import TrafficObservation, WebtrisAPI, Site

@pytest.fixture
def mock_obs_list() -> list[TrafficObservation]:
    return [
        TrafficObservation("Site 999", "3000-03-24", "07:14:00", 60.0, 100), #Normal data
        TrafficObservation("Site 999", "3000-03-24", "08:14:00", None, None), #Missing data
        TrafficObservation("Site 999", "3000-03-24", "17:14:00", 0, 0), #Zero data
    ]

@pytest.fixture
def mock_api_json() -> dict:
    return {
        "Rows": [
            {
                "Site Name": "Site 999",
                "Report Date": "3000-03-24T00:00:00",
                "Time Period Ending": "07:14:00",
                "Avg mph": "65",
                "Total Volume": "150"
            }
        ]
    }

#TESTS FOR TRAFFIC OBSERVATION

def test_validity():
    """Requirement: Determine whether a record contains valid data."""
    
    normal_data = TrafficObservation("S", "D", "T", 50.0, 100)
    zero_data = TrafficObservation("S", "D", "T", 0, 0)
    missing_data = TrafficObservation("S", "D", "T", None, None)
    malformed_data=TrafficObservation("S", "D", "T", "sdiuh", "djash") #Malformed data

    
    assert normal_data.is_valid() is True
    assert zero_data.is_valid() is True
    assert missing_data.is_valid() is False
    assert malformed_data.is_valid() is False

def test_sorting():
    obs_late = TrafficObservation("S", "D", "23:00:00", 50.0, 10)
    obs_early = TrafficObservation("S", "D", "01:00:00", 50.0, 10)
    
    records = [obs_late, obs_early]
    records.sort()
    
    assert records[0].time_period_ending == "01:00:00"

#MOCKED TESTS FOR WEBTRIS API
@patch("webtris_client.requests.get")
def test_webtris_api_success(mock_get, mock_api_json):
    """Verifies that the API client correctly parses the JSON structure."""
    # 1. Setup the Mock to 'lie' and say the internet is fine
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_api_json
    
    # 2. Run the code
    api = WebtrisAPI()
    result = api.ResponseParser(999, "24033000")
    
    # 3. Assertions
    assert len(result) == 1
    assert result[0].avg_mph == 65.0  # Check if it converted string "65" to float
    assert result[0].total_volume == 150 # Check if it converted string "150" to int

@patch("webtris_client.requests.get")
def test_api_no_content(mock_get): # Fix: Removed other arguments if not needed
    """Requirement: Handle HTTP 204 'No Content' responses correctly."""
    mock_get.return_value.status_code = 204
    
    api = WebtrisAPI()
    # If your method name is ResponseParser, use that:
    result = api.ResponseParser(461, "01012099") 
    
    assert result == []

#TESTS FOR SITE CLASS 
def test_site_total_volume(mock_obs_list):
    """Checks if Site correctly sums volumes while ignoring invalid data."""
    my_site = Site(999, "Test Site")
    my_site.observations = mock_obs_list  # Manual 'Interchangeability' injection
    
    # Logic: 100 (Normal) + 0 (Zero Data) + None (Ignored) = 100
    assert my_site.get_total_volume() == 100

def test_average_speed_zero_volume():
    """Requirement: Handle edge case where total volume is zero to avoid division by zero."""
    # Setup a site with only "Zero Data"
    my_site = Site(999, "Empty Road")
    my_site.observations = [
        TrafficObservation("S", "D", "03:00:00", 0.0, 0),
        TrafficObservation("S", "D", "03:15:00", 0.0, 0)
    ]
    
    # This should return 0.0 gracefully
    assert my_site.get_average_speed() == 0.0

def test_site_peak_hour(mock_obs_list):
    """Verifies that the peak hour is identified correctly based on volume."""
    my_site = Site(999, "Test Site")
    my_site.observations = mock_obs_list
    
    # In your fixture, 07:14:00 has 100 cars, which is the highest.
    # So the peak hour should be "07"
    assert my_site.get_peak_hour() == "07"