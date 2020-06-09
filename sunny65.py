# thinking about data transformations:
# 0: initial input-- time and temp range
# 1: filter destinations by distance, first using SQL call to compute distance using Lat/Long
# 2: futher filter by checking actual drive time distance of desintaions within acceptable range using gmaps distance matrix
# 2: further filter destinations by temperature range
# 3: output destinations, weather + distance data
# TODO: improve map html output. Somehow list drive time? 

import urllib.request, urllib.parse, urllib.error
import json
import ssl
import config
import sqlite3
import codecs
from geojson import geocode
from distance_matrix import distance_matrix
from weather import weather_forecast
from sunny65_db import get_distance_filtered_locs, get_distance_filtered_locs2


while True:
    address = input('Enter your location zipcode or address: ') 
    if len(address) < 1: break
    
    # Use google api to get lat long for origin address
    (lat,lng,zipcode)=geocode(address)

    travel = float(input('How long are you willing to travel in hours? '))
    est_miles = travel*40  # super rough guess of how far you could go in an hour
    travel_seconds = travel * 3600 
    
    # Get potential destinations filtered by "as the crow flies" distances calculated by sql database
    # distance_filtered_locs = get_distance_filtered_locs(lat,lng,est_miles)
    # print("distance filtered locs ", distance_filtered_locs)

    # attempt at left join on travel_time to include travel time from origin zip to each campsite: works!!
    # Get potential destinations filtered by "as the crow flies" distances calculated by sql database
    # Convert from tuples to dictionary
    col_names = ('ID', 'name', 'lat', 'lng', 'weather_url', 'travel_time')
    loc_tuples = get_distance_filtered_locs2(lat,lng,zipcode,est_miles)
    print("loc_tuples ", loc_tuples)
    distance_filtered_locs2 = [dict(zip(col_names, loc_tuple)) for loc_tuple in loc_tuples]
    print("distance filtered locs 2: ", distance_filtered_locs2)


    # get a list of actual travel times for all these potential destinations. Some will come from database, some will come from Google API
    durations = distance_matrix(zipcode, distance_filtered_locs)
    campsites = []
    i=0

    # make sure we got a travel duration for every potential campsite 
    if len(durations) != len(distance_filtered_locs):
      print("length of durations != length of locs, retrieval error, quitting", len(durations), len(distance_filtered_locs))
      break

    # build list of campsite objects with travel times and empty weather list
    # could try using 'zip' for this, but travel_time is not an element returned from distance_filtered_locs
    for loc in distance_filtered_locs:
      new_campsite = {}
      new_campsite['ID']= loc[0]
      new_campsite['name']= loc[1]
      new_campsite['lat']= loc[2]
      new_campsite['lng']= loc[3]
      new_campsite['weather_url']= loc[5]
      new_campsite['travel_time']= durations[i]
      new_campsite['weather']=[]
      campsites.append(new_campsite)
      i+=1

    print("campsites:  ", campsites)

    # now build list of subset of campsites that have acceptable drive time 
    # basic loop method:
    # travel_time_filtered_campsites = []
    # for campsite in campsites:
    #   if campsite['travel_time'] < travel_seconds:
    #     travel_time_filtered_campsites.append(campsite)

    # filter with lambda method
    # one liner is cool, but maybe harder to read? 
    # interesting-- filter returns an 'iterator' which is basically a linked list, not a dynamic array. Can't access indices
    # travel_time_filtered_campsites = filter(lambda campsite: campsite['travel_time'] < travel_seconds, campsites)

    # list comprehension method:
    travel_time_filtered_campsites = [campsite for campsite in campsites if campsite['travel_time'] < travel_seconds]
        
    print("Destinations within acceptable drive time: ")
    for campsite in travel_time_filtered_campsites:
      print(campsite['name'])

    # get user's weather preference and add weather details for those days at each campsite where weather is within bounds
    user_min = int(input("What's your minimum acceptable temperature? "))
    user_max = int(input("What's your maximum acceptable temperature? "))
    for campsite in travel_time_filtered_campsites:
      js = weather_forecast(campsite['lat'],campsite['lng'],campsite['weather_url'],campsite['ID'])
      for period in js['properties']['periods']:
        if period['isDaytime']:
          if period["temperature"] > user_min and period["temperature"] < user_max:
            campsite["weather"].append(period)

    # output acceptable weather windows at acceptable destinations
    # also create map
    fhand = codecs.open('where.js', 'w', "utf-8")
    fhand.write("myData = [\n")
    count = 0
    for campsite in travel_time_filtered_campsites:
      if len(campsite["weather"]):
        # print(campsite)
        lat = campsite["lat"]
        lng = campsite["lng"]
        name = campsite["name"]
        count = count + 1
        # write js file with array of campsite names and lats
        if count > 1 : fhand.write(",\n")
        output = "["+str(lat)+","+str(lng)+", '"+name+"']"
        fhand.write(output)

        # then print campsites with weather to console
        print('============================= \n')
        print("Destination: ", campsite["name"])
        for day in campsite["weather"]:
          print("Day: ", day["name"])
          print("Temperature: ", str(day["temperature"]))
          print("Weather: ", day["shortForecast"])
        print('\n')
    fhand.write("\n];\n")
    fhand.close()
    print(count, "records written to where.js")
    print("Open where.html to view the data in a browser")
    
    repeat = input('would you like to check a new origin? y/n: ')
    if repeat != 'y':
      break
  
