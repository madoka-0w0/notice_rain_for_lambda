from urllib.request import urlopen
from urllib.parse import urlencode
import json


class WeatherClient:
    BASE_URL = "http://weather.olp.yahooapis.jp/v1/place"

    def __init__(self, app_id, coordinates):
        """

        :param app_id: your YOLP app_id
        :param coordinates: tuple(longitude, latitude)
        :type app_id: str
        :type coordinates: tuple[float]
        """
        self.app_id = app_id
        self.coordinates = coordinates

    def get(self):
        url = "{}?{}".format(self.BASE_URL, urlencode({
            "appid": self.app_id,
            "coordinates": "{},{}".format(*self.coordinates),
            "output": "json",
            "interval": 5
        }))
        with urlopen(url) as res:
            return json.loads(res.read().decode('utf-8'))
