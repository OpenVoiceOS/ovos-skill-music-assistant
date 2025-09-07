from os.path import join, dirname
from typing import Iterable, Dict, Any

from ovos_media_plugin_mass.music_assistant_client import SimpleHTTPMusicAssistantClient
from ovos_utils import classproperty
from ovos_utils.ocp import MediaType, PlaybackType, MediaEntry, Playlist
from ovos_utils.parse import fuzzy_match
from ovos_utils.process_utils import RuntimeRequirements
from ovos_workshop.decorators.ocp import ocp_search, ocp_featured_media
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill


class MusicAssistantSkill(OVOSCommonPlaybackSkill):

    def __init__(self, *args, **kwargs):
        super().__init__(supported_media=[MediaType.MUSIC,
                                          MediaType.RADIO,
                                          MediaType.AUDIOBOOK,
                                          MediaType.PODCAST,
                                          MediaType.GENERIC],
                         skill_icon=join(dirname(__file__), "res", "mass.png"),
                         skill_voc_filename="mass",
                         *args, **kwargs)

    @property
    def api(self) -> SimpleHTTPMusicAssistantClient:
        # NOTE: made a property so url can be changed without reloading skill
        url = self.settings.get("url")
        url = "http://100.88.41.41:8095"  # TODO - remove
        return SimpleHTTPMusicAssistantClient(url)

    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(internet_before_load=True,
                                   network_before_load=True,
                                   gui_before_load=False,
                                   requires_internet=True,
                                   requires_network=True,
                                   requires_gui=False,
                                   no_internet_fallback=False,
                                   no_network_fallback=False,
                                   no_gui_fallback=True)

    @ocp_featured_media()
    def featured_media(self) -> Playlist:
        pl = Playlist(media_type=MediaType.MUSIC,
                      title="Recently played (Music Assistant)",
                      playback=PlaybackType.AUDIO,
                      image=self.skill_icon,
                      skill_id=self.skill_id,
                      artist="Music Assistant",
                      match_confidence=100,
                      skill_icon=self.skill_icon)
        for entry in self.api.recently_played():
            if not entry.get("is_playable"):
                continue
            # TODO - retrieve more track data from api if needed
            pl.append(self._entry2media(entry, 100))
        return pl

    @ocp_search()
    def search_mass(self, phrase, media_type) -> Iterable[MediaEntry]:
        base_score = 0

        if self.voc_match(phrase, "mass"):
            base_score += 20  # explicit request
            phrase = self.remove_voc(phrase, "mass")

        res = self.api.search_media(phrase)

        if media_type in [MediaType.MUSIC, MediaType.GENERIC]:
            for entry in self._get_tracks(res["tracks"], phrase, base_score):
                yield entry
            for entry in self._get_artists(res["artists"], phrase, base_score):
                yield entry
            for entry in self._get_albums(res["albums"], phrase, base_score):
                yield entry
        if media_type in [MediaType.AUDIOBOOK, MediaType.GENERIC]:
            for entry in self._get_radios(res["audiobooks"], phrase, base_score):
                yield entry
        if media_type in [MediaType.PODCAST, MediaType.GENERIC]:
            for entry in self._get_radios(res["podcasts"], phrase, base_score):
                yield entry
        if media_type in [MediaType.RADIO, MediaType.GENERIC]:
            for entry in self._get_radios(res["radio"], phrase, base_score):
                yield entry

    # helpers to score results and yield OCP MediaEntry objects
    def _entry2media(self, entry: Dict[str, Any], score=50) -> MediaEntry:
        # find image url
        images = []
        if "image" in entry:
            images += [entry["image"]["path"]] if entry["image"]['remotely_accessible'] else []
        elif "metadata" in entry:
            images += [image["path"] for image in entry["metadata"].get("images") or []
                       if image['remotely_accessible']]

        # find artist
        if entry["media_type"] == "artist":
            artists = [entry["name"]]
        elif "artists" in entry:
            artists = [a["name"] for a in entry["artists"]]
        else:
            artists = []

        # find media type
        if entry["media_type"] == "podcast":
            media_type = MediaType.PODCAST
        elif entry["media_type"] == "audiobook":
            media_type = MediaType.AUDIOBOOK
        elif entry["media_type"] == "radio":
            media_type = MediaType.RADIO
        else:
            media_type = MediaType.MUSIC

        # modify name for playlist results
        if entry["media_type"] == "album":
            name = entry["name"] + " (Album)"
        elif entry["media_type"] == "artist":
            name = entry["name"] + " (Artist Playlist)"
        else:
            name = entry["name"]

        return MediaEntry(media_type=media_type,
                          uri=entry["uri"],
                          title=name,
                          playback=PlaybackType.AUDIO,
                          image=images[0] if images else self.skill_icon,
                          skill_id=self.skill_id,
                          artist=" & ".join(artists) if artists else "",
                          match_confidence=min(100, score),
                          length=entry.get("duration", -1),
                          skill_icon=self.skill_icon)

    def _get_albums(self, results, phrase, base_score, media_type: MediaType = MediaType.GENERIC) -> Iterable[
        MediaEntry]:
        for entry in results:
            if not entry["is_playable"]:
                continue
            bonus = 10 if entry["favorite"] else 0
            artist_name = entry["artists"][0]["name"]
            if self.voc_match(phrase, "album"):
                bonus += 15
            if artist_name.lower() in phrase.lower():
                bonus += 5
            if media_type == MediaType.MUSIC:
                bonus += 20
            elif media_type != MediaType.GENERIC:
                bonus -= 30
            artist_score = fuzzy_match(artist_name.lower(), phrase.lower()) * 100
            album_score = fuzzy_match(entry["name"].lower(), phrase.lower()) * 100
            score = round(base_score + bonus + artist_score + album_score)
            yield self._entry2media(entry, score)

    def _get_artists(self, results, phrase, base_score, media_type: MediaType = MediaType.GENERIC) -> Iterable[
        MediaEntry]:
        for entry in results:
            if not entry["is_playable"]:
                continue
            bonus = 10 if entry["favorite"] else 0
            if self.voc_match(phrase, "artist"):
                bonus += 15
            if media_type == MediaType.MUSIC:
                bonus += 20
            elif media_type != MediaType.GENERIC:
                bonus -= 30
            score = round(base_score + bonus + fuzzy_match(entry["name"].lower(), phrase.lower()) * 100)
            yield self._entry2media(entry, score)

    def _get_tracks(self, results, phrase, base_score, media_type: MediaType = MediaType.GENERIC) -> Iterable[
        MediaEntry]:
        for entry in results:
            if not entry["is_playable"]:
                continue
            bonus = 15 if entry["favorite"] else 0
            artist_name = entry["artists"][0]["name"]
            if self.voc_match(phrase, "track"):
                bonus += 15
            if artist_name.lower() in phrase.lower():
                bonus += 5
            if media_type == MediaType.MUSIC:
                bonus += 20
            elif media_type != MediaType.GENERIC:
                bonus -= 30
            artist_score = fuzzy_match(artist_name.lower(), phrase.lower()) * 100
            track_score = fuzzy_match(entry["name"].lower(), phrase.lower()) * 100
            score = round(base_score + bonus + artist_score + track_score)
            yield self._entry2media(entry, score)

    def _get_radios(self, results, phrase, base_score, media_type: MediaType = MediaType.GENERIC) -> Iterable[
        MediaEntry]:
        for entry in results:
            if not entry["is_playable"]:
                continue
            bonus = 10 if entry["favorite"] else 0
            if self.voc_match(phrase, "radio"):
                bonus += 15
            if media_type == MediaType.RADIO:
                bonus += 15
            elif media_type != MediaType.GENERIC:
                bonus -= 30
            score = round(base_score + bonus + fuzzy_match(entry["name"].lower(), phrase.lower()) * 100)
            yield self._entry2media(entry, score)

    def _get_audiobooks(self, results, phrase, base_score, media_type: MediaType = MediaType.GENERIC) -> Iterable[
        MediaEntry]:
        for entry in results:
            if not entry["is_playable"]:
                continue
            bonus = 10 if entry["favorite"] else 0
            if self.voc_match(phrase, "audiobook"):
                bonus += 15
            if media_type == MediaType.AUDIOBOOK:
                bonus += 15
            elif media_type != MediaType.GENERIC:
                bonus -= 30
            score = round(base_score + bonus + fuzzy_match(entry["name"].lower(), phrase.lower()) * 100)
            yield self._entry2media(entry, score)

    def _get_podcasts(self, results, phrase, base_score, media_type: MediaType = MediaType.GENERIC) -> Iterable[
        MediaEntry]:
        for entry in results:
            if not entry["is_playable"]:
                continue
            bonus = 10 if entry["favorite"] else 0
            if self.voc_match(phrase, "podcast"):
                bonus += 15
            if media_type == MediaType.PODCAST:
                bonus += 15
            elif media_type != MediaType.GENERIC:
                bonus -= 30
            score = round(base_score + bonus + fuzzy_match(entry["name"].lower(), phrase.lower()) * 100)
            yield self._entry2media(entry, score)


