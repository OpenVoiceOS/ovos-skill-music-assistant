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

## Setup

Check which player stack you run before installing anything. On the classic
`ovos-audio`/OCP stack, this skill does the catalog search and hands playback
to [ovos-media-plugin-mass](https://github.com/OpenVoiceOS/ovos-media-plugin-mass);
install both together. On the newer `ovos-media` stack, this skill is replaced
entirely at flag day by
[ovos-media-provider-mass](https://github.com/OpenVoiceOS/ovos-media-provider-mass),
which does catalog search and playback on its own — do not install this skill
there.

For the classic stack:

```bash
pip install ovos-skill-music-assistant ovos-media-plugin-mass
```

Set your Music Assistant server URL in this skill's settings — the
`url` field in `settings.json`, reachable through the OVOS control panel
under this skill's settings page:

```json
{ "url": "http://192.168.1.100:8095" }
```

Settings changes made through the control panel before the skill's first run
are only picked up on the run after that: the skill writes its own
first-run marker into `settings.json` the first time it loads, which can
overwrite a hand-edited file dropped in earlier. Reload the skill (or restart
it) once after changing the URL for the first time if it does not seem to
take effect.

Say "play some jazz on music assistant" to verify the setup works end to end.

If something goes wrong:

- an "I couldn't reach your Music Assistant server" reply means the `url` in
  settings is wrong or the server is down — check both.
- no results for something you know is in your library means Music Assistant
  itself does not have that media indexed — check its own search first.
- an error about the server refusing the request usually means authentication:
  Music Assistant 2.11 requires a token this skill does not yet send; support
  for it is coming with the next client release.

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
