from flask_restful import Resource, reqparse
from models.travel_time import TravelTimeModel
from models.zipcode import ZipcodeModel
from models.campsite import CampsiteModel


class TravelTime(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("zipcode_id", type=int)
    parser.add_argument("campsite_id", type=int)
    parser.add_argument("duration", type=int)
    parser.add_argument("willing_travel_time", type=int)
    parser.add_argument("zipcode", type=str)

    # def get(self):
    #     data = TravelTime.parser.parse_args()
    #     return {
    #         "duration": TravelTimeModel.get_duration_from_google(
    #             data["zipcode"], data["campsite_id"]
    #         )
    #     }

    def post(self):
        data = TravelTime.parser.parse_args()
        if TravelTimeModel.find_by_ids(data["zipcode_id"], data["campsite_id"]):
            return {"message": f"this travel time already exists"}, 400

        if data["duration"]:
            travel_time = TravelTimeModel(
                data["zipcode_id"], data["campsite_id"], data["duration"]
            )
        else:
            try:
                duration = TravelTimeModel.get_duration_from_google(
                    data["zipcode_id"], data["campsite_id"]
                )
            except:
                return (
                    {
                        "message": "an error occured retrieving travel time from distance matrix api"
                    },
                    500,
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

    def post(self, zipcode):
        zipcode_id = ZipcodeModel.find_by_zipcode(zipcode).id
        campsites = CampsiteModel.find_by_distance_as_crow_flies(zipcode, 240)
        for campsite in campsites:
            try:
                duration = TravelTimeModel.get_duration_from_google(
                    zipcode_id, campsite.id
                )
            except:
                duration = -1
            travel_time = TravelTimeModel(zipcode_id, campsite.id, duration)
            travel_time.save_to_db()
        return {"message": "travel times inserted"}


class TravelTimeList(Resource):
    def get(self):
        return {
            "travel_times": [
                travel_time.json() for travel_time in TravelTimeModel.query.all()
            ]
        }

