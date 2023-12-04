from datetime import datetime, timedelta

from utils.base import App, toggle


class Sleep(App):
    def __init__(self, *args, **kwargs):
        self.occupied_bell_handle = None
        super().__init__(*args, **kwargs)

    async def initialize(self):
        await super().initialize()

        await self.listen_state(self.sleep, "calendar.sleep")
        await self.listen_state(self.bed_occupied, "binary_sensor.bed_occupied", new="on")
        await self.listen_state(self.bed_occupied_long, "binary_sensor.bed_occupied", new="on", duration=15)
        await self.listen_state(self.bed_occupied, "calendar.sleep", new="off")
        await self.listen_state(self.bed_occupied_long, "calendar.sleep", new="off", duration=15)
        await self.listen_state(self.bed_left, "binary_sensor.bed_occupied", new="off")

    @toggle("sleep")
    async def sleep(self, new):
        await self.select_option("input_select.project", "Sleep" if new == "on" else "sleepy")

    @toggle("sleep")
    async def bed_occupied(self, new):
        calendar_sleep = await self.bool_state("calendar.sleep")
        bed_occupied = await self.bool_state("binary_sensor.bed_occupied")

        if not bed_occupied:
            return

        if calendar_sleep:
            await self.turn_off("light.hue_bedroom")
        else:
            slot = await self.get_state("calendar.slots", "message")
            xperia = await self.get_state(
                "sensor.xperia_battery_state",
            )
            date = await self.date()
            marker_name = "input_datetime.sleep_" + slot[-1]
            marker = await self.get_state(marker_name)

            if xperia == "charging" and (slot == "Sleep 1" or slot == "Sleep 2") and marker != str(date):
                await self.set_state(marker_name, state=date)
                await self.call_service(
                    "calendar/create_event",
                    entity_id="calendar.sleep",
                    summary="Sleep",
                    start_date_time=self.datetime_str(),
                    end_date_time=(datetime.now() + timedelta(hours=2, minutes=35)).strftime("%Y-%m-%d %H:%M:%S"),
                )
            else:
                self.occupied_bell_handle = await self.run_every(
                    lambda x: self.call_service("esphome/bedroom_bell"), "now", 4
                )

    @toggle("sleep")
    async def bed_occupied_long(self):
        calendar_sleep = await self.bool_state("calendar.sleep")
        bed_occupied = await self.bool_state("binary_sensor.bed_occupied")

        if not calendar_sleep and bed_occupied:
            await self.turn_on("switch.bedroom_alarm")

    @toggle("sleep")
    async def bed_left(self, new):
        await self.turn_off("switch.bedroom_alarm")

        if self.occupied_bell_handle:
            await self.cancel_timer(self.occupied_bell_handle)

        calendar_sleep = await self.bool_state("calendar.sleep")
        if calendar_sleep:
            await self.turn_on("light.hue_bedroom")


# allow to create sleep manually, 17-24 1st, 3-10 2nd, msg ALWAYS SPLIT SLEEP