if __name__ == "__main__":
    from ovos_utils.fakebus import FakeBus
    from ovos_utils.log import LOG

    LOG.set_level("ERROR")

    s = MusicAssistantSkill(bus=FakeBus(), skill_id="t.fake")
    for r in s.search_mass("worms", MediaType.MUSIC):
        print(r)
        # MediaEntry(uri='library://track/9903', title='Worms', artist='Viagra Boys', match_confidence=100, skill_id='t.fake', playback=<PlaybackType.AUDIO: 2>, status=<TrackState.DISAMBIGUATION: 1>, media_type=<MediaType.MUSIC: 2>, length=208, image='/home/miro/PycharmProjects/ovos-skill-mass/res/mass.png', skill_icon='/home/miro/PycharmProjects/ovos-skill-mass/res/mass.png', javascript='')
        # MediaEntry(uri='library://track/2560', title='Food for the Worms', artist='Exodus', match_confidence=80, skill_id='t.fake', playback=<PlaybackType.AUDIO: 2>, status=<TrackState.DISAMBIGUATION: 1>, media_type=<MediaType.MUSIC: 2>, length=383, image='/home/miro/PycharmProjects/ovos-skill-mass/res/mass.png', skill_icon='/home/miro/PycharmProjects/ovos-skill-mass/res/mass.png', javascript='')
        # MediaEntry(uri='library://track/6014', title='Invared by Worms', artist='Dead Meat', match_confidence=62, skill_id='t.fake', playback=<PlaybackType.AUDIO: 2>, status=<TrackState.DISAMBIGUATION: 1>, media_type=<MediaType.MUSIC: 2>, length=191, image='/home/miro/PycharmProjects/ovos-skill-mass/res/mass.png', skill_icon='/home/miro/PycharmProjects/ovos-skill-mass/res/mass.png', javascript='')
        # MediaEntry(uri='library://track/2929', title='Worms Enchantress', artist='Acceptus Noctifer', match_confidence=55, skill_id='t.fake', playback=<PlaybackType.AUDIO: 2>, status=<TrackState.DISAMBIGUATION: 1>, media_type=<MediaType.MUSIC: 2>, length=271, image='/home/miro/PycharmProjects/ovos-skill-mass/res/mass.png', skill_icon='/home/miro/PycharmProjects/ovos-skill-mass/res/mass.png', javascript='')
        # MediaEntry(uri='library://track/6026', title='Invared by Worms', artist='Dead Meat', match_confidence=62, skill_id='t.fake', playback=<PlaybackType.AUDIO: 2>, status=<TrackState.DISAMBIGUATION: 1>, media_type=<MediaType.MUSIC: 2>, length=195, image='/home/miro/PycharmProjects/ovos-skill-mass/res/mass.png', skill_icon='/home/miro/PycharmProjects/ovos-skill-mass/res/mass.png', javascript='')
        # MediaEntry(uri='library://track/8052', title='Of Worms and Ruins', artist='Mayhem', match_confidence=62, skill_id='t.fake', playback=<PlaybackType.AUDIO: 2>, status=<TrackState.DISAMBIGUATION: 1>, media_type=<MediaType.MUSIC: 2>, length=228, image='/home/miro/PycharmProjects/ovos-skill-mass/res/mass.png', skill_icon='/home/miro/PycharmProjects/ovos-skill-mass/res/mass.png', javascript='')
        # MediaEntry(uri='library://track/6041', title='Worms Under My Skin', artist='Dead Meat', match_confidence=56, skill_id='t.fake', playback=<PlaybackType.AUDIO: 2>, status=<TrackState.DISAMBIGUATION: 1>, media_type=<MediaType.MUSIC: 2>, length=196, image='/home/miro/PycharmProjects/ovos-skill-mass/res/mass.png', skill_icon='/home/miro/PycharmProjects/ovos-skill-mass/res/mass.png', javascript='')
        # MediaEntry(uri='library://album/1303', title='Street Worms (Full Album)', artist='Viagra Boys', match_confidence=84, skill_id='t.fake', playback=<PlaybackType.AUDIO: 2>, status=<TrackState.DISAMBIGUATION: 1>, media_type=<MediaType.MUSIC: 2>, length=-1, image='/home/miro/PycharmProjects/ovos-skill-mass/res/mass.png', skill_icon='/home/miro/PycharmProjects/ovos-skill-mass/res/mass.png', javascript='')

    pl = s.featured_media()
    print(pl)
    for track in pl:
        print(track)
