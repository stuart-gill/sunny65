# 65 + Sunny

This app tells you where you go camping that has forecasted the weather you're looking for.

## Getting Started

To clone locally, naviagate to your preferred directory, then:

```
git clone git@github.com:stuart-gill/sunny65.git
```

Create a config.py file in the root Sunny65 directory, and enter your google maps api key and openweather api key

```
GMAPS_API_KEY = "your-key"
OPEN_WEATHER_API_KEY = "your-key"
```

### Prerequisites

If you want to access the database as it is being build or updated, I recommend DB Browser for SQLite. Download here:

```
https://sqlitebrowser.org/dl/
```

### Venv

If venv folder doesn't already exists, create virtual environment with

```
$virtualenv venv --python=python3.8.3
```

Then activate with

```
$source venv/bin/activate
```

Exit with

```
$deactivate
```

### Packages

Make sure you have numpy installed and accessible for Python 3. Numpy is used to calculate distances with lat/long coordinates

```
https://numpy.org/
```

### Installing

If you want to rebuild the database file (data.db), run in command line:

```
(venv)$python create_tables.py
```

When it prompts you if you want to build databases, type 'y' and hit enter

To run the main program, run in command line:

```
(venv)$python app.py
```

Once your locations are found, you can check the map of campsites that's been built:

```
(venv)$open where.html
```

### Most Useful API endpoints

`POST /forecasts/all`
gets updated forecast for every campsite from open weather api, saves to db
`POST /traveltimes/<zipcode> {"maximum_linear_distance": x}`
gets travel times for all campsites within x distance of zipcode from google distance api, saves them to db
`GET /traveltimes/<zipcode> {"willind_travel_time": x}`
returns travel times for every campsite within x seconds of zipcode. Each travel time includes information about the campsite itself as well as 5 days forcast for that campsite

CRUD endpoints for zipcodes, campsites, forecasts, and travel times all exist, but are less commonly used.

## Authors

- **Stuart Gill**

## License

This project is licensed under the MIT License
