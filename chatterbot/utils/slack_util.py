import json


# A small set of helper classes for working with Slack
class SlackUtil:

    def __init__(self):
        pass

    def get_channel(self, sc, channel_name):
        chan_list = self.get_channel_list(sc)
        for chan in chan_list["channels"]:
            if chan["name"] == channel_name:
                return chan
        return None

    def get_channels_to_monitor(self, sc, channel_names):
        to_monitor = []
        chan_list = self.get_channel_list(sc)

        for chan in chan_list["channels"]:
            if chan["name"] in channel_names:
                to_monitor.append(chan["id"])
        # print to_monitor
        return to_monitor

    def get_channel_list(self, sc):
        chan_list = json.loads(sc.server.api_call("channels.list"))

        return chan_list
