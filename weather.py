
import urllib.request, urllib.parse, urllib.error
import json
import ssl
from sunny65_db import set_weather_url

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

weather_service_url = 'https://api.weather.gov/points/'


def api_call(url):
  try: 
    uh = urllib.request.urlopen(url, context=ctx)
  except urllib.error.URLError as e:
    print("weather.gov request failed for this reason: ", e.reason)
  data = uh.read().decode()
  print('Retrieved', len(data), 'characters')

  try:
      js = json.loads(data)
  except:
      js = None
  
  return js


# Weather.gov api requires two calls-- first you sent lat/long to get applicable weather url. Then you call that url
# To save time, I'm adding the weather URL to the campsite database. This method checks to see if the URL is already stored there, and if not, it gets the url and stores it, along with making the actual api call for the forecast. In this way we're building the database as searches are made 
# TODO: build in failure resistance... if the stored weather_url fails, go back and get a new one
def weather_forecast(lat,lng, weather_url, ID):
  if weather_url:
    return api_call(weather_url)
  else:
    url = weather_service_url + lat + "," + lng
    forecast_url = api_call(url)["properties"]["forecast"]
    set_weather_url(forecast_url,ID)
    return api_call(forecast_url)
