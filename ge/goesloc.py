import sys
import re
import json
import requests
import zipcodes
from haversine import haversine, Unit
from datetime import datetime,timedelta
import config
from pprint import PrettyPrinter, pprint

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def name(loc):
    string = ""
    if isinstance(loc, list):
        for item in loc:
            if string != "":
                string += ","
            string += "name={locname}".format(locname=item['name'])
    else:
        string = loc['name']

    return string

class Goesloc:
    def __init__(self):
        self.goesdict = []
        self.startzip = '01960'
        self.max_asloc = config.max_asloc

        try:
            startlat = (zipcodes.matching(self.startzip)[0]['lat'])
            startlong = (zipcodes.matching(self.startzip)[0]['long'])
        except IndexError:
            eprint("Bad zipcode")
            exit(1)
        self.startgeo = (float(startlat), float(startlong))
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

        if len(out) >= int(self.max_asloc):
            eprint("There are {ct} locations returned".format(ct=len(out)))

        for item in out:
            if item['countryCode'] == 'US' and item['postalCode']:
                zip = item['postalCode'][0:5]
                test = zipcodes.matching(zip)
                if test:
                    item['lat'] = test[0]['lat']
                    item['long'] = test[0]['long']
                    item['geo'] = (float(item['lat']), float(item['long']))
                    item['dist'] = int(haversine(item['geo'], self.startgeo, unit=Unit.MILES))

                #self.goesdict[str(item['id'])] = item
                self.goesdict.append(item)

        self.locations_returned = len(out)
        self.locations_with_zip = len(self.goesdict)
        eprint("Fill returns {all_loc} with {zip_loc} in USA".format(all_loc = self.locations_returned, zip_loc = self.locations_with_zip))


    def search_location(self, key):
        location = self.find_or_add_location(key)
        return location

    def regex_find(self, pat):
        return self.regex_find_by_field(name=pat)

    def regex_find_by_field(self, **kwargs):
        arr = []
        result = []

        for type in kwargs:
            value = kwargs[type]
            #eprint("Type " + type + " value " + value)
            arr.append((type, value))

        (type, value) = arr[0]

        reg = re.compile(value)
        #eprint("Type " + type + " value " + value)
        for i in self.goesdict:
            if reg.match(i[type]):
                result.append(i)

        return result

    def find_by_field(self, **kwargs):
        arr = []
        result = []

        for type in kwargs:
            value = kwargs[type]
            #eprint("Type " + type + " value " + value)
            arr.append((type, value))

        (type, value) = arr[0]

        #eprint("Type " + type + " value " + value)
        for i in self.goesdict:
            if str(i[type]) == str(value):
                result.append(i)

        return result



    def find_or_add_location(self, key):
        location = None
        skey = str(key)
        if skey.isnumeric():
            arr = self.find_by_field(id=skey)
        elif skey.find("*") or skey.find("?"):
            arr = self.regex_find(skey)
        else:
            arr = self.find_by_field(name=skey)
        #self.udump(arr)
        return arr
        if arr:
            location = arr[0]

        return location


    def dump(self):
        pp = PrettyPrinter(indent=4)
        pp.pprint(self.goesdict)

    def udump(self, object):
        pp = PrettyPrinter(indent=4)
        pp.pprint(object)

# ---------------
x = Goesloc()

#loc = x.search_location('5003')
#print("name={name}".format(name=name(loc)))
#x.udump(loc)
#loc = x.search_location('.*erb.*')
#print("name={name}".format(name=name(loc)))
#x.udump(loc)
#loc = x.search_location('.*radley.*port.*')
#print("name={name}".format(name=name(loc)))
#x.udump(loc)
loc = x.search_location('.*radley.*')
print(name(loc))
x.udump(loc)
#loc = x.search_location('88888')
#if loc is not None:
    #x.udump(loc)
#else:
    #print("not foudn")
