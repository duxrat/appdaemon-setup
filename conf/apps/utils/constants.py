import os

date_format = "%Y-%m-%d %H:%M:%S"

local_path = "conf/" if os.environ.get("DEV") == "true" else "/home/yepdev/apps/appdaemon/conf/"
