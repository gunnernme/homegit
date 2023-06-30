import sys
import requests
import pprint
from urllib.request import urlopen
import json
from haversine import haversine, Unit
import zipcodes
from datetime import datetime,timedelta
import config

days_in_future = config.days_in_future
start_zip = config.start_zip

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if len(sys.argv) > 1:
    days_in_future = int(sys.argv[1])

if len(sys.argv) > 2:
    start_zip = sys.argv[2]

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
asloc_api_url_params = "?limit=" + str(config.max_asloc)
slots_api_url_params = "?minimum=1&filterTimestampBy=before&timestamp={timestamp}&serviceName=Global%20Entry".format(timestamp=locations_end_fmt)

api_url = scheduler_api_url + scheduler_api_endpoints['aslocations'] + asloc_api_url_params
#api_url = scheduler_api_url + scheduler_api_endpoints['aslocations'] + slots_api_url_params
#print(api_url)
api_url = scheduler_api_url + scheduler_api_endpoints['location'] + "/"
print(api_url)

nextslot_url = scheduler_api_url + scheduler_api_endpoints['location'] + "/{id}/slots" + "?startTimestamp={start}" + "&endTimestamp={end}"
printer = pprint.PrettyPrinter(indent=4)
prt = printer.pprint

#with urlopen(api_url) as resp:
        #for item in resp:
            #pprint.PrettyPrinter(indent=4).pprint(item)
            #itemd = { 'id': item['id'], 'city': item['city'], state: item['state'] }
            #arr.push(itemd)

try:
    startlat = (zipcodes.matching(start_zip)[0]['lat'])
    startlong = (zipcodes.matching(start_zip)[0]['long'])
except IndexError:
    eprint("Bad zipcode")
    exit(1)

startgeo = (float(startlat), float(startlong))


#print(api_url)
result = requests.get(api_url)

try:
    out = result.json()
except ValueError:
    eprint("Bad response to http request GET: '{url}'".format(url=api_url))
    exit(1)

if len(out) >= int(config.max_asloc):
    print("There are {ct} locations returned".format(ct=len(out)))

newarr = []
for item in out:
    # prt(item)
    if item['countryCode'] == 'US' and item['postalCode']:
        newitem = item
        zip = item['postalCode'][0:5]
        test = zipcodes.matching(zip)
        if test:
            newitem['lat'] = test[0]['lat']
            newitem['long'] = test[0]['long']
            newitem['geo'] = (float(newitem['lat']), float(newitem['long']))
            newitem['dist'] = int(haversine(item['geo'], startgeo, unit=Unit.MILES))
            newarr.append(newitem)

sout = sorted(newarr, key=lambda item: (item['dist']))

#for item in sout:
print("Before {}:".format(end_time.strftime(end_day_fmt)))
out_cnt = 0

for item in sout:
    if item['dist'] > config.max_miles:
        exit(0)

    pending = 0
    remote = 0
    url = nextslot_url.format(id=item['id'], start=slots_start_fmt, end=slots_end_fmt)
    item['slots'] = []
    item['slotslen'] = 0
    #print(url)
    slots = requests.get(url).json()
    if slots:
        slots = sorted(slots, key=lambda i: (i['timestamp']))
        pending = 0
        remote = 0
        for ts in slots:
            if str(ts['active']) != str(0):
                for i in range(ts['active']):
                    item['slots'].append(ts['timestamp'])
                    item['slotslen'] = item['slotslen'] + 1
            if str(ts['pending']).lower() != str(0):
                pending = pending + 1
            if str(ts['remote']).lower() != 'false':
                remote = remote + 1
        item['lastslot'] = slots[len(slots)-1]['timestamp']
    else:
        item['slotslen'] = 0
        continue

    if (item['slotslen'] == 0):
        item['slots'].append("none")
    else:
        item['slots'] = item['slots'][0:config.max_slots]

    out_cnt = out_cnt + 1

    print("The {id}-{name} in {city}, {state} is {dist} miles away from {startzip}.  It has {slotslen} available at this time.".format(name=item['name'], dist=item['dist'], city=item['city'], state=item['state'], startzip=config.start_zip, id=item['id'], slotslen=item['slotslen']))
    if pending:
        print("There were {pen} pending slots".format(pen = pending))
    if remote:
        print("There were {rem} remote slots".format(rem = remote))
    if item['slotslen'] == 0:
        print("\tnone\t\t{lastslot}".format(slotcount=item['slotslen'], lastslot=item['lastslot']) )
    else:
        for i in range(0,len(item['slots'])):
            print("\t{openslot}".format(openslot=item['slots'][i]))
        print("\t\t\t{lastslot}".format(lastslot=item['lastslot']) )


    if out_cnt > config.max_out:
        exit(0)



