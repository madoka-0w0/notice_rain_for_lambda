from unittest import TestCase
from unittest.mock import Mock

from handler import UserRunner, is_raining, create_raining_message, MainRunner


class TestHandler(TestCase):
    def setUp(self):
        self.weather_client = Mock()
        self.weather_client.weather_info.return_value = {
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
        self.weather_client.map_url.return_value = ""

        self.user = Mock()
        self.user.id = 1
        self.user.slack_url = ""
        self.user.need_send_slack = True
        self.user.latitude = 10
        self.user.longitude = 100

    def test_application_runner(self):
        app = UserRunner(self.user, self.weather_client, Mock(), lambda i, b: None)
        app.run()

    def test_main_runner(self):
        user_table = Mock()
        user_table.get_users.return_value = [self.user]
        user_table.getuser.return_value = self.user

        system_model = Mock()
        from datetime import datetime, timedelta
        system_model.last_startup = datetime.now() - timedelta(days=3)
        system_table = Mock()
        system_table.get.return_value = system_model
        generator = Mock()
        generator.new.return_value = Mock()

        main_runner = MainRunner(user_table, system_table, generator)
        ans = main_runner.run()
        self.assertEqual(ans, "success")

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
