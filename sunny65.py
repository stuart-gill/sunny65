# thinking about data transformations:
# 0: initial input-- time and temp range
# 1: filter destinations by distance, first using SQL call to compute distance using Lat/Long
# 2: futher filter by checking actual drive time distance of desintaions within acceptable range using gmaps distance matrix
# 2: further filter destinations by temperature range
# 3: output destinations, weather + distance data

# TODO: convert destinations by index to destinations by ID from database
# TODO: improve map html output. Somehow list drive time? 
# TODO: Add usage of zip code -> destination drive time table-- need to first try database, then send distance matrix requests bundled
# TODO: for every address, do search by zip code, not by address



import urllib.request, urllib.parse, urllib.error
import json
import ssl
import config
import sqlite3
import codecs
from geojson import geocode
from calc_distance import calc_distance
from distance_matrix import distance_matrix
from weather import weather_forecast

conn = sqlite3.connect('sunny65_db.sqlite')
cur = conn.cursor()

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

while True:
    address = input('Enter your location: ') 
    if len(address) < 1: break
    
    # Use google api to get lat long for origin address
    (lat,lng,zipcode)=geocode(address)

    travel = float(input('How long are you willing to travel in hours? '))
    est_miles = travel*40  # super rough guess of how far you could go in an hour
    
    # Get potential destinations filtered by "as the crow flies" distances calculated by sql database
    distance_filtered_locs = calc_distance(lat,lng,est_miles)
    print("distance filtered locs ", distance_filtered_locs)

    campsites = []
    for campsite in distance_filtered_locs:
      new_campsite = {}
      new_campsite['id']= campsite[0]
      new_campsite['name']= campsite[1]
      new_campsite['lat']= campsite[2]
      new_campsite['lng']= campsite[3]
      new_campsite['weather_url']= campsite[5]
      new_campsite['travel_time']= -1
      campsites.append(new_campsite)
    
    
    # use google distance matrix to get actual drive time distances 
    durations = distance_matrix(address, zipcode, distance_filtered_locs)
    # elements = js["rows"][0]["elements"]
    print("durations = ", durations)

    if len(durations) != len(distance_filtered_locs):
      print("durations != locs, retrieval error, quitting", len(durations), len(distance_filtered_locs))
      break

  
    travel_seconds = travel * 3600
    acceptable_indices = []
    user_min = int(input("What's your minimum acceptable temperature? "))
    user_max = int(input("What's your maximum acceptable temperature? "))

    # get list of indexes that pass travel duration test
    for i in range(len(durations)):
      if durations[i] < travel_seconds:
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
      
      lat = str(distance_filtered_locs[i][2])
      lng = str(distance_filtered_locs[i][3])
      weather_url = distance_filtered_locs[i][5]
      ID = distance_filtered_locs[i][0]
      js = weather_forecast(lat,lng, weather_url, ID)
      # print(json.dumps(js, indent=4))

      # Add acceptable weather windows to destinations
      for period in js["properties"]["periods"]:
        if period["isDaytime"]:
          if period["temperature"] > user_min and period["temperature"] < user_max:
            destinations[-1]["weather"].append(period)

    # output acceptable weather windows at acceptable destinations
    # also create map
    fhand = codecs.open('where.js', 'w', "utf-8")
    fhand.write("myData = [\n")
    count = 0
    for destination in destinations:
      if len(destination["weather"]):
        # print(destination)
        lat = destination["lat"]
        lng = destination["lng"]
        name = destination["name"]
        count = count + 1
        if count > 1 : fhand.write(",\n")
        output = "["+str(lat)+","+str(lng)+", '"+name+"']"
        fhand.write(output)
        print('============================= \n')
        print("Destination: ", destination["name"])
        for day in destination["weather"]:
          print("Day: ", day["name"])
          print("Temperature: ", str(day["temperature"]))
          print("Weather: ", day["shortForecast"])
        print('\n')
    fhand.write("\n];\n")
    fhand.close()
    print(count, "records written to where.js")
    print("Open where.html to view the data in a browser")
