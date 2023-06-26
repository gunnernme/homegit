import sys
import json
import requests
import zipcodes
import haversine
from datetime import datetime,timedelta
import config

class Goesloc:
    def __init__(self):
        self.goesdict = {}
        self.fill_locations(self.goesdict)

    def fill_locations(self, goesdict):
        scheduler_api_url = "https://ttp.cbp.dhs.gov/schedulerapi"
        api_url = scheduler_api_url + '/locations' + "/"
        result = requests.get(api_url)

        try:
            out = result.json()
        except ValueError:
            eprint("Bad response to http request GET: '{url}'".format(url=api_url))
            exit(1)

        if len(out) >= int(config.max_asloc):
            print("There are {ct} locations returned".format(ct=len(out)))

        for item in out:
            key = item['id']
            if item['countryCode'] == 'US' and item['postalCode']:
                zip = item['postalCode'][0:5]
                test = zipcodes.matching(zip)
                if test:
                    item['lat'] = test[0]['lat']
                    item['long'] = test[0]['long']
                    item['geo'] = (float(item['lat']), float(item['long']))
                    #item['dist'] = int(haversine(item['geo'], startgeo, unit=Unit.MILES))
            self.goesdict[key] = item

    def search_location(self, key):
        location = self.find_or_add_location(key)
        return location

    def find_or_add_location(self, key):
        if key.isnumeric():
            location = getlocation(id=key)
        elif key.find("*") or key.find("?"):
            location = getlocation(pat=key)
        else:
            location = getlocation(name=key)

    def getlocation(self, key):
        return self.goesdict[key]

    def dump(self):
        print(self.goesdict)

# ---------------
x = Goesloc()

x.dump()
