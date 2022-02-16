import requests
import sys
import json


def get_info(address, arr) :
  proto = 'http'
  apiserver = 'api.ipstack.com'
  access_key = '60e5fd796be39a1cd777fa662f131018'
  apiurl = "{}://{}/{}?access_key={}".format(proto, apiserver, address, access_key)
  #print(apiurl)

  response = requests.get(apiurl)
  out = response.json()
  out['arg'] = address
  arr.append(out)


def print_info(arr):
  for out in arr:   #sorted(arr, key = lambda d: d['ip']):
    if out.get('success', 'missing') != 'missing':
      if not out.get('success'):
        info = out['error']['info']
        print('{}: {}'.format(out['arg'], info))
        continue

    address = out['ip']
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

    print("{}: {}- {} ({}, {})".format(address, continent_name, loc, latitude[0:6], longitude[0:6]))


def main():
  arr = []
  for x in sys.argv[1:]:
    # if x not in list(map(lambda y: y['ip'], arr)):
      get_info(x, arr)

  print_info(arr)


main()
