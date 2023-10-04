import os
from functools import wraps

import appdaemon.plugins.hass.hassapi as hass

entity_prefix = "input_boolean.conf_app_"
apps = ["light", "checks", "schedule"]


class App(hass.Hass):
    async def initialize(self):
        self.is_active = {}
        for name in apps:
            state = await self.get_state(f"{entity_prefix}{name}")
            self.is_active[name] = state == "off" if os.environ.get("DEV") == "true" else state == "on"
            await self.listen_state(self.make_toggle, f"{entity_prefix}{name}")

    async def make_toggle(self, entity, attribute, old, new, kwargs):
        name = entity.split(entity_prefix)[1]
        self.is_active[name] = new == "off" if os.environ.get("DEV") == "true" else new == "on"


def toggle(name):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if name not in self.is_active:
                raise KeyError(f"Add {name} to the apps list.")
            if self.is_active[name]:
                return await func(self, *args, **kwargs)
            return None

        return wrapper

    return decorator
