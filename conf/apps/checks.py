from datetime import datetime, timedelta

from utils.base import App, toggle
from utils.bots import bots
from utils.constants import date_format


class Checks(App):
    def initialize(self):
        super().initialize()
        self.listen_state(self.calendar_slots, "calendar.slots")
        self.listen_state(self.sleep_length, "calendar.slots", attribute="message")
        self.listen_state(self.sleep_length, "calendar.slots")

    @toggle("checks")
    def calendar_slots(self, *args):
        bots.checks("No slot assigned")

    @toggle("checks")
    def sleep_length(self, *args):
        state = self.get_state("calendar.slots", attribute="all")
        attributes = state["attributes"]
        if attributes["message"] == "Sleep" and state["state"] == "on":
            start = datetime.strptime(attributes["start_time"], date_format)
            end = datetime.strptime(attributes["end_time"], date_format)
            duration = end - start
            if duration > timedelta(hours=8):
                bots.checks("Sleep duration longer than 8 hours")
