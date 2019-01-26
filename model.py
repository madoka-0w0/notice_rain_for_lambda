class UserTable:
    def __init__(self, table):
        self._table = table

    def get_users(self):
        response = self._table.scan()
        return response

    def get_user(self, user_id: int):
        response = self._table.get_item(Key={
            self.UserModel.userid_name: user_id
        })
        return self.UserModel(response["Item"])

    def change_status(self, status=None):
        status = True if status is None else status
        self._table.update_item(
            Key={
                self.UserModel.userid_name: 1
            },
            UpdateExpression='SET {} = :val1'.format(self.UserModel.need_send_slack_name),
            ExpressionAttributeValues={
                ':val1': status
            })

    class UserModel(object):
        userid_name = "userid"
        need_send_slack_name = "need_send_slack"
        slack_url_name = "slack_url"
        longitude_name = "longitude"
        latitude_name = "latitude"

        def __init__(self, item: dict):
            self._item = item

        @property
        def id(self):
            return self._item[self.userid_name]

        @property
        def need_send_slack(self):
            return self._item[self.need_send_slack_name]

        @property
        def slack_url(self):
            return self._item[self.slack_url_name]

        @property
        def longitude(self):
            return self._item.get(self.longitude_name)

        @property
        def latitude(self):
            return self._item.get(self.latitude_name)
