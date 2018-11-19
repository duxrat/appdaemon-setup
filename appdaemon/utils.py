import os
import datetime
import asyncio
import platform
import functools
import time
import cProfile
import io
import pstats

if platform.system() != "Windows":
    import pwd

__version__ = "3.1.0"
secrets = None

log_levels = {
    "CRITICAL": 50,
    "ERROR": 40,
    "WARNING": 30,
    "INFO": 20,
    "DEBUG": 10,
    "NOTSET": 0
}

class Formatter(object):
    def __init__(self):
        self.types = {}
        self.htchar = '\t'
        self.lfchar = '\n'
        self.indent = 0
        self.set_formater(object, self.__class__.format_object)
        self.set_formater(dict, self.__class__.format_dict)
        self.set_formater(list, self.__class__.format_list)
        self.set_formater(tuple, self.__class__.format_tuple)

    def set_formater(self, obj, callback):
        self.types[obj] = callback

    def __call__(self, value, **args):
        for key in args:
            setattr(self, key, args[key])
        formater = self.types[type(value) if type(value) in self.types else object]
        return formater(self, value, self.indent)

    def format_object(self, value, indent):
        return repr(value)

    def format_dict(self, value, indent):
        items = [
            self.lfchar + self.htchar * (indent + 1) + repr(key) + ': ' +
            (self.types[type(value[key]) if type(value[key]) in self.types else object])(self, value[key], indent + 1)
            for key in value
        ]
        return '{%s}' % (','.join(items) + self.lfchar + self.htchar * indent)

    def format_list(self, value, indent):
        items = [
            self.lfchar + self.htchar * (indent + 1) + (self.types[type(item) if type(item) in self.types else object])(
                self, item, indent + 1)
            for item in value
        ]
        return '[%s]' % (','.join(items) + self.lfchar + self.htchar * indent)

    def format_tuple(self, value, indent):
        items = [
            self.lfchar + self.htchar * (indent + 1) + (self.types[type(item) if type(item) in self.types else object])(
                self, item, indent + 1)
            for item in value
        ]
        return '(%s)' % (','.join(items) + self.lfchar + self.htchar * indent)


class AttrDict(dict):
    """ Dictionary subclass whose entries can be accessed by attributes
        (as well as normally).
    """

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    @staticmethod
    def from_nested_dict(data):
        """ Construct nested AttrDicts from nested dictionaries. """
        if not isinstance(data, dict):
            return data
        else:
            return AttrDict({key: AttrDict.from_nested_dict(data[key])
                             for key in data})


class StateAttrs(dict):
    def __init__(self, dict):
        device_dict = {}
        devices = set()
        for entity in dict:
            if "." in entity:
                device, name = entity.split(".")
                devices.add(device)
        for device in devices:
            entity_dict = {}
            for entity in dict:
                if "." in entity:
                    thisdevice, name = entity.split(".")
                    if device == thisdevice:
                        entity_dict[name] = dict[entity]
            device_dict[device] = AttrDict.from_nested_dict(entity_dict)

        self.__dict__ = device_dict


def _timeit(func):
    @functools.wraps(func)
    def newfunc(*args, **kwargs):
        self = args[0]
        start_time = time.time()
        result = func(self, *args, **kwargs)
        elapsed_time = time.time() - start_time
        self.log("INFO", 'function [{}] finished in {} ms'.format(
            func.__name__, int(elapsed_time * 1000)))
        return result

    return newfunc


