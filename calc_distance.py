import json
import sqlite3
import csv
import numpy as np



def calc_distance(origin_lat, origin_lng, acceptable_distance):
  # origin_lat = input("enter destination lat: ")
  # if len(origin_lat) < 1:
  #   origin_lat = 47.6062
  # origin_lng = input("enter destination lng: ")
  # if len(origin_lng) < 1:
  #   origin_lng = -122.3321
  # acceptable_distance = int(input("enter acceptable distance: "))

  conn = sqlite3.connect('sunny65_db.sqlite')
  cur = conn.cursor()
  EARTH_RADIUS = 3960
  max_lat = origin_lat + np.rad2deg(acceptable_distance/EARTH_RADIUS)
  min_lat = origin_lat - np.rad2deg(acceptable_distance/EARTH_RADIUS)

  print(max_lat)
  print(min_lat)

  max_lng = origin_lng + np.rad2deg(acceptable_distance/EARTH_RADIUS/np.cos(np.deg2rad(origin_lat)));
  min_lng = origin_lng - np.rad2deg(acceptable_distance/EARTH_RADIUS/np.cos(np.deg2rad(origin_lat)));

  cur.execute('''SELECT * FROM Campsite WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?''',(min_lat, max_lat, min_lng, max_lng))
  fetched = cur.fetchall()
  return(fetched)
