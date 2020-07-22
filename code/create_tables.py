import csv
import sqlite3

import numpy as np


class Campsite:
    def __init__(
        self,
        campsite_id: int,
        name: str,
        lat: float,
        lng: float,
        state: str,
        weather_url: str = None,
        weather_forecast: str = None,
        duration: int = None,
    ):
        self.campsite_id = campsite_id
        self.name = name
        self.lat = lat
        self.lng = lng
        self.state = state
        self.weather_url = weather_url
        self.weather_forecast = weather_forecast
        self.duration = duration

    def __str__(self):
        return f"{self.campsite_id}, {self.name}, {self.state}"  # .format(self.campsite_id, self.name, self.state)

    def __repr__(self):
        return f"<Campsite({self.campsite_id}, '{self.name}', {self.lat}, {self.lng}, {self.state}, '{self.weather_url}', '{self.weather_forecast}', {self.duration}>"


# build and initialize sqlite database of destinations
# using csv from http://www.uscampgrounds.info/takeit.html
# currently just western campsites

# READ CSV, build Camping table
def build_campsite_database():
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.executescript(
        """
    DROP TABLE IF EXISTS campsites;

    CREATE TABLE campsites (
        id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        name   TEXT UNIQUE NOT NULL,
        lat    DECIMAL(9,6) NOT NULL,
        lng    DECIMAL(9,5) NOT NULL,
        weather_url TEXT,
        weather_forecast TEXT
    );

    """
    )

    fname = input("Enter file name or hit enter for default WestCamp.csv: ")
    if len(fname) < 1:
        fname = "WestCamp.csv"

    with open(fname, newline="", errors="ignore") as csvfile:
        campsite_reader = csv.reader(csvfile, delimiter=",", quotechar="|")
        for row in campsite_reader:
            name = row[4]
            lat = row[1]
            lng = row[0]

            cur.execute(
                """INSERT OR IGNORE INTO campsites (name, lat, lng)
            VALUES ( ?, ?, ?)""",
                (name, lat, lng),
            )

            conn.commit()
    conn.close()
    print("campsites database built, connection closed")


def build_zip_database():
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.executescript(
        """
    DROP TABLE IF EXISTS zipcodes;

    CREATE TABLE zipcodes (
        id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        zipcode    INTEGER UNIQUE NOT NULL,
        lat    DECIMAL(9,6) NOT NULL,
        lng    DECIMAL(9,5) NOT NULL
    );

    """
    )

    default_fname = "us-zip-code-latitude-and-longitude.csv"
    fname = input(f"Enter file name, or hit enter for default {default_fname}: ")
    if len(fname) < 1:
        fname = default_fname

    # str_data = open(fname).read()
    # json_data = json.loads(str_data)

    with open(fname, newline="", errors="ignore") as csvfile:
        zipcode_reader = csv.reader(csvfile, delimiter=";", quotechar="|")
        for row in zipcode_reader:
            zipcode = row[0]
            lat = row[3]
            lng = row[4]

            cur.execute(
                """INSERT OR IGNORE INTO zipcodes (zipcode, lat, lng)
            VALUES ( ?, ?, ?)""",
                (zipcode, lat, lng),
            )

            conn.commit()
    conn.close()
    print("zipcodes database built, connection closed")


def set_weather_url(url, ID):
    conn = sqlite3.connect("sunny65_db.sqlite")
    cur = conn.cursor()
    cur.execute("""UPDATE Campsite SET weather_url = ? WHERE id = ?""", (url, ID))
    conn.commit()


def set_weather_forecast(forecast, campsite_id):
    print(f"set weather run with id= {campsite_id}")
    conn = sqlite3.connect("sunny65_db.sqlite")
    cur = conn.cursor()
    cur.execute(
        """
    UPDATE Campsite
    SET 
        weather_forecast = ?,
        forecast_last_updated = datetime('now')
    WHERE 
        id = ?
        """,
        (forecast, campsite_id),
    )
    conn.commit()


def get_weather_forecast(campsite_id):
    """get forecast from database if it's less than an hour old"""
    conn = sqlite3.connect("sunny65_db.sqlite")
    cur = conn.cursor()
    cur.execute(
        """
    SELECT weather_forecast
    FROM Campsite
    WHERE 
        id = ?
        AND
        (julianday('now') - julianday(forecast_last_updated))*24 < 1
        """,
        (campsite_id,),
    )
    forecast = cur.fetchone()
    if forecast:
        return forecast[0]
    else:
        return None


def set_travel_time(origin_zipcode, campsite_id, seconds):
    conn = sqlite3.connect("sunny65_db.sqlite")
    cur = conn.cursor()
    cur.execute("SELECT id FROM Zipcode WHERE zipcode = ? ", (origin_zipcode,))
    zipcode_id = cur.fetchone()[0]
    cur.execute(
        """
        INSERT OR REPLACE INTO Travel_Time
        (zipcode_id, campsite_id, duration)
        VALUES ( ?, ?, ? )
        """,
        (zipcode_id, campsite_id, seconds),
    )
    conn.commit()


