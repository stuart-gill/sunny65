from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.campsite import CampsiteModel


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
            try:
                campsite.lat = data["lat"]
                campsite.lng = data["lng"]
                campsite.weather_url = data["weather_url"]
            except:
                return {"message": "an error occurred updating the campsite"}, 500
        else:
            try:
                campsite = CampsiteModel(
                    name, data["lat"], data["lng"], data["weather_url"]
                )  # **data would expand to data["price"], data["store_id"]
                campsite.upsert()
            except:
                return {"message": "an error occured inserting the campsite"}, 500
        campsite.upsert()
        return campsite.json()


class CampsiteList(Resource):
    def get(self):
        return {
            "campsites": [campsite.json() for campsite in CampsiteModel.query.all()]
        }


class CampsiteByZipList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("acceptable_distance", type=float)

    def post(self, zipcode):
        data = CampsiteByZipList.parser.parse_args()
        campsites = CampsiteModel.find_by_distance_as_crow_flies(
            zipcode, data["acceptable_distance"]
        )
        return {"campsites": [campsite.json() for campsite in campsites]}

