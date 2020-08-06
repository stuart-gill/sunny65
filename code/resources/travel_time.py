from flask_restful import Resource, reqparse
from models.travel_time import TravelTimeModel
from models.zipcode import ZipcodeModel
from models.campsite import CampsiteModel


class TravelTime(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("zipcode_id", type=int)
    parser.add_argument("campsite_id", type=int)
    parser.add_argument("duration_value", type=int)
    parser.add_argument("duration_text", type=int)
    parser.add_argument("willing_travel_time", type=int)
    parser.add_argument("zipcode", type=str)

    def get(self):
        """
        Get travel time between one zipcode id and campsite id. Not setting db value here
        """

        data = TravelTime.parser.parse_args()
        duration_value, duration_text = TravelTimeModel.get_duration_from_google(
            data["zipcode_id"], data["campsite_id"]
        )
        return {"duration_value": duration_value, "duration_text": duration_text}

    def post(self):
        """
        Post travel time between one zipcode id and one campsite id. If request body doesn't contain travel duration, 
        we'll find out the travel duration from google matrix api and use that.
        """

        data = TravelTime.parser.parse_args()
        if TravelTimeModel.find_by_ids(data["zipcode_id"], data["campsite_id"]):
            return {"message": f"this travel time already exists"}, 400

        if data["duration"]:
            travel_time = TravelTimeModel(
                data["zipcode_id"],
                data["campsite_id"],
                data["duration_value"],
                data["duration_text"],
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
                data["zipcode_id"], data["campsite_id"], *duration
            )
        try:
            travel_time.save_to_db()
        except:
            return {"message": "an error occured while creating the travel time"}, 500

        return travel_time.json(), 201

    def put(self):
        """
        Update or post if not in database already. Requires duration in request body.
        """

        data = TravelTime.parser.parse_args()
        travel_time = TravelTimeModel.find_by_ids(
            data["zipcode_id"], data["campsite_id"]
        )
        if travel_time:
            travel_time.duration_value = data["duration_value"]
            travel_time.duration_text = data["duration_text"]
        else:
            travel_time = TravelTimeModel(
                data["zipcode_id"],
                data["campsite_id"],
                data["duration_value"],
                data["duration_text"],
            )
        try:
            travel_time.save_to_db()
        except:
            return {"message": "an error occured while updating the travel time"}, 500

        return travel_time.json(), 201


class TravelTimeByZipList(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("willing_travel_time", type=int)
    parser.add_argument("maximum_linear_distance", type=int)
    parser.add_argument("min_temp", type=int)

    def get(self, zipcode):
        """
        Get a list of travel times from origin zipcode that are under the willing travel time (includes all forecasts)
        """

        data = TravelTimeByZipList.parser.parse_args()
        zipcode_obj = ZipcodeModel.find_by_zipcode(zipcode)

        min_temp = data["min_temp"]
        travel_times = TravelTimeModel.find_campsites_by_duration(
            zipcode_obj.id, data["willing_travel_time"]
        )

        return {
            "count": len(travel_times),
            "travel_times": [travel_time.json() for travel_time in travel_times],
        }

    def post(self, zipcode):
        """
        From origin zipcode, get a list of distance appropriate campsites, then use google distance matrix to calculate travel times between zipcode and each campsite. Save each to the db. Unclear to me whether calling this will overwrite existing travel_times or not. It does not seem to create duplicates. 
        """
        data = TravelTimeByZipList.parser.parse_args()
        zipcode_obj = ZipcodeModel.find_by_zipcode(zipcode)
        # is there any advantage to calling API below rather than using CampsiteModel directly?
        campsites = CampsiteModel.find_by_distance_as_crow_flies(
            zipcode_obj.lat, zipcode_obj.lng, data["maximum_linear_distance"]
        )
        for campsite in campsites:
            try:
                duration = TravelTimeModel.get_duration_from_google(
                    zipcode_obj.lat, zipcode_obj.lng, campsite.lat, campsite.lng
                )
            except:
                duration = (-1, "")

            existing_travel_time = TravelTimeModel.find_by_ids(
                zipcode_obj.id, campsite.id
            )
            if existing_travel_time:
                existing_travel_time.delete()
            travel_time = TravelTimeModel(zipcode_obj.id, campsite.id, *duration)
            try:
                travel_time.save_to_db()
            except:
                print(f"save travel time failed for campsite {campsite.id}")
        return {"message": "travel times inserted"}


class TravelTimeList(Resource):
    def get(self):
        """
        List all travel times in database
        """
        travel_times = TravelTimeModel.query.all()
        return {
            "count": len(travel_times),
            "travel_times": [travel_time.json() for travel_time in travel_times],
        }

