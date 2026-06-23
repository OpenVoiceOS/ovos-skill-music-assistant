"""Shared Music Assistant search fixture for the skill tests."""

SKILL_ID = "ovos-skill-music-assistant.openvoiceos"

# A representative ``music/search`` response (one item per bucket).
SEARCH_RESULT = {
    "tracks": [{
        "media_type": "track", "name": "Worms", "uri": "library://track/9903",
        "is_playable": True, "favorite": True, "duration": 208,
        "artists": [{"name": "Viagra Boys"}], "album": {"name": "Street Worms"},
        "image": {"path": "https://art.example/worms.jpg", "remotely_accessible": True},
    }, {
        "media_type": "track", "name": "Food for the Worms", "uri": "library://track/2560",
        "is_playable": True, "favorite": False, "duration": 383,
        "artists": [{"name": "Exodus"}], "album": {"name": "Tempo of the Damned"},
    }],
    "artists": [{
        "media_type": "artist", "name": "Viagra Boys", "uri": "library://artist/77",
        "is_playable": True, "favorite": False,
    }],
    "albums": [{
        "media_type": "album", "name": "Street Worms", "uri": "library://album/1303",
        "is_playable": True, "favorite": False, "artists": [{"name": "Viagra Boys"}],
    }],
    "radio": [{
        "media_type": "radio", "name": "Worm Radio", "uri": "library://radio/42",
        "is_playable": True, "favorite": False,
    }],
    "podcasts": [{
        "media_type": "podcast", "name": "The Worm Cast", "uri": "library://podcast/7",
        "is_playable": True, "favorite": False,
    }],
    "audiobooks": [{
        "media_type": "audiobook", "name": "How to Train Your Worm",
        "uri": "library://audiobook/3", "is_playable": True, "favorite": False,
    }],
}

RECENTLY_PLAYED = [{
    "media_type": "track", "name": "Recent Hit", "uri": "library://track/55",
    "is_playable": True, "favorite": False, "duration": 200,
    "artists": [{"name": "Someone"}], "album": {"name": "An Album"},
}]
