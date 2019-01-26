#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import datetime

import boto3

from model import UserTable
from slack_helper import Slack
from weather import WeatherClient, filter_weathers


def handler(event, context):
    app_id = os.environ["APPID"]
    table_name = os.environ["TABLE"]
    dynamodb = boto3.resource('dynamodb')
    table = UserTable(dynamodb.Table(table_name))
    weather_client = WeatherClient(app_id)
    main_handler = MainRunner(table, weather_client)
    main_handler.run()


class MainRunner:
    def __init__(self, table: UserTable, weather_client: WeatherClient):
        self.table = table
        self.weather_client = weather_client

    def run(self):
        for user in self.table.get_users():
            print(user)
            try:
                ApplicationRunner(UserTable.UserModel(user), self.weather_client, self.table.change_status).run()
            except Exception as e:
                print(e)


class ApplicationRunner:
    def __init__(self, user, weather_client, change_status):
        """

        :param user: UserTable
        :param weather_client:
        :param change_status: (userid, need_send_slack)-> None
        :type change_status: (int,bool)->None
        """
        self.user = user
        self.weather_client = weather_client
        self.change_status = change_status
        self.slack = Slack(self.user.slack_url)

    def run(self):
        """
        If 'weathers' have Rainfall data, send the message to slack url.

        """
        coordinates = (self.user.longitude, self.user.latitude)
        info = self.weather_client.weather_info(coordinates)
        send_slack = self.user.need_send_slack
        weathers = filter_weathers(info, self.__is_raining)

        now_need = send_slack
        if len(weathers) > 0:
            if now_need:
                message = self.create_message(weathers, [self.weather_client.map_url(coordinates)])
                self.slack.send(message)
                send_slack = False
        else:
            send_slack = True
        if now_need != send_slack:
            self.change_status(self.user.id, send_slack)

    @staticmethod
    def __is_raining(weather):
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
            return rainfall != 0.0

        now = datetime.now()
        weather_type = weather["Type"]
        date = datetime.strptime(weather["Date"], "%Y%m%d%H%M")
        if weather_type == "observation" and (now - date).total_seconds() <= 10 * 60:
            return __is_rainfall(weather)
        elif weather_type == "forecast":
            return __is_rainfall(weather)

    @staticmethod
    def create_message(weathers, messages):
        """
        create message for send slack

        :param weathers:
        [{
            "Type": "observation" or "forecast"
            "Date": "201812221850"
            "Railfall": 10.00 * not need
        }]
        :type weathers: list[dict[str,str]]
        :type messages: list[str]
        :return:
        """
        ms = list()
        if len(weathers) > 0:
            first_rain = weathers[0]
            rain_type = first_rain.get("Type")
            if rain_type == "observation":
                ms.append("雨が降っています。")
            elif rain_type == "forecast":
                date = datetime.strptime(first_rain["Date"], "%Y%m%d%H%M")
                ms.append("雨が{}ごろから降るかもしれません。".format(date.strftime("%H:%M")))

        ms.extend(messages)
        return "\n".join(ms)

