import json
import sqlite3
import csv
import numpy as np

# build and initialize sqlite database of destinations
# using csv from http://www.uscampgrounds.info/takeit.html

# TODO: add weather column for forecast, and weather_updated column for time
# TODO: add zip-code table, and zip-code <=> destination join table many to many to list drive times
# TODO: 

# READ CSV, build Camping table
def build_campsite_database(): 
    conn = sqlite3.connect('sunny65_db.sqlite')
    cur = conn.cursor()
    cur.executescript('''
    DROP TABLE IF EXISTS Campsite;
    DROP TABLE IF EXISTS State;
    DROP TABLE IF EXISTS Zipcode;

    CREATE TABLE Campsite (
        id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        name   TEXT UNIQUE NOT NULL,
        lat    DECIMAL(9,6) NOT NULL,
        lng    DECIMAL(9,5) NOT NULL,
        state_id INTEGER NOT NULL, 
        weather_url TEXT 
    );

    CREATE TABLE State (
        id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        name   TEXT UNIQUE
    );
    ''')


    fname = input('Enter file name: ')
    if len(fname) < 1:
        fname = 'WestCamp.csv'

    # str_data = open(fname).read()
    # json_data = json.loads(str_data)

    with open(fname, newline='', errors='ignore') as csvfile:
        campsite_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in campsite_reader:
            name = row[4]
            lat = row[1]
            lng = row[0]
            state = row[12]
            # print((name, lat, lng))
        
            cur.execute('''INSERT OR IGNORE INTO State (name)
            VALUES (?) ''', (state, ))
        
            cur.execute('SELECT id FROM State WHERE name = ? ', (state, ))
            state_id = cur.fetchone()[0]

            cur.execute('''INSERT OR IGNORE INTO Campsite (name, lat, lng, state_id)
            VALUES ( ?, ?, ?, ?)''', ( name, lat, lng, state_id) )

            conn.commit()

def build_zip_database():
    conn = sqlite3.connect('sunny65_db.sqlite')
    cur = conn.cursor()
    cur.executescript('''
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
    ''')

    fname = input('Enter file name: ')
    if len(fname) < 1:
        fname = 'us-zip-code-latitude-and-longitude.csv'

    # str_data = open(fname).read()
    # json_data = json.loads(str_data)

    with open(fname, newline='', errors='ignore') as csvfile:
        zipcode_reader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in zipcode_reader:
            zipcode = row[0]
            lat = row[3]
            lng = row[4]
            # print((name, lat, lng))

            cur.execute('''INSERT OR IGNORE INTO Zipcode (zipcode, lat, lng)
            VALUES ( ?, ?, ?)''', ( zipcode, lat, lng) )

            conn.commit()

def set_weather_url(url,ID):
    conn = sqlite3.connect('sunny65_db.sqlite')
    cur = conn.cursor()
    cur.execute('''UPDATE Campsite SET weather_url = ? WHERE id = ?''',(url, ID) )
    conn.commit()

def set_travel_time(origin_zipcode, campsite_id, seconds):
    conn = sqlite3.connect('sunny65_db.sqlite')
    cur = conn.cursor()
    cur.execute('SELECT id FROM Zipcode WHERE zipcode = ? ', (origin_zipcode, ))
    zipcode_id = cur.fetchone()[0]
    cur.execute('''INSERT OR REPLACE INTO Travel_Time
    (zipcode_id, campsite_id, duration, last_updated) VALUES ( ?, ?, ?, datetime('now') )''',
    ( zipcode_id, campsite_id, seconds ) )
    conn.commit()

def get_travel_time(origin_zipcode, campsite_id):
    conn = sqlite3.connect('sunny65_db.sqlite')
    cur = conn.cursor()
    cur.execute('SELECT id FROM Zipcode WHERE zipcode = ? ', (origin_zipcode, ))
    zipcode_id = cur.fetchone()[0]
    cur.execute('SELECT duration FROM Travel_Time WHERE zipcode_id = zipcode_id AND campsite_id = campsite_id')
    duration = cur.fetchone()[0]
    return duration

