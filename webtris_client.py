import requests

class TrafficObservation:
    #site name, date, time period ending, avg speed, total vehicle count
    def __init__(self, name: str, date: str, time_period_ending:str, avg_mph: float | None, total_volume:int |None) -> None:
        self.name = name
        self.date = date
        self.time_period_ending=time_period_ending
        self.avg_mph=avg_mph
        self.total_volume=total_volume

    def is_valid(self) -> bool:
        if self.avg_mph is None or self.total_volume is None:
            return False
            
        try:
            float(self.avg_mph) 
            int(self.total_volume)
            return True
        except (ValueError, TypeError):
            return False
    
    def __lt__(self, other):
        if(self.time_period_ending<other.time_period_ending):
            return True
        return False

    def __eq__(self, other):
        if(self.time_period_ending==other.time_period_ending):
            return True
        return False
    
    def __repr__(self) -> str:
        return f"name={self.name}, date={self.date}, time period end={self.time_period_ending}, speed={self.avg_mph}, count={self.total_volume}"

    @classmethod
    def from_dict(cls, data: dict) -> "TrafficObservation":
        raw_mph=data.get("Avg mph", "")
        raw_vol = data.get("Total Volume", "")
        
        return cls(
            name=data.get("Site Name", ""),
            date=data.get("Report Date", ""),
            time_period_ending=data.get("Time Period Ending", ""),
            avg_mph=float(raw_mph) if raw_mph != "" else None ,
            total_volume= int(raw_vol) if raw_vol else None
        )

class WebtrisAPI():
    BASE_URL = "https://webtris.nationalhighways.co.uk/api/v1.0/reports/daily"

    def ResponseParser(self, site_id: int, date_str: str):
        payload = {
            "sites": site_id,
            "start_date": date_str,
            "end_date": date_str,
            "page": 1,
            "page_size": 500
        }
        
        print(f"DEBUG: Contacting API for Site {site_id}...")
        response = requests.get(self.BASE_URL, params=payload, timeout=20)
        #print(f"DEBUG: The full URL being called is: {response.url}")
        print(f"DEBUG: Received Response with Status {response.status_code}")

        if response.status_code == 204:
            print("No data available for this site/date combination.")
            return []  # Return an empty list so the Site class doesn't crash
        
        if response.status_code != 200:
            response.raise_for_status()
            
        data = response.json()
        
        return [
            TrafficObservation.from_dict(i) 
            for i in data.get("Rows", [])
        ]
    
class Site():
    def __init__(self, site_id: int, site_name: str) -> None:
        self.site_id = site_id
        self.site_name = site_name
        self.observations: list[TrafficObservation] = []
    
    def __iter__(self):
        return iter(self.observations)

    def fetch_data(self, api_client: WebtrisAPI, date: str) -> None:
        self.observations = api_client.ResponseParser(self.site_id, date)
        self.observations.sort() #sorts based on date because that's how the __lt__ is defined :D

    def __len__(self) -> int:
        return len(self.observations) #number of records
    
    def get_records_for_hour(self, hour: str) -> list[TrafficObservation]:
        if len(hour) == 1:
            target = "0" + hour
        else:
            target = hour 
        return [obs for obs in self.observations if obs.time_period_ending.startswith(target)]

    def _calculate_total_volume(self, records: list[TrafficObservation]) -> int:
        return sum(obs.total_volume for obs in records if obs.is_valid() and obs.total_volume is not None)
        
    def _calculate_average_speed(self, records: list[TrafficObservation]) -> float:
        valid_speeds = [obs.avg_mph for obs in records if obs.is_valid() and obs.avg_mph is not None]
        if not valid_speeds:
            return 0.0
        return sum(valid_speeds) / len(valid_speeds)
    
    def get_total_volume(self) -> int:
        return self._calculate_total_volume(self.observations)

    def get_total_volume_hour(self, hour: str) -> int:
        hour_records = self.get_records_for_hour(hour)
        return self._calculate_total_volume(hour_records)

    def get_average_speed(self) -> float:
        return self._calculate_average_speed(self.observations)

    def get_average_speed_hour(self, hour: str) -> float:
        hour_records = self.get_records_for_hour(hour)
        return self._calculate_average_speed(hour_records)
    
    def get_peak_hour(self) -> str:
        hourly_totals = {}
        for h in range(24):
            hour_str = str(h)
            if len(hour_str) == 1:
                hour_str = "0" + hour_str
            hourly_totals[hour_str] = self.get_total_volume_hour(hour_str)
        
        max_vol = -1
        peak_hour = "00"
        for hr, vol in hourly_totals.items():
            if vol > max_vol:
                max_vol = vol
                peak_hour = hr
        return peak_hour

    def __str__(self) -> str:
        vol = self.get_total_volume()
        avg = self.get_average_speed()
        peak = self.get_peak_hour()
        
        return (
            f"--- Traffic Report: {self.site_name} (ID: {self.site_id}) ---\n"
            f"Total Vehicle Volume: {vol:,}\n"
            f"Average Speed:        {avg:.2f} mph\n"
            f"Peak Traffic Hour:    {peak}\n"
            f"---------------------------------------------------"
        )