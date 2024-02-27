import os

date_format = "%Y-%m-%d %H:%M:%S"

# local_path = "conf/apps/" if os.environ.get("DEV") == "true" else "/home/yepdev/apps/appdaemon/conf/apps/"
local_path = "conf/apps/" if os.environ.get("DEV") == "true" else "/config/appdaemon/apps/apps/"
