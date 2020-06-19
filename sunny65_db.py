import csv
import sqlite3

import numpy as np

# build and initialize sqlite database of destinations
# using csv from http://www.uscampgrounds.info/takeit.html
# currently just western campsites


# READ CSV, build Camping table
def build_campsite_database():
    conn = sqlite3.connect("sunny65_db.sqlite")
    cur = conn.cursor()
    cur.executescript(
        """
    DROP TABLE IF EXISTS Campsite;
    DROP TABLE IF EXISTS State;

    CREATE TABLE Campsite (
        id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        name   TEXT UNIQUE NOT NULL,
        lat    DECIMAL(9,6) NOT NULL,
        lng    DECIMAL(9,5) NOT NULL,
        state_id INTEGER NOT NULL, 
        weather_url TEXT,
        weather_forecast TEXT,
        forecast_last_updated TEXT
    );

    CREATE TABLE State (
        id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        name   TEXT UNIQUE
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
            state = row[12]

            cur.execute(
                """INSERT OR IGNORE INTO State (name)
            VALUES (?) """,
                (state,),
            )

            cur.execute("SELECT id FROM State WHERE name = ? ", (state,))
            state_id = cur.fetchone()[0]

            cur.execute(
                """INSERT OR IGNORE INTO Campsite (name, lat, lng, state_id)
            VALUES ( ?, ?, ?, ?)""",
                (name, lat, lng, state_id),
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


def set_weather_url(url, campsite_id):
    conn = sqlite3.connect("sunny65_db.sqlite")
    cur = conn.cursor()
    cur.execute(
        """UPDATE Campsite SET weather_url = ? WHERE id = ?""", (url, campsite_id)
    )
    conn.commit()


def set_weather_forecast(forecast, campsite_id):
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
        Campsite.weather_url,
        duration
    FROM
        Campsite
    LEFT JOIN Travel_Time ON
        Campsite.id = Travel_Time.campsite_id AND
        Travel_Time.zipcode_id = ?
    WHERE
        Campsite.lat BETWEEN ? AND ? AND Campsite.lng BETWEEN ? AND ?
        """,
        (zipcode_id, min_lat, max_lat, min_lng, max_lng),
    )
    fetched = cur.fetchall()
    return fetched


# database_build = input("do you want to rebuild databases? y/n: \n")
# if database_build == 'y':
#   build_campsite_database()
#   build_zip_database()
#   print("Databases built")

# set_weather_forecast("it's gonna rain", 1)
# print(get_weather_forecast('1'))
