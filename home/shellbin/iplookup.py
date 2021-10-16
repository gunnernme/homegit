import requests
import sys


def get_info(address) :
  proto = 'http'
  apiserver = 'api.ipstack.com'
  access_key = '60e5fd796be39a1cd777fa662f131018'
  apiurl = "{}://{}/{}?access_key={}".format(proto, apiserver, address, access_key)

  response = requests.get(apiurl)
  out = response.json()

  continent_name = out['continent_name']
  country_name = out['country_name']
  region_name = out['region_name']
  city = out['city']
  latitude = str(out['latitude'])
  longitude = str(out['longitude'])

  if city == region_name:
    loc = "{}, {}".format(city, country_name)
  else:
    loc = "{}, {}/{}".format(city, region_name, country_name)

  print("{}: {} ({}, {})".format(continent_name, loc, latitude[0:6], longitude[0:6]))



def main():
  get_info(sys.argv[1])


main()
