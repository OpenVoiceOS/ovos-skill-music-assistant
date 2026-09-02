> # ⚠️ DEPRECATED
>
> This OCP **search skill** is deprecated and unmaintained. OCP search skills
> (`OVOSCommonPlaybackSkill` + `@ocp_search`) are replaced by **MediaProvider**
> plugins loaded by the OCP pipeline plugin. The search and catalog functionality
> moves to [`ovos-media-provider-mass`](https://github.com/OpenVoiceOS/ovos-media-provider-mass),
> a MediaProvider running in-process within the OCP pipeline.
> Playback of Music Assistant tracks moves to
> [`ovos-media-plugin-mass`](https://github.com/OpenVoiceOS/ovos-media-plugin-mass),
> a playback backend for the `ovos-media` player daemon.
> Both packages are published and work once their respective stacks are active —
> `ovos-media-provider-mass` provides search results when the OCP pipeline
> invokes MediaProviders; `ovos-media-plugin-mass` handles playback when
> `ovos-media` is running as your player. Installing them does not replace this skill
> under the legacy OCP/`ovos-audio` stack.
>
> - **How MediaProviders work / how to migrate:** https://github.com/OpenVoiceOS/ovos-media/blob/dev/docs/media-providers.md
> - **Base-class deprecation:** [ovos-workshop#423](https://github.com/OpenVoiceOS/ovos-workshop/pull/423)
>
> This skill keeps working until the `ovos-media` stack flips to default and
> this repository is archived.

# <img src='./res/mass.png' card_color='#40DBB0' width='50' height='50' style='vertical-align:bottom'/> Music Assistant Skill

OCP search skill for [Music Assistant](https://www.music-assistant.io/).

It answers OCP `play …` requests with playable results from a Music Assistant
server. The companion
[ovos-media-plugin-mass](https://github.com/OpenVoiceOS/ovos-media-plugin-mass)
plays back the returned `library://` uris.

On the modern `ovos-media` stack, the
[ovos-media-provider-mass](https://github.com/OpenVoiceOS/ovos-media-provider-mass)
MediaProvider serves the catalog/search role. This skill is the equivalent for
the legacy OCP/`ovos-audio` stack.

## Configure

Set your Music Assistant server URL in the skill settings (`settings.json`):

```json
{ "url": "http://192.168.1.100:8095" }
```

## Related projects

- [ovos-media-plugin-mass](https://github.com/OpenVoiceOS/ovos-media-plugin-mass): Music Assistant playback backend
- [ovos-media-provider-mass](https://github.com/OpenVoiceOS/ovos-media-provider-mass): Music Assistant MediaProvider (ovos-media stack)
- [py-music-assistant](https://github.com/TigreGotico/py-music-assistant): shared HTTP client and mediavocab bridge

## Docs

- [docs/index.md](docs/index.md) — overview, search flow, and tests

## Tests

```bash
pip install -e .[test]
pytest test/                  # unit + end2end (ovoscope), network-free
```

The end-to-end tests ([test/end2end/](test/end2end/)) run the real OCP pipeline
in a `ovoscope` MiniCroft. A spoken utterance is classified into an
`ovos.common_play.query`, this skill answers, and OCP selects a winner to play.
The tests mock the Music Assistant HTTP client.

## Credits
- JarbasAi

## Category
**Entertainment**

## Tags
#audio
#music
#OCP
#entertainment
