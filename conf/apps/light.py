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
