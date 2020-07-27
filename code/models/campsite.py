from db import db
from models.travel_time import TravelTimeModel
from models.zipcode import ZipcodeModel

import numpy as np
import requests
from pprint import pprint


class CampsiteModel(db.Model):
    __tablename__ = "campsites"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    lat = db.Column(db.Float(precision=6))
    lng = db.Column(db.Float(precision=5))

    zipcodes = db.relationship("ZipcodeModel", secondary="travel_time", lazy="noload")

    # dont' need this line because backref in weather_forecasts creates realtionship and "weather_forecasts" list
    # weather_forecasts = db.relationship(
    #     "WeatherForecastModel", backref=db.backref("campsite", lazy="joined")
    # )

    # state_id = db.Column(db.Integer, db.ForeignKey("states.id"))
    # state = db.relationship("StateModel")  # hooks items and stores tables together

    def __init__(self, name, lat, lng):
        self.name = name
        self.lat = lat
        self.lng = lng

    def json(self):
        return {
            "name": self.name,
            "id": self.id,
            "lat": self.lat,
            "lng": self.lng,
            "forecasts": [forecast.json() for forecast in self.weather_forecasts],
        }

    def json_without_forecasts(self):
        return {
            "name": self.name,
            "id": self.id,
            "lat": self.lat,
            "lng": self.lng,
        }

    @classmethod
    def find_by_name(cls, name):
        # this line replaces everything below
        return cls.query.filter_by(
            name=name
        ).first()  # gets first row, converts row to ItemModel object and returns that. Query is part of sqlalchemy

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_distance_as_crow_flies(
        cls, origin_lat, origin_lng, acceptable_distance
    ):
        """
        Get a list of all campsites within acceptable_distance of zipcode, as the crow flies
        """

        EARTH_RADIUS = 3960
        max_lat = origin_lat + np.rad2deg(acceptable_distance / EARTH_RADIUS)
        min_lat = origin_lat - np.rad2deg(acceptable_distance / EARTH_RADIUS)

        max_lng = origin_lng + np.rad2deg(
            acceptable_distance / EARTH_RADIUS / np.cos(np.deg2rad(origin_lat))
        )
        min_lng = origin_lng - np.rad2deg(
            acceptable_distance / EARTH_RADIUS / np.cos(np.deg2rad(origin_lat))
        )

        return cls.query.filter(
            cls.lat > min_lat, cls.lat < max_lat, cls.lng > min_lng, cls.lng < max_lng
        ).all()

    @classmethod
    def find_by_duration(cls, zipcode_id, max_duration):

        return (
            cls.query.join(TravelTimeModel)
            .filter(
                (TravelTimeModel.zipcode_id == zipcode_id)
                & (TravelTimeModel.duration < max_duration)
            )
            .all()
        )

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def upsert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

