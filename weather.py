import json
import requests

from sunny65_db import get_weather_forecast, set_weather_forecast, set_weather_url

WEATHER_SERVICE_URL = "https://api.weather.gov/points/"


def weather_forecast(lat, lng, weather_url, campsite_id):
    """Weather.gov api requires two calls-- first you sent lat/long to get applicable weather url.
	Then you call that url to get the forecast. To save time, I'm adding the weather URL to the
	campsite database. This method checks to see if the URL is already stored there, and if not,
	it gets the url and stores it, along with making the actual api call for the forecast.
	In this way we're building the database as searches are made
	Args:
	lat: latitude of campsite
	lng: longitude of campsite
	weather_url: url for forecast for campsite, if it was already in database
	campsite_id: id of campsite in database
	Returns:
	forecast JSON
	TODO: build in failure resistance... if the stored weather_url fails, get a new one"""

    forecast_from_database = get_weather_forecast(campsite_id)

    if forecast_from_database:
        return json.loads(forecast_from_database)
    # if we don't have forecast url, get it
    if not weather_url:
        lat = str(lat)
        lng = str(lng)
        url = WEATHER_SERVICE_URL + lat + "," + lng
        response = requests.get(url)
        weather_url = response.json()["properties"]["forecast"]
        set_weather_url(weather_url, campsite_id)
    response = requests.get(weather_url)
    set_weather_forecast(response.text, campsite_id)
    return response.json()
