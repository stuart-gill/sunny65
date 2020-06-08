# 65 + Sunny

This app tells you where you go camping that has forecasted the weather you're looking for.

## Getting Started

To clone locally, naviagate to your preferred directory, then:

```
git clone git@github.com:stuart-gill/sunny65.git
```

Create a config.py file in the root Sunny65 directory, and enter your google maps api key here, or ask me for mine

```
GMAPS_API_KEY = "your-key"
```

### Prerequisites

If you want to access the database as it is being build or updated, I recommend DB Browser for SQLite. Download here:

```
https://sqlitebrowser.org/dl/
```

Make sure you have numpy installed and accessible for Python 3. Numpy is used to calculate distances with lat/long coordinates

```
https://numpy.org/
```

### Installing

If you want to rebuild the database file (sunny65_db.sqlite), run in command line:

```
$python3 sunny65_db.py
```

When it prompts you if you want to build databases, type 'y' and hit enter

To run the main program, run in command line:

```
$python3 sunny65.py
```

Once your locations are found, you can check the map of campsites that's been built:

```
$open where.html
```

## Authors

- **Stuart Gill**

## License

This project is licensed under the MIT License
