from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.campsite import CampsiteModel
from models.weather_forecast import WeatherForecastModel

import requests


# resources used to map endpoints (like get, post) to /campsite/name or whatever
# anything not called by an API directly shouldn't be a resource but a model

# resources use models to interpret data pulled from database... models stand on their own


class Campsite(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("campsite_id", type=int)
    parser.add_argument("name", type=str)
    parser.add_argument("lat", type=float)
    parser.add_argument("lng", type=float)

    # @jwt_required()
    def get(self):
        data = Campsite.parser.parse_args()
        campsite_id = data["campsite_id"]
        campsite = CampsiteModel.find_by_id(campsite_id)
        if campsite:
            return campsite.json()
        return {"message": "campsite not found"}, 404

    def post(self):
        data = Campsite.parser.parse_args()
        name = data["name"]
        lat = data["lat"]
        lng = data["lng"]
        if CampsiteModel.find_by_name(name):
            return {"message": f"an campsite with name {name} already exists"}, 400

        data = Campsite.parser.parse_args()
        campsite = CampsiteModel(name, lat, lng)

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
    def delete(self):
        data = Campsite.parser.parse_args()
        campsite_id = data["campsite_id"]
        print(campsite_id)
        campsite = CampsiteModel.find_by_id(campsite_id)
        if campsite:
            campsite.delete()
            return {"message": "campsite deleted"}
        return {"message": "campsite not found"}, 404

    def put(self):

        data = Campsite.parser.parse_args()
        campsite = CampsiteModel.find_by_id(data["campsite_id"])

        if campsite:
            campsite.name = data["name"]
            campsite.lat = data["lat"]
            campsite.lng = data["lng"]
        else:
            return {"message": f"campsite with id {data['campsite_id']} not found"}
        try:
            campsite.upsert()
            return campsite.json()
        except:
            return {"message": "an error occured updating the campsite"}, 500


class CampsiteList(Resource):
    def get(self):
        campsites = CampsiteModel.query.all()

        return {
            "count": len(campsites),
            "campsites": [campsite.json_without_forecasts() for campsite in campsites],
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
        return {
            "count": len(campsites),
            "campsites": [campsite.json_without_forecasts() for campsite in campsites],
        }


# class CampsiteByWeatherList(Resource):
#     parser = reqparse.RequestParser()
#     parser.add_argument("min_temp", type=float)

#     def get(self, zipcode):
#         """
#         Get a list of all campsites with acceptable weather within a certain range
#         """

