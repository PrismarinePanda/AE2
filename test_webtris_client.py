import pytest
from unittest.mock import patch, MagicMock
from webtris_client import TrafficObservation, WebtrisAPI, Site

@pytest.fixture
def mock_obs_list() -> list[TrafficObservation]:
    """Creates a mock list of Traffic Observation objects for testing"""
    return [
        TrafficObservation("Site 999", "3000-03-24", "07:14:00", 60.0, 100), #Normal data
        TrafficObservation("Site 999", "3000-03-24", "08:14:00", None, None), #Missing data
        TrafficObservation("Site 999", "3000-03-24", "17:14:00", 0, 0), #Zero data
    ]

@pytest.fixture
def mock_api_json() -> dict:
    """Creates a mock API response for testing"""
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
def test_validity() -> None:
    """Tests whether the data in a given Traffic Observation Object is valid"""
    normal_data = TrafficObservation("S", "D", "T", 50.0, 100)
    zero_data = TrafficObservation("S", "D", "T", 0, 0)
    missing_data = TrafficObservation("S", "D", "T", None, None)
    malformed_data=TrafficObservation("S", "D", "T", "sdiuh", "djash") #Malformed data
  
    assert normal_data.is_valid() is True
    assert zero_data.is_valid() is True
    assert missing_data.is_valid() is False
    assert malformed_data.is_valid() is False

def test_sorting() -> None:
    """Tests whether Traffic Observation objects are being sorted into the correct order"""
    obs_late = TrafficObservation("S", "D", "23:00:00", 50.0, 10)
    obs_early = TrafficObservation("S", "D", "01:00:00", 70.0, 20)
    
    records = [obs_late, obs_early]
    records.sort()
    
    assert records[0].time_period_ending == "01:00:00"

#TESTS FOR WEBTRIS API
@patch("webtris_client.requests.get")
def test_webtris_api_success(mock_get: MagicMock, mock_api_json: dict) -> None:
    """Tests whether response_parser() correctly parses the JSON structure"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_api_json
    
    api = WebtrisAPI()
    result = api.response_parser(999, "24033000")
    
    assert len(result) == 1
    assert result[0].avg_mph == 65.0  # Check if it converted string "65" to float
    assert result[0].total_volume == 150 # Check if it converted string "150" to int

@patch("webtris_client.requests.get")
def test_api_no_content(mock_get: MagicMock) -> None:
    """Tests how response_parser() handles a 204 status code for no data"""
    mock_get.return_value.status_code = 204
    
    api = WebtrisAPI()
    result = api.response_parser(461, "01012099") 
    
    assert result == []

#TESTS FOR SITE CLASS 
def test_site_total_volume(mock_obs_list: list[TrafficObservation]) -> None:
    """Tests whether the total site volume is correctly calculated even with missing an zero data"""
    my_site = Site(999, "Test Site")
    my_site.observations = mock_obs_list 
    
    # 100 (Normal) + 0 (Zero Data) + None (Ignored) = 100
    assert my_site.get_total_volume() == 100

def test_average_speed_zero_volume() -> None:
    """Tests whether edge case where total volume is zero avoids division by zero"""
    my_site = Site(999, "Empty Road") #only zero data so total volume is 0
    my_site.observations = [
        TrafficObservation("S", "D", "03:00:00", 0.0, 0),
        TrafficObservation("S", "D", "03:15:00", 0.0, 0)
    ]
    assert my_site.get_average_speed() == 0.0

def test_site_peak_hour(mock_obs_list: list[TrafficObservation]) -> None:
    """Tests whether the peak hour function is correctly selecting the hour with the highest volume"""
    my_site = Site(999, "Test Site")
    my_site.observations = mock_obs_list
    
    assert my_site.get_peak_hour() == "07"