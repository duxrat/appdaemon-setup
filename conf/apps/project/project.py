import json
import secrets
from datetime import timedelta, datetime
from time import time

import requests
from utils.base import App, args, e
from utils.constants import local_path

toggl_auth = (secrets.TOGGL, "api_token")


class Project(App):
    def __init__(self, *args, **kwargs):
        self.set_idling_handle = None
        self.estimate_end_handle = None
        self.vibrate_mid_band_handle = None
        super().__init__(*args, **kwargs)

    def initialize(self):
        self.projects_data()
        self.register_endpoint(self.projects_data, "projects_data")

        self.listen_event(self.stop_tracking, "stop_tracking")
        self.listen_event(self.start_tracking, "start_tracking")

        @self.listen(e("binary_sensor.idling"))
        def idling_changed(idling):
            if idling == "on":
                self.reset_estimation()
                self.vibrate_mid_band_handle = self.run_every(self.vibrate_mid_band, "now", 60)
                requests.get(
                    secrets.KM + "blackout-enable",
                    verify=False,
                )
            elif idling == "off" and self.vibrate_mid_band_handle:
                self.cancel_timer(self.vibrate_mid_band_handle, True)
                requests.get(
                    secrets.KM + "blackout-disable",
                    verify=False,
                )
                self.call_service("joaoapps_join/ha_send_tasker", command="ring_stop")

        idling_changed.run()

        @self.listen(e("input_datetime.task_estimate_end", immediate=True))
        def schedule_estimate_end(estimate_end):
            estimate_end = self.parse_datetime(estimate_end)
            now = self.datetime()
            if now > estimate_end + timedelta(minutes=1):
                self.set_idling()
            else:
                self.cancel_set_idling()
                self.cancel_estimate_end()
                self.estimate_end_handle = self.run_at(
                    self.vibrate_mid_band,
                    estimate_end,
                )
                self.set_idling_handle = self.run_at(self.set_idling, estimate_end + timedelta(minutes=1))

        schedule_estimate_end.run()

        @self.listen(e("input_select.project"))
        def project_changed(project):
            category = self.global_vars["categories"]["project_category"][project]
            self.select_option(
                "input_select.category",
                category,
            )
            self.set_state("binary_sensor.idling", state="on" if category == "Idling" else "off")
            if category not in ["Tech", "Work", "Tasks", "Research"]:
                self.set_textvalue("input_text.task", "")

            self.cancel_set_idling()

            if project not in self.global_vars["marvin"]["name_id"]:
                self.toggl_start_tracking(project, project)

        project_changed.run()

        @self.listen([e("input_select.category"), e("sensor.slot")])
        def slot_aligned(category, slot):
            with open(local_path + "project/project.json") as file:
                slot_categories = json.load(file)["slot_projects"]

            if category in slot_categories[slot]:
                state = 1
            elif slot == "Work" and category not in ["Tech", "Work"] or category == "Sleep":
                state = -1
            else:
                state = 0
            self.set_state("sensor.aligned", state=state)

        slot_aligned.run()

    @args
    def set_idling(self, *args):
        self.log("setting idling")
        # idling = self.get_state("binary_sensor.idling")
        # if not idling:
        self.select_option("input_select.project", "Idling")
        self.set_textvalue("input_text.task", "")
        self.log("set idling")

    def vibrate_mid_band(self, *args):
        heartrate = self.get_state("sensor.band_heartrate")
        if heartrate != "0":
            self.call_service("joaoapps_join/ha_send_tasker", command="vibrate_mid_band")

        estimate_end = self.get_state("input_datetime.task_estimate_end")
        estimate_end = self.parse_datetime(estimate_end)
        now = self.datetime()
        if estimate_end + timedelta(minutes=1.5) < now < estimate_end + timedelta(minutes=2.5):
            self.call_service("joaoapps_join/ha_send_tasker", command="ring")

    @args
    def reset_estimation(self):
        self.set_state("input_datetime.task_estimate_end", state=self.datetime_str())

    @args
    def start_tracking(self, event_name, data, cb_args):
        self.cancel_set_idling()
        marvin = self.global_vars["marvin"]

        project_id = data["payload"]["parentId"]
        project_name = marvin["id_name"][project_id]

        self.select_option("input_select.project", project_name)
        self.set_state("input_text.task", state=data["payload"]["title"])

        result = self.toggl_start_tracking(project_name, title=data["payload"]["title"])
        self.set_state("input_number.task_toggl_id", state=result["id"])

    @args
    def stop_tracking(self, event_name, data, cb_args):
        task = self.get_state("input_text.task")
        if data["payload"]["title"] == task:
            self.reset_estimation()

            self.cancel_set_idling()
            self.set_idling_handle = self.run_in(self.set_idling, 60)

    # -------------------- Utils --------------------

    def cancel_set_idling(self):
        if self.set_idling_handle:
            self.cancel_timer(self.set_idling_handle, True)
            self.set_idling_handle = None

    def cancel_estimate_end(self):
        if self.estimate_end_handle:
            self.cancel_timer(self.estimate_end_handle, True)
            self.estimate_end_handle = None

    def toggl_start_tracking(self, project_name, title):
        url = "https://api.track.toggl.com/api/v9/time_entries"
        payload = {
            "created_with": "Snowball",
            "pid": self.global_vars["toggl"]["name_id"][project_name],
            "description": title,
            "billable": False,
            "duration": int(time()) * -1,
            "wid": 6191651,
            "start": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "duronly": False,
            "server_deleted_at": None,
            "uid": 8268725,
            "user_id": 8268725,
            # "tags": [msg.area] # Uncomment and replace 'msg.area' as needed
        }

        response = requests.post(url, auth=toggl_auth, json=payload, verify=False)
        data = response.json()
        return data

    # -------------------- Endpoints --------------------

    def projects_data(self, *args):
        url = "https://serv.amazingmarvin.com/api/categories"
        headers = {"X-API-TOKEN": secrets.MARVIN}

        data = requests.get(url, headers=headers, verify=False).json()
        id_parent, name_id, id_name = {}, {}, {}

        for project in data:
            id, name, parent_id = project["_id"], project["title"], project["parentId"]
            id_parent[id] = parent_id
            name_id[name] = id
            id_name[id] = name

        id_name["unassigned"] = "none"
        name_id["none"] = "unassigned"
        self.global_vars["marvin"] = {"name_id": name_id, "id_name": id_name, "id_parent": id_parent}

        id_to_category = {
            60528535: "Work",
            60528540: "Social",
            60528544: "Food",
            60528545: "Chores",
            60528546: "Research",
            60528547: "Body",
            60528548: "Entertainment",
            60528550: "Tech",
            60528551: "Tinkering",
            60528552: "Mind",
            60528554: "Away",
            60528556: "Sleep",
            60528558: "Idling",
            60528560: "Tasks",
            60597776: "Fun",
            64452653: "Exploring",
        }
        response = requests.get(secrets.TOGGL_PROJECTS_URL, auth=toggl_auth, verify=False)
        data = response.json()

        name_id, id_name = {}, {}
        project_to_category = {}

        for project in data:
            id, name, client_id = project["id"], project["name"], project["client_id"]
            name_id[name] = id
            id_name[id] = name
            category = id_to_category.get(client_id)
            project_to_category[name] = category

        self.global_vars["toggl"] = {"name_id": name_id, "id_name": id_name}
        self.global_vars["categories"] = {
            "project_category": project_to_category,
        }
        # todo: migrate to server
        # if os.environ.get("DEV") != "true":
        #     with open("/config/www/project.json", "w") as file:
        #         converted = {
        #             key: {to_camel_case(inner_key): value for inner_key, value in inner_dict.items()}
        #             for key, inner_dict in self.global_vars.items()
        #         }
        #         file.write(json.dumps(converted, indent=2))
        return {}, 200


def to_camel_case(s):
    parts = s.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])
