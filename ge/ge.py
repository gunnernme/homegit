import requests
import pprint
from urllib.request import urlopen
import json

api_url = "https://ttp.cbp.dhs.gov/schedulerapi/slots"

response = requests.get(api_url)

out = response.json()

pprint.PrettyPrinter(indent=4).pprint(out)

with urlopen(api_url) as resp:
    pprint.PrettyPrinter(indent=4).pprint(json.load(resp))
