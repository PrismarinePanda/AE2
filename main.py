from webtris_client import WebtrisAPI
from webtris_client import Site

api = WebtrisAPI()

if __name__ == "__main__":
    # 1. Setup
    api = WebtrisAPI()
    my_site = Site(461, "A417 Northbound")
    
    # 2. Action
    # Use a past date that definitely has data
    my_site.fetch_data(api, "15052024") 
    
    # 3. Report
    if my_site.observations:
        print(my_site)
    else:
        print("Error: No data retrieved. Check Site ID or Date.")