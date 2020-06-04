import json
import sqlite3
import csv
import numpy as np

# build and initialize sqlite database of destinations
# using csv from http://www.uscampgrounds.info/takeit.html

# READ CSV, build Camping table
def build_database(): 
    conn = sqlite3.connect('sunny65_db.sqlite')
    cur = conn.cursor()
    cur.executescript('''
    DROP TABLE IF EXISTS Campsite;
    DROP TABLE IF EXISTS State;

    CREATE TABLE Campsite (
        id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        name   TEXT UNIQUE NOT NULL,
        lat    DECIMAL(9,6) NOT NULL,
        lng    DECIMAL(9,6) NOT NULL,
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

def set_weather_url(url,ID):
    conn = sqlite3.connect('sunny65_db.sqlite')
    cur = conn.cursor()
    cur.execute('''UPDATE Campsite SET weather_url = ? WHERE id = ?''',(url, ID) )
    conn.commit()



