import json
import sqlite3
import csv

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
  origin_lat = float(input("enter destination lat: "))
  origin_lng = float(input("enter destination lng: "))
  cur.execute('''SELECT * FROM Campsite WHERE lat - ? < 2 AND lng - ? < 2''',(origin_lat,origin_lng))
  destination_id = cur.fetchone()[0]
  print(destination_id)

