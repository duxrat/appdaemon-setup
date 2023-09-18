import appdaemon.plugins.hass.hassapi as hass
from utils.base import App, toggle


# todo: require args error on compile
# todo: have a base with stuff like initialized variables like timer


class Light(App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timer = None

    async def initialize(self):
        await super().initialize()
        await self.listen_state(self.motion, "binary_sensor.motion_" + self.args["sensor"])

    @toggle("light")
    def motion(self, entity, attribute, old, new, kwargs):
        if new == "on":
            self.turn_on("light." + self.args["light"])
            # If there's a timer running, cancel it
            if self.timer is not None:
                self.cancel_timer(self.timer)
                self.timer = None
        else:
            # If motion stops, start the timer
            self.set_timer()

    def set_timer(self):
        # Cancel any existing timer
        if self.timer is not None:
            self.cancel_timer(self.timer)
        # Start a new timer to turn off the light after a specified time
        self.timer = self.run_in(self.turn_off_light, self.args.get("timer", 2))

    def turn_off_light(self, kwargs):
        self.turn_off("light." + self.args["light"])
        # Reset the timer handle
        self.timer = None
