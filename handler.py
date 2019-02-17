#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import datetime

import boto3

import settings
from model import UserTable, SystemTable
from slack_helper import Slack
from weather import WeatherClient, filter_weathers

DATETIME_FORMAT = settings.datetime_format()
NEED_SEND_SLACK_ELAPSED_HOURS = settings.need_send_slack_elapsed_hours()
OBSERVATION_BEFORE_MINUTES = settings.judge_rain_observation_before_minutes()
RAINFALL = settings.judge_rain_rainfall()


def handler(event, context):
    app_id = os.environ["APPID"]
    user_table_name = os.environ["USER_TABLE"]
    system_table_name = os.environ["SYSTEM_TABLE"]
    dynamodb = boto3.resource('dynamodb')
    user_table = UserTable(dynamodb.Table(user_table_name))
    system_table = SystemTable(dynamodb.Table(system_table_name))
    weather_client = WeatherClient(app_id)
    main_handler = MainRunner(user_table, system_table, weather_client)
    main_handler.run()


class MainRunner:
    def __init__(self, table: UserTable, system_table: SystemTable, weather_client: WeatherClient):
        self.table = table
        self.system_table = system_table
        self.weather_client = weather_client

    def run(self):
        if self.__need_send_slack():
            self.update_all_users_need_send_slack()
        self.system_table.update_last_startup()

        for user in self.table.get_users():
            try:
                user = UserTable.UserModel(user)
                ApplicationRunner(user, self.weather_client,
                                  Slack(user.slack_url), self.table.update_need_send_slack).run()
                self.system_table.update_last_startup()
            except Exception as e:
                print(e)

    def __need_send_slack(self):
        """
        if Difference between last_startup and now is out of NEED_SEND_SLACK_ELAPSED_HOURS,
        return True
        :return:
        """
        return (datetime.now() - datetime.strptime(self.system_table.get().last_startup,
                                                   DATETIME_FORMAT)).seconds > 3600 * NEED_SEND_SLACK_ELAPSED_HOURS

    def update_all_users_need_send_slack(self):
        for user in self.table.get_users():
            self.table.update_need_send_slack(user.id, True)


class ApplicationRunner:
    def __init__(self, user, weather_client, slack, change_status):
        """

        :param user: UserTable
        :param weather_client:
        :param slack:
        :param change_status: (userid, need_send_slack)-> None
        :type change_status: (int,bool)->None
        """
        self.user = user
        self.weather_client = weather_client
        self.change_status = change_status
        self.slack = slack

    def run(self):
        """
        If 'weathers' have Rainfall data, send the message to slack url.

        """
        coordinates = (self.user.longitude, self.user.latitude)
        info = self.weather_client.weather_info(coordinates)
        send_slack = self.user.need_send_slack
        weathers = filter_weathers(info, is_raining)

        now_need = send_slack
        if len(weathers) > 0:
            if now_need:
                message = create_raining_message(weathers)
                message = "\n".join([message, self.weather_client.map_url(coordinates)])
                self.slack.send(message)
                send_slack = False
        else:
            send_slack = True
        if now_need != send_slack:
            self.change_status(self.user.id, send_slack)


def is_raining(weather,compare_date=None):
    """
    If 'weathers' have Rainfall data, return weather Type. (ex. "observation" or "forecast")

    :param weather:
    {
        "Type": "observation" or "forecast"
        "Date": "201812221850"
        "Railfall": 10.00 * not need
    }
    :type weather: dict[str,any]
    :return: "observation" or "forecast" or None
    """

    def __is_rainfall(weather):
        rainfall = weather.get("Rainfall", 0)
        return rainfall > RAINFALL
    if compare_date is None:
        compare_date = datetime.now()
    weather_type = weather["Type"]
    date = datetime.strptime(weather["Date"], "%Y%m%d%H%M")
    if weather_type == "observation" and (compare_date - date).total_seconds() <= OBSERVATION_BEFORE_MINUTES * 60:
        return __is_rainfall(weather)
    elif weather_type == "forecast":
        return __is_rainfall(weather)


RAINING = settings.message_raining()
FORECAST_RAINING = settings.message_forecast_raining()


def create_raining_message(weathers):
    """
    create message for send slack

    :param weathers:
    [{
        "Type": "observation" or "forecast"
        "Date": "201812221850"
        "Railfall": 10.00 * not need
    }]
    :type weathers: list[dict[str,str]]
    :return:
    """
    ms = list()
    if len(weathers) > 0:
        first_rain = weathers[0]
        rain_type = first_rain.get("Type")
        if rain_type == "observation":
            ms.append(RAINING)
        elif rain_type == "forecast":
            date = datetime.strptime(first_rain["Date"], "%Y%m%d%H%M")
            ms.append(FORECAST_RAINING.format(date.strftime("%H:%M")))

    return "\n".join(ms)
