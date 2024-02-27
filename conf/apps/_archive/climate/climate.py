import math

from utils.base import App


class Climate(App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def initialize(self):
        self.humid_sensors = self.find_sensors("sensor.sht_", "_humidity")

        for sensor in self.humid_sensors:
            self.listen_state(self.calculate_absolute_humidity, sensor)

    def find_sensors(self, prefix, suffix):
        all_sensors = self.get_state("sensor")
        return [sensor for sensor in all_sensors if sensor.startswith(prefix) and sensor.endswith(suffix)]

    def calculate_absolute_humidity(self, entity, attribute, old, new, kwargs):
        sensor_id = entity.replace("sensor.sht_", "").replace("_humidity", "")
        temperature_entity = f"sensor.sht_{sensor_id}_temperature"
        temperature = self.get_state(temperature_entity)

        if temperature is not None and new is not None:
            temperature = float(temperature)
            humidity = float(new)
            abs_humidity = self.compute_absolute_humidity(temperature, humidity)

            self.set_state(
                f"sensor.sht_{sensor_id}_absolute",
                state=round(abs_humidity, 1),
                attributes={
                    "unit_of_measurement": "g/m³",
                    "friendly_name": f"SHT {sensor_id.replace('_', ' ').capitalize()} Absolute",
                },
            )

    def compute_absolute_humidity(self, temperature, relative_humidity):
        saturation_vapor_pressure = 6.112 * math.exp(17.67 * temperature / (temperature + 243.5))
        actual_vapor_pressure = relative_humidity * saturation_vapor_pressure / 100
        return 216.7 * (actual_vapor_pressure / (273.15 + temperature))
