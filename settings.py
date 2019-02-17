from yaml import load

settings_path = "settings.yml"


def __read_setting():
    with open(settings_path, "r", encoding="utf-8")as f:
        return load(f)


def datetime_format():
    return __read_setting()["datetime_format"]


def system_id():
    return __read_setting()["system_id"]


def __need_send_slack():
    return __read_setting()["need_send_slack"]


def need_send_slack_elapsed_hours():
    return __need_send_slack()["elapsed_hours"]


def __weather():
    return __read_setting()["weather"]


def weather_map_zoom():
    return __weather()["map_zoom"]


def interval():
    return __weather()["interval"]


def __judge_rain():
    return __weather()["judge_rain"]


def judge_rain_rainfall():
    return __judge_rain()["rainfall"]


def judge_rain_observation_before_minutes():
    return __judge_rain()["observation_before_minutes"]


def __message():
    return __read_setting()["message"]


def message_raining():
    return __message()["raining"]


def message_forecast_raining():
    return __message()["forecast_raining"]
