import json
import ssl
import config
import urllib.request, urllib.parse, urllib.error
import polyline
import math
from sunny65_db import set_travel_time, get_travel_time



def distance_matrix(zipcode, distance_filtered_locs):
  """Checks distance filterd locs array of dicts for locs without travel times. Those travel times will be added to list to be sent to google distance matrix. The travel durations found (in seconds) will be added to the database and to the distance_filtered_locs array of dictionaries. 

  Args: 
    zipcode: integer, origin zipcode
    distance_filtered_locs: list of dicts with information about potential destinations

  Returns: 
    void
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

  # TODO: set an expiration on durations in the database?

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


