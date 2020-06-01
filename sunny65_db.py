import json
import sqlite3
import csv
import numpy as np

# build and initialize sqlite database of destinations, using local json file to seed 
# what other tables would be needed? users; states; users-destinations join table; 



conn = sqlite3.connect('sunny65_db.sqlite')
cur = conn.cursor()

# READ JSON, build destinations table
cur.executescript('''
DROP TABLE IF EXISTS Destination;

CREATE TABLE Destination (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name   TEXT UNIQUE,
    lat    DECIMAL(9,6),
    lng    DECIMAL(9,6)
);
''')

fname = input('Enter file name: ')
if len(fname) < 1:
    fname = 'sunny65.json'


str_data = open(fname).read()
json_data = json.loads(str_data)

for entry in json_data:

    name = entry["name"];
    lat = entry["lat"];
    lng = entry["lng"];

    print((name, lat, lng))

    cur.execute('''INSERT OR IGNORE INTO Destination (name, lat, lng)
        VALUES ( ?, ?, ? )''', ( name, lat, lng ) )
    cur.execute('SELECT id FROM Destination WHERE name = ? ', (name, ))
    destination_id = cur.fetchone()[0]

    conn.commit()

# READ CSV, build Camping table
cur.executescript('''
DROP TABLE IF EXISTS Campsite;
DROP TABLE IF EXISTS State;

CREATE TABLE Campsite (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name   TEXT UNIQUE NOT NULL,
    lat    DECIMAL(9,6) NOT NULL,
    lng    DECIMAL(9,6) NOT NULL,
    state_id INTEGER NOT NULL
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

while True:
  origin_lat = input("enter destination lat: ")
  if len(origin_lat) < 1:
    origin_lat = 47.6062
  origin_lng = input("enter destination lng: ")
  if len(origin_lng) < 1:
    origin_lng = -122.3321
  acceptable_distance = int(input("enter acceptable distance: "))
  EARTH_RADIUS = 3960
  max_lat = origin_lat + np.rad2deg(acceptable_distance/EARTH_RADIUS)
  min_lat = origin_lat - np.rad2deg(acceptable_distance/EARTH_RADIUS)

  print(max_lat)
  print(min_lat)

  max_lng = origin_lng + np.rad2deg(acceptable_distance/EARTH_RADIUS/np.cos(np.deg2rad(origin_lat)));
  min_lng = origin_lng - np.rad2deg(acceptable_distance/EARTH_RADIUS/np.cos(np.deg2rad(origin_lat)));

  cur.execute('''SELECT * FROM Campsite WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?''',(min_lat, max_lat, min_lng, max_lng))
  fetched = cur.fetchall()
  print(fetched)

