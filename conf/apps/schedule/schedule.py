import json
import os
from datetime import datetime, timedelta, time as dt_time

from utils.base import App, toggle


class Schedule(App):
    async def initialize(self):
        await super().initialize()
        time = dt_time(2, 00, 0)
        await self.run_daily(self.schedule_events, time)

    @toggle("schedule")
    async def schedule_events(self, *args, **kwargs):
        current_date = datetime.now().date()
        weekday = current_date.weekday()

        with open(
            "conf/apps/schedule/schedule.json"
            if os.environ.get("DEV") == "true"
            else "/config/appdaemon/apps/apps/schedule/schedule.json",
            "r",
        ) as f:
            schedule_data = {k: list(v.items()) for k, v in json.load(f).items()}

        if weekday == 4:
            events = schedule_data["friday"]
            events.append(schedule_data["saturday"][0])
        elif weekday == 5:
            events = schedule_data["saturday"]
            events.append(schedule_data["sunday"][0])
        elif weekday == 6:
            events = schedule_data["sunday"]
            events.append(schedule_data["workday"][0])
        else:
            events = schedule_data["workday"]
            events.append(schedule_data["friday"][0])

        prev_time = None
        prev_event = None
        for time_str, event in events:
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
