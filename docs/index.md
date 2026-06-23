# ovos-skill-music-assistant

An OCP (OVOS Common Play) **search skill** for
[Music Assistant](https://www.music-assistant.io/). It answers
`ovos.common_play.query` with playable results from a Music Assistant server.

## How it works

```
"play worms on music assistant"
        │
        ▼
  OCP pipeline ──▶ ovos.common_play.query
        │
        ▼
  @ocp_search search_mass(phrase, media_type)
        │  api.search_media(phrase)  (via py-music-assistant)
        ▼
  ovos.common_play.query.response  (MediaEntry list, uri=library://…)
        │
        ▼
  OCP selects a winner ──▶ ovos-media-plugin-mass plays the library:// uri
```

- The skill extends `OVOSCommonPlaybackSkill` and registers `search_mass`
  (`@ocp_search`) and `featured_media` (`@ocp_featured_media`).
- It supports `MUSIC`, `RADIO`, `AUDIOBOOK`, `PODCAST` and `GENERIC` queries,
  scoring each Music Assistant result (track / album / artist / radio / podcast /
  audiobook) with `fuzzy_match` plus vocab/favorite bonuses.
- Results carry Music Assistant `library://…` uris, which the companion
  [ovos-media-plugin-mass](https://github.com/OpenVoiceOS/ovos-media-plugin-mass)
  backend resolves and plays.

All server access is delegated to the
[py-music-assistant](https://github.com/TigreGotico/py-music-assistant) client.

## Relationship to ovos-media

On the modern `ovos-media` stack the catalog/search role is served in-process by
the [ovos-media-provider-mass](https://github.com/OpenVoiceOS/ovos-media-provider-mass)
MediaProvider. This skill is the equivalent for the legacy OCP/`ovos-audio` stack
and is maintained alongside the provider during the transition.

## Configuration

Set the Music Assistant server URL in the skill settings:

```json
{ "url": "http://192.168.1.100:8095" }
```

## Testing

```bash
pip install -e .[test]
pytest test/                 # unit (test/test_search.py) + e2e (test/end2end/)
```

The end-to-end tests load the skill in a MiniCroft with the real
`ovos-ocp-pipeline-plugin`, fire an utterance, and assert the full
utterance → query → response → `ocp:play` flow. The Music Assistant client is
mocked, so no server is required.
