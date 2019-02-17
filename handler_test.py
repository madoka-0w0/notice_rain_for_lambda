from unittest import TestCase
from unittest.mock import Mock

from handler import ApplicationRunner, is_raining, create_raining_message


class TestHandler(TestCase):
    def test_main(self):
        weather_client = Mock()
        weather_client.weather_info.return_value = {
            "Feature": [
                {
                    "Property": {
                        "WeatherList": {
                            "Weather": [
                                {
                                    "Date": "201912222030",
                                    "Type": "observation",
                                    "Rainfall": 10.0
                                },
                                {
                                    "Date": "201812222040",
                                    "Type": "observation",
                                    "Rainfall": 0.0
                                },
                                {
                                    "Date": "201812222050",
                                    "Type": "observation",
                                    "Rainfall": 0.0
                                },
                                {
                                    "Date": "201812222100",
                                    "Type": "observation",
                                    "Rainfall": 0.0
                                },
                                {
                                    "Date": "201812222110",
                                    "Type": "observation",
                                    "Rainfall": 0.0
                                },
                                {
                                    "Date": "201812222120",
                                    "Type": "observation",
                                    "Rainfall": 0.0
                                },
                                {
                                    "Date": "201812222130",
                                    "Type": "observation",
                                    "Rainfall": 0.0
                                },
                                {
                                    "Date": "201812222140",
                                    "Type": "forecast",
                                    "Rainfall": 0.0
                                },
                                {
                                    "Date": "201812222150",
                                    "Type": "forecast",
                                    "Rainfall": 0.0
                                },
                                {
                                    "Date": "201812222200",
                                    "Type": "forecast",
                                    "Rainfall": 0.0
                                },
                                {
                                    "Date": "201812222210",
                                    "Type": "forecast",
                                    "Rainfall": 0.0
                                },
                                {
                                    "Date": "201812222220",
                                    "Type": "forecast",
                                    "Rainfall": 0.0
                                },
                                {
                                    "Date": "201812222230",
                                    "Type": "forecast",
                                    "Rainfall": 0.0
                                }
                            ]
                        },
                    }
                }
            ]
        }
        weather_client.map_url.return_value = ""

        user = Mock()
        user.id = 1
        user.slack_url = ""
        user.need_send_slack = True
        user.latitude = 10
        user.longitude = 100

        app = ApplicationRunner(user, weather_client, Mock(), lambda i, b: None)
        app.run()

    def test_is_raining(self):
        from datetime import datetime
        self.assertTrue(is_raining(
            {
                "Date": "201812222030",
                "Type": "observation",
                "Rainfall": 10.0
            }, compare_date=datetime(2018, 12, 22, 20, 40)))
        self.assertFalse(is_raining(
            {
                "Date": "201812222030",
                "Type": "observation",
                "Rainfall": 10.0
            }, compare_date=datetime(2018, 12, 22, 20, 41)))
        self.assertTrue(is_raining(
            {
                "Date": "201812222230",
                "Type": "forecast",
                "Rainfall": 10.0
            }, compare_date=datetime(2018, 12, 22, 20, 41)))

    def test_create_message(self):
        import settings
        self.assertEqual(settings.message_raining(),
                         create_raining_message(
                             [
                                 {
                                     "Date": "201812222030",
                                     "Type": "observation",
                                     "Rainfall": 10.0
                                 },
                             ]))
        self.assertEqual(settings.message_forecast_raining().format("22:30"),
                         create_raining_message([
                             {
                                 "Date": "201812222230",
                                 "Type": "forecast",
                                 "Rainfall": 10.0
                             }]))
        self.assertEqual("", create_raining_message([]))
