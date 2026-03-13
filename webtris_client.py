import requests

# Make a GET request
response = requests.get('https://webtris.nationalhighways.co.uk/api/v1.0/reports/daily?sites=461&start_date=19102025&end_date=19102025&page=1&page_size=500')

# Check if successful
print(response.status_code)  # 200

# Parse JSON into Python 
data = response.json()

class TrafficObservation:
    #site name, date, time period ending, avg speed, total vehicle count
    def __init__(self, site_name, date, time_period_ending, avg_speed, total_vehicle_count) -> None:
        self.site_name = site_name
        self.date = date
        self.time_period_ending=time_period_ending
        self.avg_speed=avg_speed
        self.total_vehicle_count=total_vehicle_count
