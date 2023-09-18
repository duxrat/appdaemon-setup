import os
from functools import wraps

import appdaemon.plugins.hass.hassapi as hass


class App(hass.Hass):
    async def initialize(self):
        self.is_active = {}

        for name in ["light", "checks"]:
            state = await self.get_state(f"input_boolean.conf_app_{name}")
            self.is_active[name] = state == "off" if os.environ.get("DEV") == "true" else state == "on"
            await self.listen_state(self.make_toggle_app(name), f"input_boolean.conf_app_{name}")

    def make_toggle_app(self, name):
        async def toggle(entity, attribute, old, new, kwargs):
            self.is_active[name] = new == "off" if os.environ.get("DEV") == "true" else new == "on"

        return toggle


def toggle(name):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.is_active.get(name, False):
                return func(self, *args, **kwargs)

        return wrapper

    return decorator
