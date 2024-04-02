import datetime as dt
import inspect
from datetime import datetime
from functools import wraps

import appdaemon.plugins.hass.hassapi as hass

entity_prefix = "input_boolean.conf_app_"


def nop():
    return


class App(hass.Hass):
    def datetime_str(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def cancel_timer(self, handle: str, silent=False) -> bool:
        if handle:
            return super().cancel_timer(handle, silent)
        return False

    # redefining methods without async as PyCharm doesn't infer that @utils.sync_wrapper
    # makes return type not Coroutine when called without await
    def get_state(self, *args, **kwargs):
        # AD SYNC_WRAPPER ONLY WORKS IN PYTHON 3.8,
        # HIGHER VERSIONS RETURN TASKS INSTEAD OF VALUES
        return super().get_state(*args, **kwargs)

    def datetime(self, *args, **kwargs) -> dt.datetime:
        return super().datetime(*args, **kwargs)

    def parse_datetime(self, *args, **kwargs) -> dt.datetime:
        return super().parse_datetime(*args, **kwargs)

    def format_datetime(self, datetime) -> str:
        return datetime.strftime("%Y-%m-%d %H:%M:%S")

    def run_every(self, *args, **kwargs) -> str:
        return super().run_every(*args, **kwargs)

    def listen(self, params):
        if not isinstance(params, list):
            params = [params]

        def decorator(func):
            def wrapper(*args_, **kwargs):
                if len(params) == 1:
                    return func(args_[3], **kwargs)
                else:
                    x = [self.get_state(entity, **kwargs) for entity, kwargs in params]
                    return func(*x)

            def run():
                for entity, kwargs in params:
                    self.listen_state(wrapper, entity, **kwargs)

            wrapper.run = run
            return wrapper

        return decorator


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


def e(entity_id, **params):
    return entity_id, params
