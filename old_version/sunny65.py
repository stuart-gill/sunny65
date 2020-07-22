# TODO: improve map html output. Somehow list drive time?

import codecs

from distance_matrix import distance_matrix
from geojson import geocode
from sunny65_db import get_distance_filtered_locs
from weather import weather_forecast

while True:
    address = input("Enter your location zipcode or address: ")
    if len(address) < 1:
        break

    # Use google api to get lat long for origin address
    (lat, lng, zipcode) = geocode(address)
    if not (lat or lng or zipcode):
        print("unsuitable address input \n")
        continue

    travel = float(input("How long are you willing to travel in hours? "))
    est_miles = travel * 40  # super rough guess of how far you could go in an hour
    travel_seconds = travel * 3600

    # Get potential destinations filtered by vector distances calculated by sql database
    # Convert from tuples to dictionary
    # this is using a generator pattern (I think) idea
    # from David Beazley's powerpoint deck on Generators
    col_names = ("ID", "name", "lat", "lng", "weather_url", "travel_time")
    loc_tuples = get_distance_filtered_locs(
        origin_lat=lat,
        origin_lng=lng,
        origin_zipcode=zipcode,
        acceptable_distance=est_miles,
    )
    print("loc_tuples ", loc_tuples)
    distance_filtered_locs = [
        dict(zip(col_names, loc_tuple)) for loc_tuple in loc_tuples
    ]
    # silly to loop again, but have to add weather key and empty array
    for loc in distance_filtered_locs:
        loc.update({"weather": []})

    # distance matrix takes the distance filtered locs and gets travel_time
    # from google for any locations that don't have them stored in database.
    # It both adds them to database and adds them to travel_time key in each
    # dictionary (mutating method). After this is run, every loc should have
    # a travel time
    distance_matrix(zipcode, distance_filtered_locs)

    # now build list of subset of campsites that have acceptable drive time,
    # trying out 'list comprehension'
    travel_time_filtered_campsites = [
        campsite
        for campsite in distance_filtered_locs
        if campsite["travel_time"] < travel_seconds
    ]

    print("Destinations within acceptable drive time: ")
    for campsite in travel_time_filtered_campsites:
        print(campsite["name"])

    # get user's weather preference and add weather details for those days at
    # each campsite where weather is within bounds
    user_min = int(input("What's your minimum acceptable temperature? "))
    user_max = int(input("What's your maximum acceptable temperature? "))
    for campsite in travel_time_filtered_campsites:
        js = weather_forecast(
            campsite["lat"], campsite["lng"], campsite["weather_url"], campsite["ID"]
        )
        for period in js["properties"]["periods"]:
            if period["isDaytime"]:
                if (
                    period["temperature"] > user_min
                    and period["temperature"] < user_max
                ):
                    campsite["weather"].append(period)

    # output acceptable weather windows at acceptable destinations
    # also create map
    fhand = codecs.open("where.js", "w", "utf-8")
    fhand.write("myData = [\n")
    count = 0
    for campsite in travel_time_filtered_campsites:
        if len(campsite["weather"]) > 0:
            # print(campsite)
            lat = campsite["lat"]
            lng = campsite["lng"]
            name = campsite["name"]
            count += 1
            # write js file with array of campsite names and lats
            if count > 1:
                fhand.write(",\n")
            output = "[" + str(lat) + "," + str(lng) + ", '" + name + "']"
            fhand.write(output)

            # then print campsites with weather to console
            print("============================= \n")
            print("Destination: ", campsite["name"])
            for day in campsite["weather"]:
                print("Day: ", day["name"])
                print("Temperature: ", str(day["temperature"]))
                print("Weather: ", day["shortForecast"])
            print("\n")
    fhand.write("\n];\n")
    fhand.close()
    print(count, "records written to where.js")
    print("Open where.html to view the data in a browser")

    repeat = input("would you like to check a new origin? y/n: ")
    if repeat != "y":
        break
