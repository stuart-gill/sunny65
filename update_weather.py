import requests
import time

campsite_ids = []

serviceurl = "https://sgill.dev/campsites/all"
response = requests.get(serviceurl)
js = response.json()
for campsite in js["campsites"]:
    campsite_ids.append(campsite["id"])


for campsite_id in campsite_ids:
    serviceurl = f"https://sgill.dev/forecast/{campsite_id}"
    response = requests.post(serviceurl)
    print(response.json())
    time.sleep(1.1)
