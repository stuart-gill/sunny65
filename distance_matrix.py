import json
import ssl
import config
import urllib.request, urllib.parse, urllib.error
import polyline
import math
from sunny65_db import set_travel_time


def distance_matrix(address, zipcode, distance_filtered_locs):

  api_key = config.GMAPS_API_KEY

  serviceurl = 'https://maps.googleapis.com/maps/api/distancematrix/json?'

  # Ignore SSL certificate errors
  ctx = ssl.create_default_context()
  ctx.check_hostname = False
  ctx.verify_mode = ssl.CERT_NONE


  # TODO: build a table of origins and a join table (many to many) of origin->destination general travel times. This would require generalizing origins -- "seattle area" -- to avoid having infinite origins


# At this point I'm batching distance API requests to work with Googles 25 destination max per call. 
# Could get expensive at .005 cents per call. 

  durations = []
  iterations = math.ceil(len(distance_filtered_locs)/25)
  print("\n\n ITERATIONS: ", iterations, "\n\n")

  for i in range(iterations):
    # Add each potential destination to destinations parameter using encoded polyline: https://developers.google.com/maps/documentation/utilities/polylinealgorithm
    destinations_parm = ''
    destinations_list = []
    for loc in distance_filtered_locs[(i*25):((i+1)*25)]:
      loc_tuple = (loc[2], loc[3])
      destinations_list.append(loc_tuple)
    print(destinations_list)
    destinations_parm = 'enc:' + polyline.encode(destinations_list) + ':'

    # for loc in distance_filtered_locs:
    #   destinations_parm += str(loc[2]) + "," + str(loc[3]) + '|'
    
    # Build the rest of the api call 
    parms = dict()
    parms['origins'] = address
    parms['destinations']= destinations_parm
    parms['key'] = api_key
    url = serviceurl + urllib.parse.urlencode(parms)

    # GET LOCATIONS FROM GOOGLE DISTANCE MATRIX
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

    print(json.dumps(js, indent=4))
    elements=(js["rows"][0]["elements"])
    for element in elements:
      if element["status"] == "OK":
        durations.append(element["duration"]["value"])
      else: durations.append(-1)
    
    for j in range(i*25,(i+1)*25):
      if j < len(distance_filtered_locs):
        campsite_id = distance_filtered_locs[j][0]
        travel_time = durations[j]
        set_travel_time(zipcode, campsite_id, travel_time)

  return durations
