from datetime import datetime
import inspect
import os
from functools import wraps
from typing import Any, Optional

import appdaemon.plugins.hass.hassapi as hass

entity_prefix = "input_boolean.conf_app_"
apps = ["dev", "light", "checks", "schedule", "music", "project", "sleep"]


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
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # format in %Y-%m-%d %H:%M:%S

    async def bool_state(
        self,
        entity_id: str = None,
        default: Any = None,
        copy: bool = True,
        **kwargs: Optional[Any],
    ) -> Any:
        state = await super().get_state(entity_id, None, default, copy, **kwargs)
        if state == "on":
            return True
        elif state == "off":
            return False
        else:
            raise ValueError(f"State of {entity_id} is not on or off.")


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
                    return await func(self, *args)
                else:
                    return await func(self)
            return await nop()

        return wrapper

    return decorator
