from utils.base import App, args


class Music(App):
    def initialize(self):
        self.listen_state(self.idling, "input_select.category", new="Idling")
        self.listen_state(self.resume, "input_select.category", old="Idling")
        self.listen_state(self.unmuted, "media_player.desk", attribute="is_volume_muted")

    @args
    def idling(self):
        self.call_service("media_player/volume_mute", entity_id="media_player.desk", is_volume_muted=True)
        self.set_state("input_boolean.auto_muted", state="on")

    @args
    def resume(self):
        auto_muted = self.get_state("input_boolean.auto_muted")
        if auto_muted == "on":
            self.call_service("media_player/volume_mute", entity_id="media_player.desk", is_volume_muted=False)
        # todo: set auto_muted to false after starting the non-desk project

    @args
    def unmuted(self):
        category_state = self.get_state("input_select.category")
        if category_state == "Idling":
            self.call_service("media_player/volume_mute", entity_id="media_player.desk", is_volume_muted=True)
