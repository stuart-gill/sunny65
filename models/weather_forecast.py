from db import db

import config
import os
import requests


class WeatherForecastModel(db.Model):

    __tablename__ = "weather_forecasts"

    id = db.Column(db.Integer, primary_key=True)
    campsite_id = db.Column(db.Integer, db.ForeignKey("campsites.id"))
    forecast_time = db.Column(db.DateTime(timezone=True))
    short_forecast = db.Column(db.String)
    temperature = db.Column(db.Integer)
    time_created = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    campsite = db.relationship(
        "CampsiteModel",
        backref=db.backref("weather_forecasts", cascade="all, delete-orphan"),
    )

    def __init__(self, campsite_id, forecast_time, short_forecast, temperature):
        self.campsite_id = campsite_id
        self.forecast_time = forecast_time
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
    def get_forecast(cls, lat, lng):

        # api_key = os.environ.get("OPEN_WEATHER_API_KEY")
        api_key = config.OPEN_WEATHER_API_KEY
        serviceurl = "https://api.openweathermap.org/data/2.5/forecast"

        params = {"lat": lat, "lon": lng, "appid": api_key, "units": "imperial"}
        response = requests.get(serviceurl, params=params)
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
            "forecast_time": self.forecast_time.isoformat(),
            "short_forecast": self.short_forecast,
            "temperature": self.temperature,
            "time_created": self.time_created.isoformat(),
        }

