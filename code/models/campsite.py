from db import db
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
    weather_url = db.Column(db.String)
    weather_forecast = db.Column(db.String)

    zipcodes = db.relationship("ZipcodeModel", secondary="travel_time")

    # state_id = db.Column(db.Integer, db.ForeignKey("states.id"))
    # state = db.relationship("StateModel")  # hooks items and stores tables together

    def __init__(self, name, lat, lng, weather_url=None, weather_forecast=None):
        self.name = name
        self.lat = lat
        self.lng = lng
        self.weather_url = weather_url
        self.weather_forecast = weather_forecast

    def json(self):
        return {
            "name": self.name,
            "id": self.id,
            "lat": self.lat,
            "lng": self.lng,
            "weather_url": self.weather_url,
            "weather_forecast": self.weather_forecast,
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
    def find_by_distance_as_crow_flies(cls, origin_zipcode, acceptable_distance):
        """
        Get a list of all campsites within acceptable_distance of zipcode, as the crow flies
        """

        zipcode = ZipcodeModel.find_by_zipcode(origin_zipcode)
        origin_lat = zipcode.lat
        origin_lng = zipcode.lng

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

    def get_weather_url(self):
        lat, lng = str(self.lat), str(self.lng)
        url = "https://api.weather.gov/points/" + lat + "," + lng
        response = requests.get(url)
        # pprint(response.json())
        try:
            forecast_url = response.json()["properties"]["forecast"]
        except:
            forecast_url = None
        return forecast_url

    def get_weather_forecast(self):
        url = self.weather_url
        response = requests.get(url)
        pprint(response.json())
        return response.text

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def upsert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

