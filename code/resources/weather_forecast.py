from flask_restful import Resource, reqparse
from models.campsite import CampsiteModel
from models.weather_forecast import WeatherForecastModel


class WeatherForecastList(Resource):
    def get(self):
        """
        Get and list all weather forecasts for campsites that have a weather_url property
        """
        for campsite in CampsiteModel.query.all():
            if campsite.weather_url:
                js = WeatherForecastModel.get_forecast(campsite.weather_url)
                try:
                    for period in js["properties"]["periods"]:
                        if period["isDaytime"]:
                            forecast = WeatherForecastModel(
                                campsite.id,
                                period["name"],
                                period["detailedForecast"],
                                period["shortForecast"],
                                period["temperature"],
                            )
                            forecast.save_to_db()
                except:
                    print(f"forecast for {campsite.name} failed")

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