def _profile_this(fn):
    def profiled_fn(*args, **kwargs):
        self = args[0]
        self.pr = cProfile.Profile()
        self.pr.enable()

        result = fn(self, *args, **kwargs)

        self.pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(self.pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        self.profile = fn + s.getvalue()

        return result

    return profiled_fn


def _dummy_secret(loader, node):
    pass

def _secret_yaml(loader, node):
    if secrets is None:
        raise ValueError("!secret used but no secrets file found")

    if node.value not in secrets:
        raise ValueError("{} not found in secrets file".format(node.value))

    return secrets[node.value]

def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

def day_of_week(day):
    nums = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    days = {day: idx for idx, day in enumerate(nums)}

    if type(day) == str:
        return days[day]
    if type(day) == int:
        return nums[day]
    raise ValueError("Incorrect type for 'day' in day_of_week()'")


async def run_in_executor(loop, executor, fn, *args, **kwargs):
    completed, pending = await asyncio.wait([loop.run_in_executor(executor, fn, *args, **kwargs)])
    response = list(completed)[0].result()
    return response


def find_path(name):
    for path in [os.path.join(os.path.expanduser("~"), ".homeassistant"),
                 os.path.join(os.path.sep, "etc", "appdaemon")]:
        _file = os.path.join(path, name)
        if os.path.isfile(_file) or os.path.isdir(_file):
            return _file
    return None


def single_or_list(field):
    if isinstance(field, list):
        return field
    else:
        return [field]

def _sanitize_kwargs(kwargs, keys):
    for key in keys:
        if key in kwargs:
            del kwargs[key]
    return kwargs

def process_arg(self, arg, args, **kwargs):
    if args:
        if arg in args:
            value = args[arg]
            if "int" in kwargs and kwargs["int"] is True:
                try:
                    value = int(value)
                    setattr(self, arg, value)
                except ValueError:
                    self.log("WARNING", "Invalid value for {}: {}, using default({})".format(arg, value, getattr(self, arg)))
            if "float" in kwargs and kwargs["float"] is True:
                try:
                    value = float(value)
                    setattr(self, arg, value)
                except ValueError:
                    self.log("WARNING", "Invalid value for {}: {}, using default({})".format(arg, value, getattr(self, arg)))
            else:
                setattr(self, arg, value)


def log(logger, level, msg, name="", ts=None, ascii_encode=True):
    if name != "":
        name = " {}:".format(name)

    if ts == None:
        timestamp = datetime.datetime.now()
    else:
        timestamp = ts

    if ascii_encode is True:
        safe_enc = lambda s: str(s).encode("utf-8", "replace").decode("ascii", "replace")
        name = safe_enc(name)
        msg = safe_enc(msg)

    logger.log(log_levels[level], "{} {}{} {}".format(timestamp, level, name, msg))

def find_owner(filename):
    return pwd.getpwuid(os.stat(filename).st_uid).pw_name

def check_path(type, logger, path, pathtype="directory", permissions=None):
    #disable checks for windows platform
    if platform.system() == "Windows":
        return

    try:
        perms = permissions
        if pathtype == "file":
            dir = os.path.dirname(path)
            file = path
            if perms is None:
                perms = "r"
        else:
            dir = path
            file = None
            if perms is None:
                perms = "rx"

        dirs = []
        while not os.path.ismount(dir):
            dirs.append(dir)
            d, F = os.path.split(dir)
            dir = d

        fullpath = True
        for directory in reversed(dirs):
            if not os.access(directory, os.F_OK):
                path_log(logger, "{}: {} does not exist exist".format(type, directory))
                fullpath = False
            elif not os.path.isdir(directory):
                if os.path.isfile(directory):
                    path_log(logger, "{}: {} exists, but is a file instead of a directory".format(type,
    directory))
                    fullpath = False
            else:
                owner = find_owner(directory)
                if "r" in perms and not os.access(directory, os.R_OK):
                    path_log(logger, "{}: {} exists, but is not readable, owner: {}".format(type, directory, owner))
                    fullpath = False
                if "w" in perms and not os.access(directory, os.W_OK):
                    path_log(logger, "{}: {} exists, but is not writeable, owner: {}".format(type, directory, owner))
                    fullpath = False
                if "x" in perms and not os.access(directory, os.X_OK):
                    path_log(logger, "{}: {} exists, but is not executable, owner: {}".format(type, directory, owner))
                    fullpath = False
        if fullpath is True:
            owner = find_owner(path)
            user = pwd.getpwuid(os.getuid()).pw_name
            if owner != user:
                path_log(logger, "{}: {} is owned by {} but appdaemon is running as {}".format(type, path, owner, user))

        if file is not None:
            owner = find_owner(file)
            if "r" in perms and not os.access(file, os.R_OK):
                path_log(logger, "{}: {} exists, but is not readable, owner: {}".format(type, file, owner))
            if "w" in perms and not os.access(file, os.W_OK):
                path_log(logger, "{}: {} exists, but is not writeable, owner: {}".format(type, file, owner))
            if "x" in perms and not os.access(file, os.X_OK):
                path_log(logger, "{}: {} exists, but is not executable, owner: {}".format(type, file, owner))
    except KeyError:
        #
        # User ID is not properly set up with a username in docker variants
        # getpwuid() errors out with a KeyError
        # We just have to skip most of these tests
        pass


def path_log(logger, msg):
    if logger is None:
        print(msg)
    else:
        log(logger, "WARNING", msg)