from webtris_client import WebtrisAPI, Site

def main() -> None: 
    """Runs a traffic analysis by taking user input, fetching the requested data from the actual API, and displaying a report"""
    api_client = WebtrisAPI()
    
    print("--- Traffic Analysis Tool ---")
    print("Press [Enter] to use defaults (Site 461, Date 24/03/2025)")
    
    user_site: str = input("Enter Site ID: ")
    site_id = int(user_site) if user_site else 461
    
    user_date: str = input("Enter Date (DDMMYYYY): ")
    target_date = user_date if user_date else "24032025"
    
    my_site = Site(site_id, "Test Site")
    
    try:
        print(f"\nAnalyzing Site {site_id} for {target_date}...")
        my_site.fetch_data(api_client, target_date)
        
        if len(my_site) == 0:
            print("No data found. Try a different date!")
        else:
            print(my_site)
            
    except Exception as e: #storing the exception as e so we can then print it
        print(f"Connection error: {e}")

if __name__ == "__main__":
    main()