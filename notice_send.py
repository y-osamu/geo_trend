import slackweb


def send_slack_log(message):
    slack = slackweb.Slack(
        url="")
    slack.notify(text=message)
