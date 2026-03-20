import requests

class TrafficObservation:
    #site name, date, time period ending, avg speed, total vehicle count
    def __init__(self, name: str, date: str, time_period_ending:str, avg_mph: float, total_volume:int) -> None:
        self.name = name
        self.date = date
        self.time_period_ending=time_period_ending
        self.avg_mph=avg_mph
        self.total_volume=total_volume

    def is_valid(self)->bool:
        if(self.name != '' and self.date!='' and self.time_period_ending!='' and self.avg_mph!='' and self.total_volume!=''):
            return True
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
        return cls(
            name=data.get("Site Name", ""),
            date=data.get("Report Date", ""),
            time_period_ending=data.get("Time Period Ending", ""),
            avg_mph=data.get("Avg mph", ""),
            total_volume=data.get("Total Volume", ""),
        )

class WebtrisAPI():
    BASE_URL = "https://webtris.nationalhighways.co.uk/api/v1.0"

    def ResponseParser(self):
        response = requests.get(self.BASE_URL, timeout=10)
        data = response.json()
        return [
            TrafficObservation.from_dict(i)
            for i in data.get("results", [])
            if i.get("wrapperType") == "trafficobservation"
        ]

#class Parser():
#class Site():
