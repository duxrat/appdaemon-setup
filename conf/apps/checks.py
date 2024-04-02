from datetime import datetime, timedelta

from utils.base import App, args
from utils.bots import bots
from utils.constants import date_format


class Checks(App):
    def initialize(self):
        x = self.get_history(entity_id="sensor.band_battery", days=10)
        self.set_state("sensor.band_battery", state=x[0][-1]["state"] if x else "0")

        self.listen_state(self.calendar_slots, "calendar.slots")
        self.listen_state(self.sleep_length, "calendar.slots", attribute="message")
        self.listen_state(self.sleep_length, "calendar.slots")

    @args
    def calendar_slots(self, *args):
        bots.checks("No slot assigned")

    @args
    def sleep_length(self, *args):
        state = self.get_state("calendar.slots", attribute="all")
        attributes = state["attributes"]
        if attributes["message"] == "Sleep" and state["state"] == "on":
            start = datetime.strptime(attributes["start_time"], date_format)
            end = datetime.strptime(attributes["end_time"], date_format)
            duration = end - start
            if duration > timedelta(hours=8):
                bots.checks("Sleep duration longer than 8 hours")
