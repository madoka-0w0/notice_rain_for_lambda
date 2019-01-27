from datetime import datetime

import settings

DATETIME_FORMAT = settings.datetime_format()
SYSTEM_ID = settings.system_id()


class UserTable:
    def __init__(self, table):
        self._table = table

    def get_users(self):
        response = self._table.scan()
        return response

    def get_user(self, user_id: int):
        response = self._table.get_item(Key={
            self.UserModel.USERID_NAME: user_id
        })
        return self.UserModel(response["Item"])

    def update_need_send_slack(self, userid, status=None):
        status = True if status is None else status
        self._table.update_item(
            Key={
                self.UserModel.USERID_NAME: userid
            },
            UpdateExpression='SET {} = :val1'.format(self.UserModel.NEED_SEND_SLACK_NAME),
            ExpressionAttributeValues={
                ':val1': status
            })

    class UserModel(object):
        USERID_NAME = "userid"
        NEED_SEND_SLACK_NAME = "need_send_slack"
        SLACK_URL_NAME = "slack_url"
        LONGITUDE_NAME = "longitude"
        LATITUDE_NAME = "latitude"

        def __init__(self, item: dict):
            self._item = item

        @property
        def id(self):
            return self._item[self.USERID_NAME]

        @property
        def need_send_slack(self):
            return self._item[self.NEED_SEND_SLACK_NAME]

        @property
        def slack_url(self):
            return self._item[self.SLACK_URL_NAME]

        @property
        def longitude(self):
            return self._item.get(self.LONGITUDE_NAME)

        @property
        def latitude(self):
            return self._item.get(self.LATITUDE_NAME)


class SystemTable:
    def __init__(self, table):
        self._table = table

    def get(self):
        response = self._table.get_item(Key={
            self.SystemModel.SYSTEM_ID_NAME: SYSTEM_ID
        })
        return self.SystemModel(response["Item"])

    def update_last_startup(self):
        self._table.update_item(
            Key={
                self.SystemModel.SYSTEM_ID_NAME: SYSTEM_ID
            },
            UpdateExpression='SET {} = :val1'.format(self.SystemModel.LAST_STARTUP),
            ExpressionAttributeValues={
                ':val1': datetime.now().strftime(DATETIME_FORMAT)
            })

    class SystemModel(object):
        SYSTEM_ID_NAME = "system_id"
        LAST_STARTUP = "last_startup"

        def __init__(self, item: dict):
            self._item = item

        @property
        def last_startup(self):
            return self._item.get(self.LAST_STARTUP)
