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


out = requests.get(api_url).json()

#pprint.PrettyPrinter(indent=4).pprint(out)

#arr=[]
#with urlopen(api_url) as resp:
        #for item in resp:
            #pprint.PrettyPrinter(indent=4).pprint(item)
            #itemd = { 'id': item['id'], 'city': item['city'], state: item['state'] }
            #arr.push(itemd)
    #pprint.PrettyPrinter(indent=4).pprint(json.load(resp))
for loc in out:
    print("{}, {}: {} ({})".format(
        loc['city'], loc['state'], loc['postalCode'], loc['name'].strip(), loc['id']))
#pprint.PrettyPrinter(indent=4).pprint(json.load(arr))

#api_url = scheduler_api_url + scheduler_api_endpoints['location'] + "/5444"  + "/slots"
#print(api_url)
#with urlopen(api_url) as resp:
    #pprint.PrettyPrinter(indent=4).pprint(json.load(resp))
