import json
from OSMPythonTools.nominatim import Nominatim
import folium
import requests

img_src = "https://media.istockphoto.com/videos/navigation-map-and-red-checkpoint-icon-loop" \
          "-animation-on-white-4k-video-id1182644412?s=640x640"
url = "https://gisn.tel-aviv.gov.il/arcgis/rest/services/IView2/MapServer" \
      "/970/query?where=1%3D1&outFields=*&f=json"


def login():
    response = requests.get(url=url)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print(f"[Error : {response.status_code}]")
        return None


def getCoordinates(name):
    nominatim = Nominatim()
    location = nominatim.query(name, wkt=True)
    info = location.toJSON()
    for item in info:
        return float(item['lat']),  float(item['lon'])
    return info


def getDetails(data):
    details = []
    features = data["features"]
    for attr in features:
        loc = {}
        loc["shem_chenyon"] = attr["attributes"]["shem_chenyon"]
        loc["ktovet"] = attr["attributes"]["ktovet"]
        loc["status_chenyon"] = attr["attributes"]["status_chenyon"]
        loc["location"] = getCoordinates(str(attr["attributes"]["ktovet"]))
        details.append(loc)
    return details


def mapping(details):
    ls = []
    for element in details:
        status = element["status_chenyon"]
        name = element['ktovet']
        loc = list(element["location"])
        curr = {"status": status, "loc": loc, "name": name}
        if loc:
            ls.append(curr)
    if ls:
        m = folium.Map(location=ls[0]['loc'], tiles="OpenStreetMap", zoom_start=12)
        for d in ls:
            if d['status'] in ['פנוי', 'פעיל']:
                color = 'green'
            elif d['status'] in ['מעט']:
                color = 'orange'
            elif d['status'] in ['מעט', 'סגור', 'מלא']:
                color = 'red'
            else:
                color = 'black'
                d['status'] = 'לא קיים'
            folium.Marker(
                location=d['loc'],
                icon=folium.Icon(icon_color=color),
                tooltip=d['status']
            ).add_to(m)
        m.save('map.html')


if __name__ == '__main__':
    data = login()
    details = getDetails(data)
    mapping(details)
