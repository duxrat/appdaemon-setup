import os
from functools import wraps

import appdaemon.plugins.hass.hassapi as hass


class App(hass.Hass):
    async def initialize(self):
        self.is_active = {}
        await self.listen_state(self.make_toggle, "input_boolean.conf_app_*")

    async def make_toggle(self, entity, attribute, old, new, kwargs):
        name = entity.split("input_boolean.conf_app_")[1]
        self.is_active[name] = new == "off" if os.environ.get("DEV") == "true" else new == "on"


def toggle(name):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if name not in self.is_active:
                state = await self.get_state(f"input_boolean.conf_app_{name}")
                self.is_active[name] = state == "off" if os.environ.get("DEV") == "true" else state == "on"
            if self.is_active[name]:
                return await func(self, *args, **kwargs)
            return None

        return wrapper

    return decorator
