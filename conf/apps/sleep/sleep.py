from datetime import datetime, timedelta

from utils.base import App, args, e


class Sleep(App):
    def __init__(self, *args, **kwargs):
        self.occupied_bell_handle = None
        super().__init__(*args, **kwargs)

    def initialize(self):
        @self.listen(e("calendar.sleep"))
        def sleep(sleep):
            self.select_option("input_select.project", "Sleep" if sleep == "on" else "sleepy")

        sleep.run()

        @self.listen([e("binary_sensor.bed_occupied", new="on"), e("calendar.sleep", new="off")])
        def bed_occupied(bed_occupied, sleep):
            if not bed_occupied:
                return

            if sleep:
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

        bed_occupied.run()

        @self.listen([e("binary_sensor.bed_occupied", new="on", duration=15), e("calendar.sleep", new=False)])
        def bed_occupied_long(bed_occupied, sleep):
            if not sleep and bed_occupied:
                self.turn_on("switch.bedroom_alarm")

        bed_occupied_long.run()

        @self.listen(e("binary_sensor.bed_occupied", new="off"))
        def bed_left(bed_occupied):
            self.turn_off("switch.bedroom_alarm")

            if self.occupied_bell_handle:
                self.cancel_timer(self.occupied_bell_handle)

            calendar_sleep = self.bool_state("calendar.sleep")
            if calendar_sleep:
                self.turn_on("light.hue_bedroom")

        bed_left.run()


# allow to create sleep manually, 17-24 1st, 3-10 2nd, msg ALWAYS SPLIT SLEEP
