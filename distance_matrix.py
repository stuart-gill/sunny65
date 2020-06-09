import json
import ssl
import config
import urllib.request, urllib.parse, urllib.error
import polyline
import math
from sunny65_db import set_travel_time, get_travel_time



def distance_matrix(zipcode, distance_filtered_locs):
  """Fetches travel times from origin zipcode to various campsites. First it checks the database to see if we have the travel time stored, and then it checks the google distance matrix API for all those durations not found in database, and also adds those newfound durations to the database
  Args: 
    zipcode: integer, origin zipcode
    distance_filtered_locs: list of tuples with information about potential destinations

  Returns: 
    A list of travel time durations in seconds that corresponds to the list of potential destinations. Travel times that cannot be retrieved with the google api are listed as -1
  """

  api_key = config.GMAPS_API_KEY

  serviceurl = 'https://maps.googleapis.com/maps/api/distancematrix/json?'

  # Ignore SSL certificate errors
  ctx = ssl.create_default_context()
  ctx.check_hostname = False
  ctx.verify_mode = ssl.CERT_NONE


  durations_from_db = []
  locs_sans_durations = []
  durations_from_api = []

  # get the durations we have stored in database, and make sure we go look up durations for those that we don't have, and add those to database
  # TODO: set an expiration on durations in the database?
  # for loc in distance_filtered_locs:
  #   travel_time=get_travel_time(zipcode,loc[0])
  #   durations_from_db.append(travel_time)
  #   if not travel_time:
  #     locs_sans_durations.append(loc)

  locs_sans_durations = [loc for loc in distance_filtered_locs if not loc['travel_time']]

  
  print("locs sans durations: ", locs_sans_durations)

  iterations = math.ceil(len(locs_sans_durations)/25)
  print("\n\n ITERATIONS: ", iterations, "\n\n")

  for i in range(iterations):
    # Add each potential destination to destinations parameter using encoded polyline: https://developers.google.com/maps/documentation/utilities/polylinealgorithm
    destinations_parm = ''
    destinations_list = []
    for loc in locs_sans_durations[(i*25):((i+1)*25)]:
      loc_tuple = (loc['lat'], loc['lng'])
      destinations_list.append(loc_tuple)
    print(destinations_list)
    destinations_parm = 'enc:' + polyline.encode(destinations_list) + ':'
    
    # Build the rest of the api call 
    parms = dict()
    parms['origins'] = zipcode
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
        durations_from_api.append(element["duration"]["value"])
      else: durations_from_api.append(-1)
    
    for j in range(i*25,(i+1)*25):
      # to prevent out of range error
      if j < len(locs_sans_durations):
        campsite_id = locs_sans_durations[j]['ID']
        travel_time = durations_from_api[j]
        set_travel_time(zipcode, campsite_id, travel_time)
        locs_sans_durations[j]['travel_time']= durations_from_api[j]

  # now, shuffle the durations retrieved from api in with the durations we already got from the database
  # complete_durations = []
  # for duration in durations_from_db:
  #   if duration == None:
  #     complete_durations.append(durations_from_api.pop(0))
  #   else: complete_durations.append(duration)
  # return complete_durations
