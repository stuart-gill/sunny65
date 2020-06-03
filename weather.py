
import urllib.request, urllib.parse, urllib.error
import json
import ssl

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


def weather_forecast(lat,lng):
  url = weather_service_url + lat + "," + lng
  forecast_url = api_call(url)["properties"]["forecast"]
  return api_call(forecast_url)
