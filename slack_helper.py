import slackweb


class Slack:
    def __init__(self, url):
        self.slack = slackweb.Slack(url)

    def send(self, text, channel=None):
        payload = {
            "text": text,
        }
        if channel:
            payload["channel"] = channel
        self.slack.send(payload)
