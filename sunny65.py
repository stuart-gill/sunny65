# thinking about data transformations:
# 0: initial input-- time and temp range
# 1: filter destinations by distance, first using SQL call to compute distance using Lat/Long
# 2: futher filter by checking actual drive time distance of desintaions within acceptable range using gmaps distance matrix
# 2: further filter destinations by temperature range
# 3: output destinations, weather + distance data

# TODO: make weather api its own file and function. Input: lat, long. Output: list of weather dictionaries for that location
# TODO: store weather forecast urls in location table in database
# TODO: convert destinations by index to destinations by ID from database

import urllib.request, urllib.parse, urllib.error
import json
import ssl
import config
import sqlite3
from geojson import geocode
from calc_distance import calc_distance
from distance_matrix import distance_matrix

conn = sqlite3.connect('sunny65_db.sqlite')
cur = conn.cursor()

weather_service_url = 'https://api.weather.gov/points/'

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

while True:
    address = input('Enter your location: ') 
    if len(address) < 1: break
    
    # Use google api to get lat long for origin address
    (lat,lng)=geocode(address)

    travel = float(input('How long are you willing to travel in hours? '))
    est_miles = travel*40  # super rough guess of how far you could go in an hour
    
    # Get potential destinations filtered by "as the crow flies" distances calculated by sql database
    distance_filtered_locs = calc_distance(lat,lng,est_miles)
    print(distance_filtered_locs)
    
    # use google distance matrix to get actual drive time distances 
    js = distance_matrix(address, distance_filtered_locs)
    elements = js["rows"][0]["elements"]
  
    travel_seconds = travel * 3600
    acceptable_indices = []
    user_min = int(input("What's your minimum acceptable temperature? "))
    user_max = int(input("What's your maximum acceptable temperature? "))

    # get list of indexes that pass travel duration test
    for i in range(len(elements)):
      if elements[i]["status"] == "OK" and elements[i]["duration"]["value"] < travel_seconds:
        acceptable_indices.append(i)
        

    # print names of acceptable cities ( index in the list of destinations... should convert to IDs when using database)
    print("Destinations within acceptable drive time: ")
    for i in acceptable_indices:
      print(distance_filtered_locs[i][1])

    destinations = []
    # GET WEATHER FROM WEATHER.GOV 
    for i in acceptable_indices:
      print("ran with i: ", i)
      # Build destinations dictionary
      destinations.append({"id":distance_filtered_locs[i][0], "name":distance_filtered_locs[i][1], "lat":distance_filtered_locs[i][2], "lng":distance_filtered_locs[i][3], "weather":[]})
      
      # Get forecast API URL using lat and long
      # Could push this url to database? Then just use database stored url, and only run this api call again if the database address doesn't work 
      # Could put all this functionality in a separate module
      url = weather_service_url + str(distance_filtered_locs[i][2]) + "," + str(distance_filtered_locs[i][3])# + "/forecast"
      
      try: 
        uh = urllib.request.urlopen(url, context=ctx)
      except urllib.error.URLError as e:
        print("weather.gov request failed for this reason: ", e.reason)
        continue
      data = uh.read().decode()
      print('Retrieved', len(data), 'characters')

      try:
          js = json.loads(data)
      except:
          js = None
      forecast_url = js["properties"]["forecast"]

      # Now, get forcast using URL just retrieved
      try: 
        uh = urllib.request.urlopen(forecast_url, context=ctx)
      except urllib.error.URLError as e:
        print("weather.gov request failed for this reason: ", e.reason)
        continue
      data = uh.read().decode()
      print('Retrieved', len(data), 'characters')

      try:
          js = json.loads(data)
      except:
          js = None


      # print(json.dumps(js, indent=4))

      # Add acceptable weather windows to destinations
      for period in js["properties"]["periods"]:
        if period["isDaytime"]:
          if period["temperature"] > user_min and period["temperature"] < user_max:
            destinations[-1]["weather"].append(period)

    # output acceptable weather windows at acceptable destinations
    for destination in destinations:
      if len(destination["weather"]):
        print('============================= \n')
        print("Destination: ", destination["name"])
        for day in destination["weather"]:
          print("Day: ", day["name"])
          print("Temperature: ", str(day["temperature"]))
          print("Weather: ", day["shortForecast"])
        print('\n')
