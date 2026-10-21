import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from network import parse_commands


class ParseCommandsTest(unittest.TestCase):
    def test_newline_separated(self):
        self.assertEqual(parse_commands("Nothing\nScoreAway-\nPing\n"), (["Nothing", "ScoreAway-", "Ping"], ""))

    def test_old_remote_without_separator(self):
        self.assertEqual(parse_commands("ScoreHome+ScoreHome+"), (["ScoreHome+", "ScoreHome+"], ""))

    def test_command_split_over_two_packets(self):
        commands, rest = parse_commands("StartStop\nScoreHo")
        self.assertEqual((commands, rest), (["StartStop"], "ScoreHo"))
        self.assertEqual(parse_commands(rest + "me+\n"), (["ScoreHome+"], ""))

    def test_unknown_commands_are_dropped(self):
        self.assertEqual(parse_commands("bogus\nFoulAway+"), (["FoulAway+"], ""))
        self.assertEqual(parse_commands("bogus\nPerio"), ([], "Perio"))
        self.assertEqual(parse_commands("x" * 80), ([], ""))


if __name__ == "__main__":
    unittest.main()
