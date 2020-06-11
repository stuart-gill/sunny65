import requests


def geocode(locale):
    """fetch lat, long, and zipcode for a location
    Currently using url from Python for Everybody course, probably need to change that
    args:
        locale: string, can be address or zip code or institution (like Univeristy of Washington), but not city name unless city has only one zip code
    """

    api_key = False
    if api_key is False:
        api_key = 42
        serviceurl = "http://py4e-data.dr-chuck.net/json"
    else:
        serviceurl = "https://maps.googleapis.com/maps/api/geocode/json"

    address_data = {"address": locale, "key": 42}
    response = requests.get(serviceurl, params=address_data)
    print("retrieving", response.url)
    text = response.text
    print("received ", len(text), " characters")
    js = response.json()

    if not js or "status" not in js or js["status"] != "OK":
        print("==== Failure To Retrieve ====")
        print(response.text)
        return (None, None, None)

    lat = js["results"][0]["geometry"]["location"]["lat"]
    lng = js["results"][0]["geometry"]["location"]["lng"]

    # location of zipcode in json varies depending on what kind of address is input...
    # this seems to catch most cases
    zipcode = None
    for component in js["results"][0]["address_components"]:
        if component["types"][0] == "postal_code":
            zipcode = component["short_name"]

    return (lat, lng, zipcode)
