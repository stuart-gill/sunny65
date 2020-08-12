import csv
import sqlite3

import numpy as np

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
        lng    DECIMAL(9,5) NOT NULL
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


database_build = input("do you want to rebuild databases? y/n: \n")
if database_build == "y":
    build_campsite_database()
    build_zip_database()
    print("Databases built")
