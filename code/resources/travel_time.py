from flask_restful import Resource, reqparse
from models.travel_time import TravelTimeModel


class TravelTime(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("zipcode_id", type=int)
    parser.add_argument("campsite_id", type=int)
    parser.add_argument("duration", type=int)
    parser.add_argument("willing_travel_time", type=int)

    def post(self):
        data = TravelTime.parser.parse_args()
        if TravelTimeModel.find_by_ids(data["zipcode_id"], data["campsite_id"]):
            return {"message": f"this travel time already exists"}, 400

        travel_time = TravelTimeModel(
            data["zipcode_id"], data["campsite_id"], data["duration"]
        )
        try:
            travel_time.save_to_db()
        except:
            return {"message": "an error occured while creating the travel time"}, 500

        return travel_time.json(), 201


class TravelTimeByZipList(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("willing_travel_time", type=int)

    def get(self, zipcode_id):
        data = TravelTimeByZipList.parser.parse_args()
        return {
            "travel_times": [
                travel_time.json()
                for travel_time in TravelTimeModel.find_campsites_by_duration(
                    zipcode_id, data["willing_travel_time"]
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

