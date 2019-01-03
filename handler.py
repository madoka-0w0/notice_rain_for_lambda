#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import datetime

import boto3

from slack_helper import Slack
from weather import WeatherClient


def handler(event, context):
    app_id = os.environ["APPID"]
    longitude, latitude = os.environ["LONGITUDE"], os.environ["LATITUDE"]
    slackurl = os.environ["SLACK_URL"]
    table_name = os.environ["TABLE"]
    manager = WeatherClient(app_id, (longitude, latitude))
    slack = Slack(slackurl)
    app = App(table_name)
    message = app.send_slack_if_rain(manager, slack)
    return {
        'message': message
    }


class App:
    def __init__(self, table_name):
        dynamodb = boto3.resource('dynamodb')
        self.table = dynamodb.Table(table_name)
        self.send_slack = self.need_send_slack()

    def send_slack_if_rain(self, manager, slack):
        """
        If it can get 'weathers' have Rainfall data, it send message to slack url.

        :type manager: WeatherClient
        :type slack: Slack
        :return:
        """
        info = manager.get()
        weathers = info["Feature"][0]["Property"]["WeatherList"]["Weather"]
        rain_type = self.__is_raining(weathers)
        message = None
        if rain_type == "observation":
            message = "雨が降っています。"
        elif rain_type == "forecast":
            message = "雨が１時間以内に降るかもしれません。"

        now_need = self.send_slack
        if message is not None:
            if self.send_slack:
                slack.send(message)
                self.send_slack = False
        else:
            self.send_slack = True
        if now_need != self.send_slack:
            self.update_need_send_slack(self.send_slack)

        return message

    def need_send_slack(self):
        response = self.table.get_item(Key={
            'userid': 1
        })
        return response["Item"]["need_send_slack"]

    def update_need_send_slack(self, need):
        self.table.update_item(
            Key={
                'userid': 1
            },
            UpdateExpression='SET need_send_slack = :val1',
            ExpressionAttributeValues={
                ':val1': need
            })

    @staticmethod
    def __is_raining(weathers):
        """
        If 'weathers' have Rainfall data, return weather Type. (ex. "observation" or "forecast")

        :param weathers:
        [{
            "Type": "observation" or "forecast"
            "Date": "201812221850"
            "Railfall": 10.00 * not need
        }]
        :type weathers: list[dict[str,any]]
        :return: "observation" or "forecast" or None
        """

        def __is_rainfall(weather):
            rainfall = weather.get("Rainfall")
            return rainfall is not None and rainfall != 0.0

        now = datetime.now()
        for weather in weathers:
            weather_type = weather["Type"]
            date = datetime.strptime(weather["Date"], "%Y%m%d%H%M")
            if weather_type == "observation" and (now - date).total_seconds() <= 10 * 60:
                if __is_rainfall(weather):
                    return weather_type
            elif weather_type == "forecast":
                if __is_rainfall(weather):
                    return weather_type
