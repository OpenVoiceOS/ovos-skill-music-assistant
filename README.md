# <img src='./res/mass.png' card_color='#40DBB0' width='50' height='50' style='vertical-align:bottom'/> Music Assistant Skill

OCP search skill for [Music Assistant](https://www.music-assistant.io/).

It answers OCP `play …` requests with playable results from a Music Assistant
server. Playback of the returned `library://` uris is handled by the companion
[ovos-media-plugin-mass](https://github.com/OpenVoiceOS/ovos-media-plugin-mass).

On the modern `ovos-media` stack the catalog/search role is served by the
[ovos-media-provider-mass](https://github.com/OpenVoiceOS/ovos-media-provider-mass)
MediaProvider; this skill is the equivalent for the legacy OCP/`ovos-audio` stack.

## Configure

Set your Music Assistant server URL in the skill settings (`settings.json`):

```json
{ "url": "http://192.168.1.100:8095" }
```

## Related projects

- [ovos-media-plugin-mass](https://github.com/OpenVoiceOS/ovos-media-plugin-mass) — Music Assistant playback backend
- [ovos-media-provider-mass](https://github.com/OpenVoiceOS/ovos-media-provider-mass) — Music Assistant MediaProvider (ovos-media stack)
- [py-music-assistant](https://github.com/TigreGotico/py-music-assistant) — shared HTTP client + mediavocab bridge

## Docs

- [docs/index.md](docs/index.md) — overview, search flow, testing

## Credits
- JarbasAi

## Category
**Entertainment**

## Tags
#audio
#music
#OCP
#entertainment
