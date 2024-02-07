from utils.base import App, args


class Couch(App):
    def __init__(self, *args, **kwargs):
        self.occupied_bell_handle = None
        super().__init__(*args, **kwargs)

    def initialize(self):
        self.cancel_timer(self.occupied_bell_handle)
        self.listen_state(self.couch_occupied, "binary_sensor.couch_occupied", new="on")
        self.listen_state(self.couch_occupied, "sensor.slot", new="Work")

        self.listen_state(self.couch_occupied_long, "binary_sensor.couch_occupied", new="on", duration=15)
        self.listen_state(self.couch_occupied_long, "sensor.slot", new="Work", duration=15)

        self.listen_state(self.couch_left, "binary_sensor.couch_occupied", new="off")

    @args
    def couch_occupied(self):
        couch_occupied = self.bool_state("binary_sensor.couch_occupied")
        work = self.get_state("sensor.slot") == "Work"

        if work and couch_occupied:
            self.occupied_bell_handle = self.run_every(lambda x: self.call_service("esphome/couch_bell"), "now", 4)

    @args
    def couch_occupied_long(self):
        couch_occupied = self.bool_state("binary_sensor.couch_occupied")
        work = self.get_state("sensor.slot") == "Work"

        if work and couch_occupied:
            self.turn_on("switch.couch_alarm")

    @args
    def couch_left(self):
        self.turn_off("switch.couch_alarm")
        self.cancel_timer(self.occupied_bell_handle)
