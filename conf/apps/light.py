from utils.base import App, args

# todo: require args error on compile
# todo: have a base with stuff like initialized variables like timer


class Light(App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timer = None

    def initialize(self):
        self.listen_state(self.motion_on, "binary_sensor.motion_" + self.args["sensor"], new="on")
        self.listen_state(
            self.motion_off,
            "binary_sensor.motion_" + self.args["sensor"],
            new="off",
            duration=self.args.get("duration", 60),
        )

    @args
    def motion_on(self):
        self.turn_on("light." + self.args["light"])

    @args
    def motion_off(self):
        self.turn_off("light." + self.args["light"])


# class Light(App):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.timer = None
#
#     def initialize(self):
#         super().initialize()
#         self.listen_state(self.motion, "binary_sensor.motion_" + self.args["sensor"])
#
#     @toggle
#     def motion(self):
#         if new == "on":
#             self.turn_on("light." + self.args["light"])
#             # If there's a timer running, cancel it
#             if self.timer is not None:
#                 self.cancel_timer(self.timer)
#                 self.timer = None
#         else:
#             # If motion stops, start the timer
#             self.set_timer()
#
#     def set_timer(self):
#         # Cancel any existing timer
#         if self.timer is not None:
#             self.cancel_timer(self.timer)
#         # Start a new timer to turn off the light after a specified time
#         self.timer = self.run_in(self.turn_off_light, self.args.get("timer", 60))
#
#     def turn_off_light(self, kwargs):
#         self.turn_off("light." + self.args["light"])
#         # Reset the timer handle
#         self.timer = None
