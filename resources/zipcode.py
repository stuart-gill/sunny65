from flask_restful import Resource, reqparse
from models.zipcode import ZipcodeModel


class Zipcode(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("lat", type=float)
    parser.add_argument("lng", type=float)

    def get(self, zipcode):
        zipcode = ZipcodeModel.find_by_zipcode(zipcode)
        if zipcode:
            return zipcode.json()
        return {"message": "zipcode not found"}, 404

    def post(self, zipcode):
        if ZipcodeModel.find_by_zipcode(zipcode):
            return {"message": f"a zipcode '{zipcode}' already exists"}, 400

        data = Zipcode.parser.parse_args()
        zipcode = ZipcodeModel(zipcode, data["lat"], data["lng"])
        try:
            zipcode.save_to_db()
        except:
            return {"message": "an error occured while creating the zipcode"}, 500

        return zipcode.json(), 201

    def put(self, zipcode):

        data = Zipcode.parser.parse_args()

        zipcode = ZipcodeModel.find_by_zipcode(zipcode)

        if zipcode:
            try:
                zipcode.lat = data["lat"]
                zipcode.lng = data["lng"]
            except:
                return {"message": "an error occurred updating the zipcode"}, 500
        else:
            try:
                zipcode = ZipcodeModel(zipcode, data["lat"], data["lng"])
                zipcode.save_to_db()
            except:
                return {"message": "an error occured inserting the zipcode"}, 500
        zipcode.save_to_db()
        return zipcode.json()

    def delete(self, zipcode):
        zipcode = ZipcodeModel.find_by_zipcode(zipcode)
        if zipcode:
            zipcode.delete_from_db()
            return {"message": "zipcode deleted"}
        return {"message": f"a zipcode {zipcode} could not be found"}


class ZipcodeList(Resource):
    def get(self):
        zipcodes = ZipcodeModel.query.all()
        return {
            "count": len(zipcodes),
            "zipcodes": [zipcode.json() for zipcode in zipcodes],
        }
