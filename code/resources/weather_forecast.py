from flask_restful import Resource, reqparse
from models.campsite import CampsiteModel
from models.weather_forecast import WeatherForecastModel
from pprint import pprint
from datetime import datetime, timezone

import requests


class WeatherForecastList(Resource):
    def get(self):
        """
        Get and list all weather forecasts for campsites that have a weather_url property
        """
        # for campsite in CampsiteModel.query.all():
        #     if campsite.weather_url:
        #         js = WeatherForecastModel.get_forecast(campsite.weather_url)
        #         try:
        #             for period in js["properties"]["periods"]:
        #                 if period["isDaytime"]:
        #                     forecast = WeatherForecastModel(
        #                         campsite.id,
        #                         period["name"],
        #                         period["detailedForecast"],
        #                         period["shortForecast"],
        #                         period["temperature"],
        #                     )
        #                     forecast.save_to_db()
        #         except:
        #             print(f"forecast for {campsite.name} failed")

        return {
            "forecasts": [
                forecast.json() for forecast in WeatherForecastModel.query.all()
            ]
        }


class WeatherForecastForCampsite(Resource):
    """
    Get and list all weather forecasts for one campsite by id
    """

    def get(self, campsite_id):
        forecasts = WeatherForecastModel.find_forecasts_for_campsite(campsite_id)
        return {"forecasts": [forecast.json() for forecast in forecasts]}

    def post(self, campsite_id):
        # first, delete all existing forecasts from database
        # doing this by calling api inside api call, to see how that works
        # not the best idea to delete all forecasts before successfully retrieving new ones-- need to change this, add failsafe
        requests.delete(f"http://127.0.0.1:5000/forecast/{campsite_id}")
        campsite = CampsiteModel.find_by_id(campsite_id)
        forecast_js = WeatherForecastModel.get_forecast(campsite.lat, campsite.lng)
        try:
            for period in forecast_js["list"]:
                time = datetime.fromtimestamp(period["dt"], tz=timezone.utc)
                short_forecast = period["weather"][0]["description"]
                temperature = period["main"]["temp"]
                forecast = WeatherForecastModel(
                    campsite_id, time, short_forecast, temperature
                )
                forecast.save_to_db()
            return {
                "message": f"forecasts for campsite {campsite_id} retrieved and inserted"
            }
        except:
            return {"message": "forecast post failure"}
        pprint(forecast_js)

    """
    Delete all weather forecasts for one campsite by id
    """

    def delete(self, campsite_id):
        forecasts = WeatherForecastModel.find_forecasts_for_campsite(campsite_id)
        for forecast in forecasts:
            forecast.delete_from_db()
        return {
            "message": f"all forecasts for campsite {campsite_id} have been deleted"
        }

