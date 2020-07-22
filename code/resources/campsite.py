from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.campsite import CampsiteModel
from models.weather_forecast import WeatherForecastModel
import time


# resources used to map endpoints (like get, post) to /campsite/name or whatever
# anything not called by an API directly shouldn't be a resource but a model

# resources use models to interpret data pulled from database... models stand on their own


class Campsite(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("lat", type=float)
    parser.add_argument("lng", type=float)
    parser.add_argument("weather_url", type=str)
    parser.add_argument("weather_forecast", type=str)

    # @jwt_required()
    def get(self, name):
        campsite = CampsiteModel.find_by_name(name)
        if campsite:
            return campsite.json()
        return {"message": "campsite not found"}, 404

    def post(self, name):
        if CampsiteModel.find_by_name(name):
            return {"message": f"an campsite with name {name} already exists"}, 400

        data = Campsite.parser.parse_args()
        campsite = CampsiteModel(
            name,
            data["lat"],
            data["lng"],
            data["weather_url"],
            data["weather_forecast"],
        )

        try:
            campsite.upsert()
        except:
            return (
                {"message": "an error occured while trying to post the campsite"},
                500,
            )

        # note: we always have to return json
        return campsite.json(), 201

    # @jwt_required()
    def delete(self, name):
        campsite = CampsiteModel.find_by_name(name)
        if campsite:
            campsite.delete()
            return {"message": "campsite deleted"}
        return {"message": "campsite not found"}, 404

    def put(self, name):

        data = Campsite.parser.parse_args()

        campsite = CampsiteModel.find_by_name(name)

        if campsite:
            campsite.lat = data["lat"]
            campsite.lng = data["lng"]
            campsite.weather_url = data["weather_url"]
        else:
            campsite = CampsiteModel(
                name, data["lat"], data["lng"], data["weather_url"]
            )
        try:
            campsite.upsert()
            return campsite.json()
        except:
            return {"message": "an error occured inserting the campsite"}, 500


class CampsiteList(Resource):
    def get(self):
        campsites = CampsiteModel.query.all()

        return {
            "count": len(campsites),
            "campsites": [campsite.json() for campsite in campsites],
        }


class CampsiteByZipList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("acceptable_distance", type=float)

    def get(self, zipcode):
        """
        Get a list of all campsites within acceptable_distance of zipcode, as the crow flies
        """
        data = CampsiteByZipList.parser.parse_args()
        campsites = CampsiteModel.find_by_distance_as_crow_flies(
            zipcode, data["acceptable_distance"]
        )
        for campsite in campsites:
            # get campsite weather url from weather.gov
            if not campsite.weather_url:
                campsite.weather_url = campsite.get_weather_url()
                campsite.upsert()
            # get forecast for campsite
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
            "count": len(campsites),
            "campsites": [campsite.json() for campsite in campsites],
        }

