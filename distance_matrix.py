import json
import ssl
import config
import urllib.request, urllib.parse, urllib.error


def distance_matrix(address, distance_filtered_locs):

  api_key = config.GMAPS_API_KEY

  serviceurl = 'https://maps.googleapis.com/maps/api/distancematrix/json?'

  # Ignore SSL certificate errors
  ctx = ssl.create_default_context()
  ctx.check_hostname = False
  ctx.verify_mode = ssl.CERT_NONE

  # Add each potential destination to destinations parameter
  # TODO: implement encoded polyline format for Google distance matrix api call: https://developers.google.com/maps/documentation/utilities/polylinealgorithm
  destinations_parm = ''
  for loc in distance_filtered_locs:
    destinations_parm += str(loc[2]) + "," + str(loc[3]) + '|'
  
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

  # print(json.dumps(js, indent=4))
  return js
