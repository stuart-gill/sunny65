import csv
import sqlite3

# import numpy as np


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


def build_zip_database():
    conn = sqlite3.connect("sunny65_db.sqlite")
    cur = conn.cursor()
    cur.executescript(
        """
    DROP TABLE IF EXISTS Zipcode;
    DROP TABLE IF EXISTS Travel_Time;

    CREATE TABLE Zipcode (
        id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        zipcode    INTEGER UNIQUE NOT NULL,
        lat    DECIMAL(9,6) NOT NULL,
        lng    DECIMAL(9,5) NOT NULL
    );

    CREATE TABLE Travel_Time (
        zipcode_id    INTEGER,
        campsite_id   INTEGER,
        duration      INTEGER,
        last_updated  TEXT,
        PRIMARY KEY (zipcode_id, campsite_id)
    );
    """
    )

    fname = input("Enter file name, or hit enter for default: ")
    if len(fname) < 1:
        fname = "us-zip-code-latitude-and-longitude.csv"

    # str_data = open(fname).read()
    # json_data = json.loads(str_data)

    with open(fname, newline="", errors="ignore") as csvfile:
        zipcode_reader = csv.reader(csvfile, delimiter=";", quotechar="|")
        for row in zipcode_reader:
            zipcode = row[0]
            lat = row[3]
            lng = row[4]

            cur.execute(
                """INSERT OR IGNORE INTO Zipcode (zipcode, lat, lng)
            VALUES ( ?, ?, ?)""",
                (zipcode, lat, lng),
            )

            conn.commit()


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
        (zipcode_id, campsite_id, duration, last_updated)
        VALUES ( ?, ?, ?, datetime('now') )
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


def get_distance_filtered_locs(
    origin_lat, origin_lng, origin_zipcode, acceptable_distance
):
    """Fetches campsites that are within a certain radius of the origin lat/long
    also adds duration column, with travel duration in seconds from origin_zipcode to each campsite,
     which may or may not be in database"""

    conn = sqlite3.connect("sunny65_db.sqlite")
    cur = conn.cursor()

    cur.execute("SELECT id FROM Zipcode WHERE zipcode = ? ", (origin_zipcode,))
    zipcode_id = cur.fetchone()[0]

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
        Campsite.id,
        Campsite.name,
        Campsite.lat,
        Campsite.lng,
        State.name,
        Campsite.weather_url,
        Travel_Time.duration
    FROM
        Campsite
    LEFT JOIN Travel_Time ON
        Campsite.id = Travel_Time.campsite_id AND
        Travel_Time.zipcode_id = ?
    LEFT JOIN State ON
        Campsite.state_id = State.id
    WHERE
        Campsite.lat BETWEEN ? AND ? AND Campsite.lng BETWEEN ? AND ?
        """,
        (zipcode_id, min_lat, max_lat, min_lng, max_lng),
    )
    fetched = cur.fetchall()

    # try building out class based campsite objects
    campsites = [
        Campsite(campsite_id, name, lat, lng, state, weather_url, duration)
        for (campsite_id, name, lat, lng, state, weather_url, duration) in fetched
    ]
    for campsite in campsites:
        print(campsite)
    # for campsite_tuple in fetched:
    #     campsite_id, name, lat, lng, weather_url, duration, state = campsite_tuple
    #     campsite = Campsite(campsite_id, name, lat, lng, state, weather_url, duration)
    #     print(campsite)
    return fetched


database_build = input("do you want to rebuild databases? y/n: \n")
if database_build == "y":
    build_campsite_database()
    #   build_zip_database()
    print("Databases built")

# set_weather_forecast("it's gonna rain", 1)
# print(get_weather_forecast('1'))

