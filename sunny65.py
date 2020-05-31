# thinking about data transformations:
# 0: initial input-- time and temp range
# 1: filter destinations by distance (one or two steps? What to do as # of destinations gets large)
# 2: further filter destinations by temperature range
# 3: output destinations, weather + distance data


import urllib.request, urllib.parse, urllib.error
import json
import ssl
import config

api_key = config.GMAPS_API_KEY

serviceurl = 'https://maps.googleapis.com/maps/api/distancematrix/json?'

weather_service_url = 'https://api.weather.gov/points/'

# destinations = [
#   'Yakima, WA',
#   'Tacoma, WA',
#   'Bellingham, WA',
#   'Leavenworth, WA',
#   'Portland, OR',
#   'Lopez Island, WA',
#   'Bend, OR'
# ]

# destinations_parm = ''
# for destination in destinations:
#   destinations_parm += destination + '|'

# Read JSON to build destinations parameter, as opposed to hard coded array above 
# Should be able to extend this to reading from a database
str_data = open('sunny65.json').read()
destinations = json.loads(str_data)

destinations_parm = ''
for loc in destinations:
  destinations_parm += str(loc["lat"]) + "," + str(loc["lng"]) + '|'


# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

while True:
    address = input('Enter your location: ')
    if len(address) < 1: break

    parms = dict()
    parms['origins'] = address
    parms['destinations']= destinations_parm
    if api_key is not False: parms['key'] = api_key
    url = serviceurl + urllib.parse.urlencode(parms)

    # GET LOCATIONS FROM DISTANCE MATRIX
    print('Retrieving', url)
    uh = urllib.request.urlopen(url, context=ctx)
    data = uh.read().decode()
    print('Retrieved', len(data), 'characters')

    try:
        js = json.loads(data)
    except:
        js = None

    if not js or 'status' not in js or js['status'] != 'OK':
        print('==== Failure To Retrieve ====')
        print(data)
        continue

    # print(json.dumps(js, indent=4))

    travel = float(input('How long are you willing to travel in hours? '))
    travel_seconds = travel * 3600
    acceptable_results = []

    user_min = int(input("What's your minimum acceptable temperature? "))
    user_max = int(input("What's your maximum acceptable temperature? "))

    elements = js["rows"][0]["elements"]

    for i in range(len(elements)):
      if elements[i]["duration"]["value"] < travel_seconds:
        acceptable_results.append(i)

    # print names of acceptable cities ('result' is the index in the list of destinations... should convert to IDs when using database)
    for result in acceptable_results:
      print(destinations[result]["name"])


    # GET WEATHER FROM WEATHER.GOV 
    for result in acceptable_results:
      url = weather_service_url + str(destinations[result]["lat"]) + "," + str(destinations[result]["lng"]) + "/forecast"
      print('Retrieving', url)
      uh = urllib.request.urlopen(url, context=ctx)
      data = uh.read().decode()
      print('Retrieved', len(data), 'characters')

      try:
          js = json.loads(data)
      except:
          js = None

      # Add weather key
      destinations[result]["weather"]= []
      for period in js["properties"]["periods"]:
        if period["isDaytime"]:
          if period["temperature"] > user_min and period["temperature"] < user_max:
            destinations[result]["weather"].append(period)

    for result in acceptable_results:
      if len(destinations[result]["weather"]):
        print("Destination: ", destinations[result]["name"])
        for day in destinations[result]["weather"]:
          print("Day: ", day["name"])
          print("Temperature: ", str(day["temperature"]))
          print("Weather: ", day["shortForecast"])

      


    # url = weather_service_url + str(destinations[0]["lat"]) + "," + str(destinations[0]["lng"]) + "/forecast"

    # print('Retrieving', url)
    # uh = urllib.request.urlopen(url, context=ctx)
    # data = uh.read().decode()
    # print('Retrieved', len(data), 'characters')

    # try:
    #     js = json.loads(data)
    # except:
    #     js = None

    # if not js or 'status' not in js or js['status'] != 'OK':
    #     print('==== Failure To Retrieve ====')
    #     print(data)
    #     continue

    # print(json.dumps(js, indent=4))







    # lat = js['results'][0]['geometry']['location']['lat']
    # lng = js['results'][0]['geometry']['location']['lng']
    # print('lat', lat, 'lng', lng)
    # location = js['results'][0]['formatted_address']
    # placeid = js['results'][0]['place_id']
    # print(location)
    # print("place id: ", placeid)
