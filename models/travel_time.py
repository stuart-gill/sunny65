from db import db
import polyline


# uncomment if running locally with config folder
# import config

import os

import requests


class TravelTimeModel(db.Model):

    __tablename__ = "travel_time"

    id = db.Column(db.Integer, primary_key=True)
    zipcode_id = db.Column(db.Integer, db.ForeignKey("zipcodes.id"))
    campsite_id = db.Column(db.Integer, db.ForeignKey("campsites.id"))
    duration_value = db.Column(db.Integer)
    duration_text = db.Column(db.String(80))
    __table_args__ = (
        db.UniqueConstraint("zipcode_id", "campsite_id", name="_campsite_zipcode_uc"),
    )

    # don't need zipcode info, hence lazy="noload"
    zipcode = db.relationship(
        "ZipcodeModel",
        backref=db.backref("travel_time", cascade="all, delete-orphan", lazy="noload"),
    )
    campsite = db.relationship(
        "CampsiteModel",
        backref=db.backref("travel_time", cascade="all, delete-orphan"),
    )

    # leave id off object creation since DB autoincrements it... we should never be entering an ID
    def __init__(self, zipcode_id, campsite_id, duration_value, duration_text):
        self.zipcode_id = zipcode_id
        self.campsite_id = campsite_id
        self.duration_value = duration_value
        self.duration_text = duration_text

    @classmethod
    def find_by_ids(cls, zipcode_id, campsite_id):

        return cls.query.filter_by(
            zipcode_id=zipcode_id, campsite_id=campsite_id
        ).first()

    # think that db.joinedload(campsite) will auto load campsite for each duration in one select statement rather than two
    @classmethod
    def find_campsites_by_duration(cls, zipcode_id, willing_duration):
        return (
            cls.query.filter_by(zipcode_id=zipcode_id)
            .filter(cls.duration_value < willing_duration, cls.duration_value >= 0)
            .options(db.joinedload(cls.campsite))
            .all()
        )

    @classmethod
    def get_duration_from_google(
        cls, zipcode_lat, zipcode_lng, campsite_lat, campsite_lng
    ):
        # for hosted on Digital Ocean (and Heroku too?)
        api_key = os.environ.get("GMAPS_API_KEY")
        # if hosted locally
        if not api_key:
            api_key = config.GMAPS_API_KEY
        serviceurl = "https://maps.googleapis.com/maps/api/distancematrix/json?"

        params = {
            "origins": f"{zipcode_lat},{zipcode_lng}",
            "destinations": f"{campsite_lat},{campsite_lng}",
            "key": api_key,
        }
        response = requests.get(serviceurl, params=params)
        js = response.json()

        duration_value = js["rows"][0]["elements"][0]["duration"]["value"]
        duration_text = js["rows"][0]["elements"][0]["duration"]["text"]
        return (duration_value, duration_text)

    # get durations in batches of 25 campsite locations to save time
    @classmethod
    def get_durations_from_google(cls, zipcode_lat, zipcode_lng, campsite_locations):
        # for hosted on Digital Ocean (and Heroku too?)
        api_key = os.environ.get("GMAPS_API_KEY")
        # if hosted locally
        if not api_key:
            api_key = config.GMAPS_API_KEY
        serviceurl = "https://maps.googleapis.com/maps/api/distancematrix/json?"

        # polyline encoding destinations tuples for batching distance matrix api call
        destinations_param = "enc:" + polyline.encode(campsite_locations) + ":"
        params = {
            "origins": f"{zipcode_lat},{zipcode_lng}",
            "destinations": destinations_param,
            "key": api_key,
        }
        response = requests.get(serviceurl, params=params)
        js = response.json()
        elements = js["rows"][0]["elements"]

        return elements

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def json(self):
        return {
            "duration": {"value": self.duration_value, "text": self.duration_text},
            "campsite": self.campsite.json(),
        }

