import json
import os
from datetime import datetime, timedelta, time as dt_time

from utils.base import App, toggle


class Schedule(App):
    async def initialize(self):
        await super().initialize()
        time = dt_time(17, 00, 0)
        await self.run_daily(self.schedule_events, time)

    @toggle("schedule")
    async def schedule_events(self, *args, **kwargs):
        current_date = datetime.now().date()

        with open(
            "conf/apps/schedule/schedule.json"
            if os.environ.get("DEV") == "true"
            else "/config/appdaemon/apps/apps/schedule/schedule.json",
            "r",
        ) as f:
            if current_date.weekday() >= 5:
                events = json.load(f)["weekend"]
            else:
                events = json.load(f)["workday"]

        event_items = list(events.items())
        first_item = event_items[0]
        event_items.append(first_item)

        prev_time = None
        prev_event = None
        for time_str, event in event_items:
            time = datetime.strptime(time_str, "%H:%M").time()
            if prev_time and time < prev_time.time():
                current_date += timedelta(days=1)

            dt = datetime.combine(current_date, time)
            if prev_event:
                end_dt = dt
                await self.call_service(
                    "calendar/create_event",
                    summary=prev_event,
                    start_date_time=prev_time.isoformat(),
                    end_date_time=end_dt.isoformat(),
                    entity_id="calendar.slots",
                    return_result=True,
                )

            prev_time = dt
            prev_event = event
