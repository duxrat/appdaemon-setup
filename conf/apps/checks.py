from utils.base import App, toggle
from utils.bots import bots


class Checks(App):
    async def initialize(self):
        await super().initialize()
        await self.listen_state(self.calendar_slots, "calendar.slots", new="off")

    @toggle("checks")
    async def calendar_slots(self, *args):
        await bots.checks("No slot assigned")
