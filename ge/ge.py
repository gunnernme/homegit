import requests
import pprint
from urllib.request import urlopen
import json
from haversine import haversine, Unit
import zipcodes
from datetime import datetime,timedelta

start_time = datetime.now()
start_time.replace(microsecond=0)
end_time = start_time + timedelta(days=90)

scheduler_api_url = "https://ttp.cbp.dhs.gov/schedulerapi"
scheduler_api_endpoints = {
        'locations' : "/slots/locations",
        'locationids' : "/slots/locationids",
        'sites' : "/sites",
        'aslocations' : "/slots/asLocations",
        'location': "/locations"
        }
asloc_api_url_params = "?limit=200"
slots_api_url_params = "?minimum=1&filterTimestampBy=before&timestamp={timestamp}&serviceName=Global%20Entry".format(timestamp=end_time.strftime("%Y-%m-%d"))

api_url = scheduler_api_url + scheduler_api_endpoints['aslocations'] + asloc_api_url_params
api_url = scheduler_api_url + scheduler_api_endpoints['aslocations'] + slots_api_url_params
print(api_url)


out = requests.get(api_url).json()
#print("There are {} locations returned".format(len(out)))


#pprint.PrettyPrinter(indent=4).pprint(out)

#arr=[]
#with urlopen(api_url) as resp:
        #for item in resp:
            #pprint.PrettyPrinter(indent=4).pprint(item)
            #itemd = { 'id': item['id'], 'city': item['city'], state: item['state'] }
            #arr.push(itemd)
    #pprint.PrettyPrinter(indent=4).pprint(json.load(resp))

#pprint.PrettyPrinter(indent=4).pprint(out)
peabodyzip = '01960'
peabodylat = (zipcodes.matching(peabodyzip)[0]['lat'])
peabodylong = (zipcodes.matching(peabodyzip)[0]['long'])
peabodygeo = (float(peabodylat), float(peabodylong))

#pprint.PrettyPrinter(indent=4).pprint(peabodylat)


newarr = []
for item in out:
    if item['countryCode'] == 'US':
        newitem = item
        zip = item['postalCode'][0:5]
        #print(zip)
        test = zipcodes.matching(zip)
        if test:
            item['lat'] = test[0]['lat']
            item['long'] = test[0]['long']
            item['geo'] = (float(item['lat']), float(item['long']))
            #print("Adding postalCode: {}/{}/{}".format(item['postalCode'], item['lat'], item['long']))
            newarr.append(newitem)
    #else:
        #print("Ignoring postalCode: {}".format(item['postalCode']))

#pprint.PrettyPrinter(indent=4).pprint(newarr)
sout = sorted(newarr, key=lambda item: (haversine(item['geo'], peabodygeo, unit=Unit.MILES)))
#pprint.PrettyPrinter(indent=4).pprint(sout)

for loc in sout:
    print("{}, {}: {} '{}' ({})".format(
        loc['city'], loc['state'], loc['postalCode'], loc['name'].strip(), loc['id']))

#api_url = scheduler_api_url + scheduler_api_endpoints['location'] + "/5444"  + "/slots"
#print(api_url)
#with urlopen(api_url) as resp:
    #pprint.PrettyPrinter(indent=4).pprint(json.load(resp))
