import inspect
import os
from datetime import datetime
from functools import wraps
from typing import Any, Optional, Callable, Union

import datetime as dt
import appdaemon.plugins.hass.hassapi as hass

entity_prefix = "input_boolean.conf_app_"


def nop():
    return


class App(hass.Hass):
    def datetime_str(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # format in %Y-%m-%d %H:%M:%S

    def listen_state(
        self, callback: Callable, entity_id: Union[str, list] = None, now=False, **kwargs: Optional[Any]
    ) -> Union[Any, str, list]:
        if now:
            state = self.get_state(entity_id)
            callback(state)
        return super().listen_state(callback, entity_id, **kwargs)

    def bool_state(
        self,
        entity_id: str = None,
        default: Any = None,
        copy: bool = True,
        **kwargs: Optional[Any],
    ) -> Any:
        state = super().get_state(entity_id, None, default, copy, **kwargs)
        if state == "on":
            return True
        elif state == "off":
            return False
        else:
            raise ValueError(f"State of {entity_id} is not on or off.")

    # redefining methods without async as PyCharm doesn't infer that @utils.sync_wrapper
    # makes return type not Coroutine when called without await
    def get_state(self, *args, **kwargs):
        return super().get_state(*args, **kwargs)

    def datetime(self, *args, **kwargs) -> dt.datetime:
        return super().datetime(*args, **kwargs)

    def parse_datetime(self, *args, **kwargs) -> dt.datetime:
        return super().parse_datetime(*args, **kwargs)

    def run_every(self, *args, **kwargs) -> str:
        return super().run_every(*args, **kwargs)


def args(func):
    sig = inspect.signature(func)

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if len(args) == 0:
            return func(self)
        elif len(args) == 1:
            return func(self, args[0])
        elif len(sig.parameters) == 2:
            return func(self, args[3])
        elif len(sig.parameters) > 2:
            return func(self, *args)
        else:
            return func(self)

    return wrapper
