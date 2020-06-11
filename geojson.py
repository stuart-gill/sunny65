import urllib.request, urllib.parse, urllib.error
import json
import ssl

api_key = False
# If you have a Google Places API key, enter it here
# api_key = 'AIzaSy___IDByT70'
# https://developers.google.com/maps/documentation/geocoding/intro


def geocode(locale):
    """fetch lat, long, and zipcode for a location
    Currently using url from Python for Everybody course, probably need to change that
    args: 
        locale: string, can be address or zip code or institution (like Univeristy of Washington), but not city name unless city has only one zip code
    """

    api_key = False
    if api_key is False:
        api_key = 42
        serviceurl = "http://py4e-data.dr-chuck.net/json?"
    else:
        serviceurl = "https://maps.googleapis.com/maps/api/geocode/json?"

    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # address = input('Enter location: ')

    parms = dict()
    parms["address"] = locale
    if api_key is not False:
        parms["key"] = api_key
    url = serviceurl + urllib.parse.urlencode(parms)

    print("Retrieving", url)
    uh = urllib.request.urlopen(url, context=ctx)
    data = uh.read().decode()
    print("Retrieved", len(data), "characters")

    try:
        js = json.loads(data)
    except:
        js = None

    if not js or "status" not in js or js["status"] != "OK":
        print("==== Failure To Retrieve ====")
        print(data)

    lat = js["results"][0]["geometry"]["location"]["lat"]
    lng = js["results"][0]["geometry"]["location"]["lng"]

    # location of zipcode in json varies depending on what kind of address is input... this seems to catch most cases
    zipcode = None
    for component in js["results"][0]["address_components"]:
        if component["types"][0] == "postal_code":
            zipcode = component["short_name"]

    return (lat, lng, zipcode)
