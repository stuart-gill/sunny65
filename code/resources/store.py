from flask_restful import Resource
from models.zipcode import ZipcodeModel


class Zipcode(Resource):
    def get(self, name):
        zipcode = ZipcodeModel.find_by_name(name)
        if zipcode:
            return zipcode.json()
        return {"message": "zipcode not found"}, 404

    def post(self, name, lat, lng):
        if ZipcodeModel.find_by_name(name):
            return {"message": f"a zipcode with the name '{name}' already exists"}, 400

        zipcode = ZipcodeModel(name, lat, lng)
        try:
            zipcode.save_to_db()
        except:
            return {"message": "an error occured while creating the zipcode"}, 500

        return zipcode.json(), 201

    def delete(self, name):
        zipcode = ZipcodeModel.find_by_name(name)
        if zipcode:
            zipcode.delete_from_db()
            return {"message": "zipcode deleted"}
        return {"message": "a zipcode with that name could not be found"}


class ZipcodeList(Resource):
    def get(self):
        return {"zipcodes": [zipcode.json() for zipcode in ZipcodeModel.query.all()]}
