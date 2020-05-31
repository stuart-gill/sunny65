import json
import sqlite3

# build and initialize sqlite database of destinations, using local json file to seed 
# what other tables would be needed? users; states; users-destinations join table; 

conn = sqlite3.connect('sunny65_db.sqlite')
cur = conn.cursor()

# Do some setup
cur.executescript('''
DROP TABLE IF EXISTS Destinations;

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
