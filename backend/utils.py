import urllib.parse
from datetime import datetime, timedelta

def generate_expedia_url(location: str):
    check_in = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    check_out = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
    loc_enc = urllib.parse.quote(location)
    return f"https://www.expedia.co.id/Hotel-Search?destination={loc_enc}&startDate={check_in}&endDate={check_out}&adults=2&language=id_ID"