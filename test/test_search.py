"""Unit tests for the Music Assistant skill's OCP search scoring (network-free)."""
from unittest.mock import MagicMock, patch

import requests
from music_assistant_models.errors import MusicAssistantError
from ovos_utils.fakebus import FakeBus
from ovos_utils.ocp import MediaType, MediaEntry, Playlist

import ovos_skill_music_assistant as mod

from test.fixtures import SKILL_ID, SEARCH_RESULT, RECENTLY_PLAYED


def _skill(search_result=None, recently=None):
    skill = mod.MusicAssistantSkill(bus=FakeBus(), skill_id=SKILL_ID)
    client = MagicMock()
    client.search_media.return_value = search_result if search_result is not None else SEARCH_RESULT
    client.recently_played.return_value = recently if recently is not None else RECENTLY_PLAYED
    return skill, client


def _search(skill, client, phrase, media_type):
    with patch.object(mod, "SimpleHTTPMusicAssistantClient", return_value=client):
        return list(skill.search_mass(phrase, media_type))


def test_token_reaches_client_constructor():
    skill = mod.MusicAssistantSkill(bus=FakeBus(), skill_id=SKILL_ID)
    skill.settings["token"] = "sekrit-token"
    with patch.object(mod, "SimpleHTTPMusicAssistantClient") as mock_client:
        assert skill.api is mock_client.return_value
    mock_client.assert_called_once_with("http://localhost:8095", token="sekrit-token")


def test_no_token_passes_none_to_client_constructor():
    skill = mod.MusicAssistantSkill(bus=FakeBus(), skill_id=SKILL_ID)
    skill.settings["token"] = None
    with patch.object(mod, "SimpleHTTPMusicAssistantClient") as mock_client:
        assert skill.api is mock_client.return_value
    mock_client.assert_called_once_with("http://localhost:8095", token=None)


def test_music_search_returns_media_entries():
    skill, client = _skill()
    results = _search(skill, client, "worms", MediaType.MUSIC)
    assert results
    assert all(isinstance(r, MediaEntry) for r in results)
    assert all(r.uri.startswith("library://") for r in results)
    # exact title match outranks the partial one
    by_title = {r.title: r.match_confidence for r in results}
    assert by_title["Worms"] > by_title["Food for the Worms"]


def test_generic_search_spans_all_media_types():
    skill, client = _skill()
    results = _search(skill, client, "worms", MediaType.GENERIC)
    kinds = {r.media_type for r in results}
    # the audiobook/podcast scorers are wired (previously routed through radio)
    assert MediaType.MUSIC in kinds
    assert MediaType.RADIO in kinds
    assert MediaType.PODCAST in kinds
    assert MediaType.AUDIOBOOK in kinds


def test_radio_search_only_returns_radio():
    skill, client = _skill()
    results = _search(skill, client, "worm radio", MediaType.RADIO)
    assert results
    assert all(r.media_type == MediaType.RADIO for r in results)


def test_unplayable_results_are_skipped():
    skill, client = _skill(search_result={
        "tracks": [{"media_type": "track", "name": "Nope", "uri": "library://track/1",
                    "is_playable": False, "favorite": False, "artists": [{"name": "x"}]}],
        "artists": [], "albums": [], "radio": [], "podcasts": [], "audiobooks": [],
    })
    assert _search(skill, client, "nope", MediaType.MUSIC) == []


def test_mass_vocab_boosts_score():
    skill, client = _skill()
    plain = _search(skill, client, "worms", MediaType.MUSIC)
    boosted = _search(skill, client, "worms on music assistant", MediaType.MUSIC)
    plain_worms = next(r for r in plain if r.title == "Worms")
    boosted_worms = next(r for r in boosted if r.title == "Worms")
    assert boosted_worms.match_confidence >= plain_worms.match_confidence


def test_search_succeeds_when_server_is_reachable():
    """Regression check: a healthy server still yields results as before."""
    skill, client = _skill()
    with patch.object(mod, "SimpleHTTPMusicAssistantClient", return_value=client), \
            patch.object(skill, "speak_dialog") as speak_dialog:
        results = list(skill.search_mass("worms", MediaType.MUSIC))
    assert results
    assert all(isinstance(r, MediaEntry) for r in results)
    speak_dialog.assert_not_called()


def test_connection_failure_speaks_unreachable_dialog_once():
    skill, client = _skill()
    client.search_media.side_effect = requests.exceptions.ConnectionError("boom")
    with patch.object(mod, "SimpleHTTPMusicAssistantClient", return_value=client), \
            patch.object(skill, "speak_dialog") as speak_dialog:
        results = list(skill.search_mass("worms", MediaType.MUSIC))
    assert results == []
    speak_dialog.assert_called_once_with("mass.unreachable")


def test_server_error_speaks_error_dialog_once():
    skill, client = _skill()
    client.search_media.side_effect = MusicAssistantError("server refused")
    with patch.object(mod, "SimpleHTTPMusicAssistantClient", return_value=client), \
            patch.object(skill, "speak_dialog") as speak_dialog:
        results = list(skill.search_mass("worms", MediaType.MUSIC))
    assert results == []
    speak_dialog.assert_called_once_with("mass.error")


def test_featured_media_returns_playlist():
    skill, client = _skill()
    with patch.object(mod, "SimpleHTTPMusicAssistantClient", return_value=client):
        pl = skill.featured_media()
    assert isinstance(pl, Playlist)
    assert len(pl) == 1
