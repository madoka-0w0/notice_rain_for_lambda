import json
from urllib.parse import urlencode
from urllib.request import urlopen

import settings

INTERVAL = settings.interval()
MAP_ZOOM = settings.weather_map_zoom()


class WeatherClient:
    BASE_URL = "http://weather.olp.yahooapis.jp/v1/place"
    MAP_URL = "https://weather.yahoo.co.jp/weather/zoomradar/"

    def __init__(self, app_id):
        """

        :param app_id: your YOLP app_id
        :type app_id: str
        """
        self.app_id = app_id

    def weather_info(self, coordinates):
        """
        :param coordinates: tuple(longitude, latitude)
        :type coordinates: tuple[float]
        :return:
        """
        url = "{}?{}".format(self.BASE_URL, urlencode({
            "appid": self.app_id,
            "coordinates": "{},{}".format(*coordinates),
            "output": "json",
            "interval": INTERVAL
        }))
        with urlopen(url) as res:
            return json.loads(res.read().decode('utf-8'))

    @staticmethod
    def map_url(coordinates):
        """
        :param coordinates: tuple(longitude, latitude)
        :type coordinates: tuple[float]
        :return:
        """
        if len(coordinates) != 2:
            raise RuntimeError("coordinates must be (longitude, latitude)")
        url = "{}?{}".format(WeatherClient.MAP_URL, urlencode({
            "lon": coordinates[0],
            "lat": coordinates[1],
            "z": MAP_ZOOM
        }))
        return url


def filter_weathers(weather_info, func):
    """

    :param weather_info: WeatherClient.weather_infoより取得したdict
    :param func: filter条件
    :return:
    """
    weathers = weather_info["Feature"][0]["Property"]["WeatherList"]["Weather"]
    return list(filter(func, weathers))
