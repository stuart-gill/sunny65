import sqlite3
from db import db
from models.zipcode import ZipcodeModel
from models.campsite import CampsiteModel
import config

import requests


class TravelTimeModel(db.Model):

    __tablename__ = "travel_time"

    id = db.Column(db.Integer, primary_key=True)
    zipcode_id = db.Column(db.Integer, db.ForeignKey("zipcodes.id"))
    campsite_id = db.Column(db.Integer, db.ForeignKey("campsites.id"))
    duration = db.Column(db.Integer)

    zipcode = db.relationship(
        ZipcodeModel, backref=db.backref("travel_time", cascade="all, delete-orphan")
    )
    campsite = db.relationship(
        CampsiteModel, backref=db.backref("travel_time", cascade="all, delete-orphan")
    )

    # leave id off object creation since DB autoincrements it... we should never be entering an ID
    def __init__(self, zipcode_id, campsite_id, duration):
        self.zipcode_id = zipcode_id
        self.campsite_id = campsite_id
        self.duration = duration

    @classmethod
    def find_by_ids(cls, zipcode_id, campsite_id):

        return cls.query.filter_by(
            zipcode_id=zipcode_id, campsite_id=campsite_id
        ).first()

    @classmethod
    def find_campsites_by_duration(cls, zipcode, willing_duration):
        zipcode_id = ZipcodeModel.find_by_zipcode(zipcode).id
        return (
            cls.query.filter_by(zipcode_id=zipcode_id)
            .filter(cls.duration < willing_duration, cls.duration >= 0)
            .all()
        )

    @classmethod
    def get_duration_from_google(cls, zipcode_id, campsite_id):
        zipcode = ZipcodeModel.find_by_id(zipcode_id)
        campsite = CampsiteModel.find_by_id(campsite_id)
        origin_lat, origin_lng = zipcode.lat, zipcode.lng
        destination_lat, destination_lng = campsite.lat, campsite.lng

        api_key = config.GMAPS_API_KEY
        serviceurl = "https://maps.googleapis.com/maps/api/distancematrix/json?"

        params = {
            "origins": f"{origin_lat},{origin_lng}",
            "destinations": f"{destination_lat},{destination_lng}",
            "key": api_key,
        }
        response = requests.get(serviceurl, params=params)
        js = response.json()
        duration = js["rows"][0]["elements"][0]["duration"]["value"]
        return duration

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def json(self):
        return {
            "zipcode_id": self.zipcode_id,
            "zipcode": self.zipcode.zipcode,
            "campsite_id": self.campsite_id,
            "campsite_name": self.campsite.name,
            "travel_time": self.duration,
        }

