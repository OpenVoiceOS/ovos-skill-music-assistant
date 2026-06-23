"""End-to-end OCP test for the Music Assistant skill (ovoscope).

Drives the **real** OCP pipeline: a ``recognizer_loop:utterance`` is classified by
``ovos-ocp-pipeline-plugin`` into an ``ovos.common_play.query``, the skill's
``@ocp_search`` handler answers with ``ovos.common_play.query.response`` messages,
and OCP selects a winner and emits ``ocp:play``. The Music Assistant HTTP client
is mocked, so no network or server is required.
"""
import time
import unittest
from unittest.mock import MagicMock, patch

from ovos_bus_client.message import Message

from ovoscope import get_minicroft, is_pipeline_available

import ovos_skill_music_assistant as mod

from test.fixtures import SKILL_ID, SEARCH_RESULT

OCP_PIPELINE = [
    "ovos-ocp-pipeline-plugin-high",
    "ovos-ocp-pipeline-plugin-medium",
    "ovos-ocp-pipeline-plugin-low",
]


class TestMusicAssistantOCP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not is_pipeline_available(OCP_PIPELINE):
            raise AssertionError(
                "ovos-ocp-pipeline-plugin is required for the OCP e2e tests "
                "(it is a declared test dependency)"
            )

    def setUp(self):
        self.minicroft = get_minicroft([SKILL_ID], default_pipeline=OCP_PIPELINE)
        self.client = MagicMock()
        self.client.search_media.return_value = SEARCH_RESULT

    def tearDown(self):
        if self.minicroft:
            self.minicroft.stop()

    def _say(self, utterance, lang="en-US", wait=3.0):
        captured = []
        self.minicroft.bus.on(
            "message",
            lambda m: captured.append(Message.deserialize(m) if isinstance(m, str) else m),
        )
        with patch.object(mod, "SimpleHTTPMusicAssistantClient", return_value=self.client):
            self.minicroft.bus.emit(Message(
                "recognizer_loop:utterance",
                {"utterances": [utterance], "lang": lang},
            ))
            time.sleep(wait)
        return captured

    def test_play_utterance_searches_and_plays(self):
        captured = self._say("play worms on music assistant")
        types = [m.msg_type for m in captured]

        # the skill answered the OCP query with playable results...
        responses = [m for m in captured
                     if m.msg_type == "ovos.common_play.query.response"
                     and m.data.get("results")]
        self.assertTrue(responses, "skill returned no OCP results for the utterance")
        for m in responses:
            for r in m.data["results"]:
                self.assertEqual(r["skill_id"], SKILL_ID)
                self.assertTrue(r["uri"].startswith("library://"))

        # ...and OCP selected a winner to play
        self.assertIn("ocp:play", types)

    def test_search_media_called_with_phrase(self):
        self._say("play worm radio on music assistant")
        self.assertTrue(self.client.search_media.called)
        phrase = self.client.search_media.call_args[0][0]
        self.assertIn("worm", phrase.lower())


if __name__ == "__main__":
    unittest.main()
