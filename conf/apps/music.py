from utils.base import App, toggle


class Music(App):
    async def initialize(self):
        await super().initialize()
        await self.listen_state(self.idling, "input_select.category", new="Idling")
        await self.listen_state(self.resume, "input_select.category", old="Idling")
        await self.listen_state(self.unmuted, "media_player.desk", attribute="is_volume_muted")

    @toggle("music")
    async def idling(self, entity, attribute, old, new, kwargs):
        await self.call_service("media_player/volume_mute", entity_id="media_player.desk", is_volume_muted=True)
        await self.set_state("input_boolean.auto_muted", state="on")

    @toggle("music")
    async def resume(self, entity, attribute, old, new, kwargs):
        auto_muted = await self.get_state("input_boolean.auto_muted")
        if auto_muted == "on":
            await self.call_service("media_player/volume_mute", entity_id="media_player.desk", is_volume_muted=False)
        # todo: set auto_muted to false after starting the non-desk project

    @toggle("music")
    async def unmuted(self, entity, attribute, old, new, kwargs):
        category_state = await self.get_state("input_select.category")
        if category_state == "Idling":
            await self.call_service("media_player/volume_mute", entity_id="media_player.desk", is_volume_muted=True)
