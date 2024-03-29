from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

import os

from security import authenticate, identity
from resources.user import UserRegister
from resources.campsite import Campsite, CampsiteList, CampsiteByZipList
from resources.zipcode import Zipcode, ZipcodeList
from resources.travel_time import TravelTime, TravelTimeList, TravelTimeByZipList
from resources.weather_forecast import WeatherForecastList, WeatherForecastForCampsite
from db import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///data.db"
)
# confusing-- I think this keep flask from tracking changes but lets SQLalchemy do it??
app.config["SQLALCHEMY_TRACK_NOTIFICATIONS"] = False
app.secret_key = "stuart"
api = Api(app)


jwt = JWT(
    app, authenticate, identity
)  # JWT will create /auth endpoint... that endpoint will return JWT token

api.add_resource(Zipcode, "/zipcode/<string:zipcode>")
api.add_resource(Campsite, "/campsite")
api.add_resource(CampsiteList, "/campsites/all")
api.add_resource(ZipcodeList, "/zipcodes")
api.add_resource(TravelTime, "/traveltime")
api.add_resource(TravelTimeList, "/traveltimes")
api.add_resource(TravelTimeByZipList, "/traveltimes/<string:zipcode>")
api.add_resource(CampsiteByZipList, "/campsites/<string:zipcode>")
api.add_resource(UserRegister, "/register")
api.add_resource(WeatherForecastList, "/forecasts/all")
api.add_resource(WeatherForecastForCampsite, "/forecast/<int:campsite_id>")


# conditional ensures that app is only run when we run app.py, and not if/when we import it to another file
# only the file you directly run is __main__
if __name__ == "__main__":
    db.init_app(app)
    app.run(port=5000, debug=True)
