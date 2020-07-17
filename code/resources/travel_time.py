from flask_restful import Resource, reqparse
from models.travel_time import TravelTimeModel
from models.zipcode import ZipcodeModel


class TravelTime(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("zipcode_id", type=int)
    parser.add_argument("campsite_id", type=int)
    parser.add_argument("duration", type=int)
    parser.add_argument("willing_travel_time", type=int)
    parser.add_argument("zipcode", type=str)

    def get(self):
        data = TravelTime.parser.parse_args()
        return {
            "duration": TravelTimeModel.get_duration_from_google(
                data["zipcode"], data["campsite_id"]
            )
        }

    def post(self):
        data = TravelTime.parser.parse_args()
        if TravelTimeModel.find_by_ids(data["zipcode_id"], data["campsite_id"]):
            return {"message": f"this travel time already exists"}, 400

        if data["duration"]:
            travel_time = TravelTimeModel(
                data["zipcode_id"], data["campsite_id"], data["duration"]
            )
        else:
            duration = TravelTimeModel.get_duration_from_google(
                data["zipcode_id"], data["campsite_id"]
            )
            travel_time = TravelTimeModel(
                data["zipcode_id"], data["campsite_id"], duration
            )
        try:
            travel_time.save_to_db()
        except:
            return {"message": "an error occured while creating the travel time"}, 500

        return travel_time.json(), 201

    def put(self):
        data = TravelTime.parser.parse_args()
        travel_time = TravelTimeModel.find_by_ids(
            data["zipcode_id"], data["campsite_id"]
        )
        if travel_time:
            travel_time.duration = data["duration"]
        else:
            travel_time = TravelTimeModel(
                data["zipcode_id"], data["campsite_id"], data["duration"]
            )
        try:
            travel_time.save_to_db()
        except:
            return {"message": "an error occured while updating the travel time"}, 500

        return travel_time.json(), 201


class TravelTimeByZipList(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("willing_travel_time", type=int)

    def get(self, zipcode):
        data = TravelTimeByZipList.parser.parse_args()

        return {
            "travel_times": [
                travel_time.json()
                for travel_time in TravelTimeModel.find_campsites_by_duration(
                    zipcode, data["willing_travel_time"]
                )
            ]
        }


class TravelTimeList(Resource):
    def get(self):
        return {
            "travel_times": [
                travel_time.json() for travel_time in TravelTimeModel.query.all()
            ]
        }

