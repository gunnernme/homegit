import sys
import requests
import pprint
from urllib.request import urlopen
import json
from haversine import haversine, Unit
import zipcodes
from datetime import datetime,timedelta

days_in_future = 120

if sys.argv[1]:
    days_in_future = int(sys.argv[1])

start_time = datetime.now()
start_time.replace(microsecond=0)
end_time = start_time + timedelta(days=days_in_future)

start_day_fmt = start_time.strftime("%Y-%m-%d")
end_day_fmt = end_time.strftime("%Y-%m-%d")

start_time_fmt = start_time.strftime("T%H:%M")
end_time_fmt = end_time.strftime("T%H:%M")

#locations_start_fmt = start_day_fmt
locations_end_fmt = end_day_fmt

slots_start_fmt = start_day_fmt + start_time_fmt
slots_end_fmt = end_day_fmt + end_time_fmt

scheduler_api_url = "https://ttp.cbp.dhs.gov/schedulerapi"
scheduler_api_endpoints = {
        'locations' : "/slots/locations",
        'locationids' : "/slots/locationids",
        'sites' : "/sites",
        'aslocations' : "/slots/asLocations",
        'location': "/locations"
        }
asloc_api_url_params = "?limit=200"
slots_api_url_params = "?minimum=1&filterTimestampBy=before&timestamp={timestamp}&serviceName=Global%20Entry".format(timestamp=locations_end_fmt)

api_url = scheduler_api_url + scheduler_api_endpoints['aslocations'] + asloc_api_url_params
api_url = scheduler_api_url + scheduler_api_endpoints['aslocations'] + slots_api_url_params
print(api_url)

nextslot_url = scheduler_api_url + scheduler_api_endpoints['location'] + "/{id}/slots" + "?startTimestamp={start}" + "&endTimestamp={end}"

#with urlopen(api_url) as resp:
        #for item in resp:
            #pprint.PrettyPrinter(indent=4).pprint(item)
            #itemd = { 'id': item['id'], 'city': item['city'], state: item['state'] }
            #arr.push(itemd)

peabodyzip = '01960'
peabodylat = (zipcodes.matching(peabodyzip)[0]['lat'])
peabodylong = (zipcodes.matching(peabodyzip)[0]['long'])
peabodygeo = (float(peabodylat), float(peabodylong))


out = requests.get(api_url).json()
print("There are {ct} locations returned".format(ct=len(out)))

newarr = []
for item in out:
    # pprint.PrettyPrinter(indent=4).pprint(item)
    if item['countryCode'] == 'US':
        newitem = item
        zip = item['postalCode'][0:5]
        test = zipcodes.matching(zip)
        if test:
            newitem['lat'] = test[0]['lat']
            newitem['long'] = test[0]['long']
            newitem['geo'] = (float(item['lat']), float(newitem['long']))
            newitem['dist'] = int(haversine(item['geo'], peabodygeo, unit=Unit.MILES))
            newarr.append(newitem)

sout = sorted(newarr, key=lambda item: (item['dist']))

#for item in sout:
for item in sout[0:10]:
    url = nextslot_url.format(id=item['id'], start=slots_start_fmt, end=slots_end_fmt)
    item['slots'] = []
    slots = requests.get(url).json()
    if slots:
        item['slots'].append(slots[0]['timestamp'])
        item['slotslen'] = len(slots)
    else:
        item['slots'].append("none")
        item['slotslen'] = 0
    print("{city}, {state} - {dist} mi: {zip} '{name}' ({id}) = [{slotct}, next={slot}]".format(
        city=item['city'], state=item['state'], dist=item['dist'], zip=item['postalCode'], name=item['name'].strip(), id=item['id'], slotct=item['slotslen'], slot=item['slots']))



