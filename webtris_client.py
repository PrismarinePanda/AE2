import requests

class TrafficObservation:
    #site name, date, time period ending, avg speed, total vehicle count
    def __init__(self, name: str, date: str, time_period_ending:str, avg_mph: float | None, total_volume:int |None) -> None:
        self.name = name
        self.date = date
        self.time_period_ending=time_period_ending
        self.avg_mph=avg_mph
        self.total_volume=total_volume

    def is_valid(self)->bool:
        return self.avg_mph is not None and self.total_volume is not None
    
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
        print(f"DEBUG: Received Response with Status {response.status_code}")
        
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

    def fetch_data(self, api_client: WebtrisAPI, date: str) -> None:
        self.observations = api_client.ResponseParser(self.site_id, date)
        self.observations.sort() #sorts based on date because that's how the __lt__ is defined :D

    def get_total_volume(self) -> int:  
        total = 0
        for obs in self.observations:
            if obs.is_valid() and obs.total_volume is not None:
                total += obs.total_volume
        return total

    def get_average_speed(self) -> float:
        total_speed = 0.0
        count = 0

        for obs in self.observations:
            if obs.is_valid() and obs.avg_mph is not None:
                total_speed += obs.avg_mph
                count += 1

        if count == 0:
            return 0.0
            
        return total_speed / count
    
    def get_peak_hour(self) -> str:
        valid_hours = {}
        max_vol = -1
        peak_hour = "00"

        #builds a dictornary lumping each 15 min inverval into hours so we can find the volume per hour rather than per 15 mins
        for obs in self.observations:
            if obs.is_valid() and obs.total_volume is not None:
                hour = obs.time_period_ending.split(':')[0]
                
                if hour in valid_hours:
                    valid_hours[hour] += obs.total_volume
                else:
                    valid_hours[hour] = obs.total_volume
        
        #find the max
        for hr, vol in valid_hours.items():
            if vol > max_vol:
                max_vol = vol
                peak_hour = hr

        return f"{peak_hour}:00"
    
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