import datetime as dt
import inspect
import os
from functools import wraps

import appdaemon.plugins.hass.hassapi as hass

entity_prefix = "input_boolean.conf_app_"
apps = ["light", "checks", "schedule", "music", "project"]


async def nop():
    return


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

    def datetime_str(self) -> str:
        return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # format in %Y-%m-%d %H:%M:%S


def toggle(name):
    if name not in apps:
        raise KeyError(f"Add {name} to the apps list.")

    def decorator(func):
        sig = inspect.signature(func)

        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if self.is_active[name]:
                if len(sig.parameters) == 2:
                    return await func(self, args[3])
                elif len(sig.parameters) > 2:
                    return await func(self, *args, **kwargs)
                else:
                    return await func(self)
            return await nop()

        return wrapper

    return decorator
