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

### Digital Ocean

SSH into digital ocean with

```
ssh stuart@128.199.0.88
```

128.199.0.88 is the IP address of the api.
Type $sudo su to access superuser
Type $psql as user stuart to connect to Postgres database which is named "stuart"
Type $\conninfo for info about the database
Type $\q to quit the Postgres terminal
vi /etc/postgresql/9.5/main/pg_hba.conf to modify Postgres login settings (login must be with MD5 password. Already did this. SQLAlchemy won't work without it).
also using NGINX... communicates with UWSGI to allow multithreading
Type $sudo ufw status : to get info about what's allowed through the firewall 
$systemctl status nginx : to get info about nginx
$systemctl reload nginx : (or restart instead of reload. Reload is graceful restart. restart only when changing ports or interfaces)
Nginx config file is at /etc/nginx/sites-available/items-rest.conf (must type cd /etc or whatever, ls from ~ won't show anything)
This config also contains info about uwsgi stuff.
This config file is linked (soft) to /sites-available
The whole git repo is copied (cloned) into /var/www/html/items-rest
We also use a venv and install everything from the requirements.txt file in the venv
ENV variables about the uwsgi service are stored in this file: /etc/systemd/system/uwsgi_items_rest.service
This file also includes the run command (called ExecStart), Restart=always, KillSignal=SIGQUIT, Type=notify, NotifyAccess=all (notification parameters).  
This service is going to run uWSGI and uWSGI is going to run the Flask app.
5432 is the port Postgres typically runs on
The Install part of this file allows us to start the service when the server boots up.
The /var/www/html/items-rest/uwsgi.ini files are different between Heroku and Digital Ocean

The run.py file exists to make sure the database exists before we run the app.py file

socket.sock file is what allows communication between uwsgi file and NGINX

harakiri = 7000 is a long time (7000 seconds) before killing a process

To start the service, enter:

$sudo systemctl start uwsgi_items_rest

sudo systemctl reload nginx (to make it read config file)
sudo systemctl restart nginx
sudo systemctl start uwsgi_items_rest

POST /forecasts/all was running into a timeout issue (since open weather only allows 1 forecast a second)...
fixed this with

uwsgi_read_timeout 3600s;
uwsgi_send_timeout 3600s;

inserted in location section of etc/nginx/sites-available/items-rest.conf. This replaced proxy_read_timeout 3600; proxy_send_timeout 3600; which are nginx configurations-- apparently nginx doesn't allow settings longer than 60 seconds

### Most Useful API endpoints

```
POST /forecasts/all
```

gets updated forecast for every campsite from open weather api, saves to db

```
POST /traveltimes/<zipcode> {"maximum_linear_distance": x}
```

gets travel times for all campsites within x distance of zipcode from google distance api, saves them to db

```
GET /traveltimes/<zipcode> {"willind_travel_time": x}
```

returns travel times for every campsite within x seconds of zipcode. Each travel time includes information about the campsite itself as well as 5 days forcast for that campsite

CRUD endpoints for zipcodes, campsites, forecasts, and travel times all exist, but are less commonly used.

## Authors

- **Stuart Gill**

## License

This project is licensed under the MIT License
