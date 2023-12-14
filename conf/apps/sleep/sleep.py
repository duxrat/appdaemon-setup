from datetime import datetime, timedelta

from utils.base import App, toggle


class Sleep(App):
    def __init__(self, *args, **kwargs):
        self.occupied_bell_handle = None
        super().__init__(*args, **kwargs)

    def initialize(self):
        super().initialize()

        self.listen_state(self.sleep, "calendar.sleep")
        self.listen_state(self.bed_occupied, "binary_sensor.bed_occupied", new="on")
        self.listen_state(self.bed_occupied_long, "binary_sensor.bed_occupied", new="on", duration=15)
        self.listen_state(self.bed_occupied, "calendar.sleep", new="off")
        self.listen_state(self.bed_occupied_long, "calendar.sleep", new="off", duration=15)
        self.listen_state(self.bed_left, "binary_sensor.bed_occupied", new="off")

    @toggle("sleep")
    def sleep(self, new):
        self.select_option("input_select.project", "Sleep" if new == "on" else "sleepy")

    @toggle("sleep")
    def bed_occupied(self):
        calendar_sleep = self.bool_state("calendar.sleep")
        bed_occupied = self.bool_state("binary_sensor.bed_occupied")

        if not bed_occupied:
            return

        if calendar_sleep:
            self.turn_off("light.hue_bedroom")
        else:
            slot = self.get_state("calendar.slots", "message")
            xperia = self.get_state(
                "sensor.xperia_battery_state",
            )
            date = self.date()
            marker_name = "input_datetime.sleep_" + slot[-1]
            marker = self.get_state(marker_name)

            if xperia == "charging" and (slot == "Sleep 1" or slot == "Sleep 2") and marker != str(date):
                self.set_state(marker_name, state=date)
                self.call_service(
                    "calendar/create_event",
                    entity_id="calendar.sleep",
                    summary="Sleep",
                    start_date_time=self.datetime_str(),
                    end_date_time=(datetime.now() + timedelta(hours=3, minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
                )
            else:
                self.occupied_bell_handle = self.run_every(
                    lambda x: self.call_service("esphome/bedroom_bell"), "now", 4
                )

    @toggle("sleep")
    def bed_occupied_long(self):
        calendar_sleep = self.bool_state("calendar.sleep")
        bed_occupied = self.bool_state("binary_sensor.bed_occupied")

        if not calendar_sleep and bed_occupied:
            self.turn_on("switch.bedroom_alarm")

    @toggle("sleep")
    def bed_left(self):
        self.turn_off("switch.bedroom_alarm")

        if self.occupied_bell_handle:
            self.cancel_timer(self.occupied_bell_handle)

        calendar_sleep = self.bool_state("calendar.sleep")
        if calendar_sleep:
            self.turn_on("light.hue_bedroom")


# allow to create sleep manually, 17-24 1st, 3-10 2nd, msg ALWAYS SPLIT SLEEP
