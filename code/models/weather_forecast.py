import sqlite3
from db import db
from models.campsite import CampsiteModel
import config

import requests


# user is in models instead of resources because there are no API endpoints for User information
# model is the internal representation, resource is the external representation


class WeatherForecastModel(db.Model):

    __tablename__ = "weather_forecasts"

    id = db.Column(db.Integer, primary_key=True)
    campsite_id = db.Column(db.Integer, db.ForeignKey("campsites.id"))
    name = db.Column(db.String)
    detailed_forecast = db.Column(db.String)
    short_forecast = db.Column(db.String)
    temperature = db.Column(db.Integer)
    time_created = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    campsite = db.relationship(
        CampsiteModel,
        backref=db.backref("weather_forecasts", cascade="all, delete-orphan"),
    )

    def __init__(
        self, campsite_id, name, detailed_forecast, short_forecast, temperature
    ):
        self.campsite_id = campsite_id
        self.name = name
        self.detailed_forecast = detailed_forecast
        self.short_forecast = short_forecast
        self.temperature = temperature

    @classmethod
    def find_by_campsite_id(cls, campsite_id):

        return cls.query.filter_by(campsite_id=campsite_id).all()

    # @classmethod  (can turn into find by temperature range)
    # def find_campsites_by_duration(cls, zipcode, willing_duration):
    #     zipcode_id = ZipcodeModel.find_by_zipcode(zipcode).id
    #     return (
    #         cls.query.filter_by(zipcode_id=zipcode_id)
    #         .filter(cls.duration < willing_duration, cls.duration >= 0)
    #         .all()
    #     )

    @classmethod
    def get_forecast(cls, weather_url):
        url = weather_url
        response = requests.get(url)

        if response.status_code != 200:
            print(f"status code for forecast: {response.status_code}")
            print(response.text)
        js = response.json()
        return js

    @classmethod
    def find_forecasts_for_campsite(cls, campsite_id):
        return cls.query.filter_by(campsite_id=campsite_id).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def json(self):
        return {
            "campsite_id": self.campsite_id,
            "campsite_name": self.campsite.name,
            "name": self.name,
            "short_foreast": self.short_forecast,
            "detailed_forecast": self.detailed_forecast,
            "temperature": self.temperature,
            "time_created": self.time_created.isoformat(),
        }