def get_travel_time(origin_zipcode, campsite_id):
    """Gets travel time for a single zipcode->campsite trip"""

    conn = sqlite3.connect("sunny65_db.sqlite")
    cur = conn.cursor()
    cur.execute("SELECT id FROM Zipcode WHERE zipcode = ? ", (origin_zipcode,))
    zipcode_id = cur.fetchone()[0]
    cur.execute(
        "SELECT duration FROM Travel_Time WHERE zipcode_id = ? AND campsite_id = ?",
        (zipcode_id, campsite_id),
    )
    duration = cur.fetchone()
    if duration:
        return duration[0]
    else:
        return None


def get_distance_filtered_locs(origin_zipcode, acceptable_distance):
    """Fetches campsites that are within a certain radius of the origin lat/long
    also adds duration column, with travel duration in seconds from origin_zipcode to each campsite,
     which may or may not be in database"""

    conn = sqlite3.connect("data.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT id, lat, lng FROM zipcodes WHERE zipcode = ? ", (origin_zipcode,)
    )
    zipcode_id, origin_lat, origin_lng = cur.fetchone()
    # zipcode_id = cur.fetchone()[0]
    # origin_lat = cur.fetchone()[1]
    # origin_lng = cur.fetchone()[2]

    EARTH_RADIUS = 3960
    max_lat = origin_lat + np.rad2deg(acceptable_distance / EARTH_RADIUS)
    min_lat = origin_lat - np.rad2deg(acceptable_distance / EARTH_RADIUS)

    max_lng = origin_lng + np.rad2deg(
        acceptable_distance / EARTH_RADIUS / np.cos(np.deg2rad(origin_lat))
    )
    min_lng = origin_lng - np.rad2deg(
        acceptable_distance / EARTH_RADIUS / np.cos(np.deg2rad(origin_lat))
    )

    cur.execute(
        """
    SELECT
        campsites.id,
        campsites.name,
        campsites.lat,
        campsites.lng,
        campsites.weather_url
    FROM
        campsites
    WHERE
        campsites.lat BETWEEN ? AND ? AND campsites.lng BETWEEN ? AND ?
        """,
        (min_lat, max_lat, min_lng, max_lng),
    )
    fetched = cur.fetchall()

    print("fetched: ", fetched)
    return fetched


def distance_matrix(zipcode, distance_filtered_locs):
    """Checks distance filterd locs array of dicts for locs without travel times.
    Those travel times will be added to list to be sent to google distance matrix.
    The travel durations found (in seconds) will be added to the database and to
    the distance_filtered_locs array of dictionaries.
    Args:
        zipcode: integer, origin zipcode
        distance_filtered_locs: list of dicts with information about potential destinations
    Returns:
        void
  """

    api_key = config.GMAPS_API_KEY
    serviceurl = "https://maps.googleapis.com/maps/api/distancematrix/json?"

    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    locs_sans_durations = []
    durations_from_api = []

    # TODO: set an expiration on durations in the database?

    locs_sans_durations = [
        loc for loc in distance_filtered_locs if not loc["travel_time"]
    ]

    print("locs sans durations: ", locs_sans_durations)

    iterations = math.ceil(len(locs_sans_durations) / 25)
    print("\n\n ITERATIONS: ", iterations, "\n\n")

    for i in range(iterations):
        # Add each potential destination to destinations parameter using encoded
        # polyline: https://developers.google.com/maps/documentation/utilities/polylinealgorithm
        destinations_parm = ""
        destinations_list = []
        for loc in locs_sans_durations[(i * 25) : ((i + 1) * 25)]:
            loc_tuple = (loc["lat"], loc["lng"])
            destinations_list.append(loc_tuple)
        print(destinations_list)
        destinations_parm = "enc:" + polyline.encode(destinations_list) + ":"

        # Build the rest of the api call
        parms = dict()
        parms["origins"] = zipcode
        parms["destinations"] = destinations_parm
        parms["key"] = api_key
        url = serviceurl + urllib.parse.urlencode(parms)

        # GET LOCATIONS FROM GOOGLE DISTANCE MATRIX
        print("Retrieving", url)
        url_handle = urllib.request.urlopen(url, context=ctx)
        data = url_handle.read().decode()
        print("Retrieved", len(data), "characters")

        try:
            locations_json = json.loads(data)
        except:
            locations_json = None

        if (
            not locations_json
            or "status" not in locations_json
            or locations_json["status"] != "OK"
        ):
            print("==== Failure To Retrieve ====")
            print(data)

        print(json.dumps(locations_json, indent=4))
        elements = locations_json["rows"][0]["elements"]
        for element in elements:
            if element["status"] == "OK":
                durations_from_api.append(element["duration"]["value"])
            else:
                durations_from_api.append(-1)

        for j in range(i * 25, (i + 1) * 25):
            # to prevent out of range error
            if j < len(locs_sans_durations):
                campsite_id = locs_sans_durations[j]["ID"]
                travel_time = durations_from_api[j]
                set_travel_time(zipcode, campsite_id, travel_time)
                locs_sans_durations[j]["travel_time"] = durations_from_api[j]


# database_build = input("do you want to rebuild databases? y/n: \n")
# if database_build == "y":
#     build_campsite_database()
#     build_zip_database()
#     print("Databases built")


get_distance_filtered_locs(98122, 20)

