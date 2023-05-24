import requests
import pprint
from urllib.request import urlopen
import json

scheduler_api_url = "https://ttp.cbp.dhs.gov/schedulerapi"
scheduler_api_endpoints = {
        'locations' : "/slots/locations",
        'locationids' : "/slots/locationids",
        'sites' : "/sites",
        'aslocations' : "/slots/asLocations",
        'location': "/locations"
        }

api_url = scheduler_api_url + scheduler_api_endpoints['aslocations'] + "?limit=100"
print(api_url)

#response = requests.get(api_url)

#out = response.json()

#pprint.PrettyPrinter(indent=4).pprint(out)

with urlopen(api_url) as resp:
    pprint.PrettyPrinter(indent=4).pprint(json.load(resp))

api_url = scheduler_api_url + scheduler_api_endpoints['location'] + "/5444"  + "/slots"
print(api_url)
with urlopen(api_url) as resp:
    pprint.PrettyPrinter(indent=4).pprint(json.load(resp))
