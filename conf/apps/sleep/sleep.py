from utils.base import App, toggle


class Sleep(App):
    async def initialize(self):
        await super().initialize()

        await self.listen_state(self.sleep, "calendar.sleep")
        await self.listen_state(self.bed_occupied, "binary_sensor.bed_occupied")
        await self.listen_state(self.bed_occupied_long, "binary_sensor.bed_occupied", new="on", duration=1)
        await self.listen_state(self.bed_occupied_long, "calendar.sleep", new="off")

    @toggle("sleep")
    async def sleep(self, new):
        await self.select_option("input_select.project", "Sleep" if new == "on" else "sleepy")

    @toggle("sleep")
    async def bed_occupied(self, new):
        calendar_sleep = await self.get_state("calendar.sleep")
        if calendar_sleep == "on":
            if new == "on":
                await self.turn_off("light.hue_bedroom")
            # else light them and room up to min

    @toggle("sleep")
    async def bed_occupied_long(self, new):
        calendar_sleep = await self.bool_state("calendar.sleep")
        bed_occupied = await self.bool_state("input_boolean.bed_occupied")

        if bed_occupied and not calendar_sleep:
            slot = await self.get_state("calendar.slots", "message")
            if slot.startsWith("Sleep"):  # and sleep date is not lower
                print(slot)
            # create sleep event if sleep date with given number is today or before
            # then set it to tomorrow
            else:
                # alarm
                pass


# allow to create sleep manually, 17-24 1st, 3-10 2nd, msg ALWAYS SPLIT SLEEP
