import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from network import KICK_DELAY, arp_lookup, idle_stations, parse_commands, parse_stations


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


ARP_TABLE = """IP address       HW type     Flags       HW address            Mask     Device
10.5.141.3       0x1         0x2         20:9b:a9:68:9e:20     *        wlan0
10.5.141.4       0x1         0x0         00:00:00:00:00:00     *        wlan0
192.168.0.1      0x1         0x2         d8:cf:61:43:a3:fd     *        eth0
"""


class ArpLookupTest(unittest.TestCase):
    def test_finds_mac_and_interface(self):
        self.assertEqual(arp_lookup("10.5.141.3", ARP_TABLE), ("20:9b:a9:68:9e:20", "wlan0"))

    def test_unknown_or_incomplete_entry(self):
        self.assertIsNone(arp_lookup("10.5.141.9", ARP_TABLE))
        self.assertIsNone(arp_lookup("10.5.141.4", ARP_TABLE))


class IdleStationsTest(unittest.TestCase):
    def test_parse_all_sta(self):
        output = "20:9b:a9:68:9e:20\nflags=[AUTH][ASSOC][AUTHORIZED]\naid=0\naa:bb:cc:dd:ee:ff\ntimeout_next=NULLFUNC POLL\n"
        self.assertEqual(parse_stations(output), {"20:9b:a9:68:9e:20", "aa:bb:cc:dd:ee:ff"})

    def test_station_without_connection_is_logged_off_after_delay(self):
        idle = {}
        remote = {"20:9b:a9:68:9e:20"}
        self.assertEqual(idle_stations(idle, remote, set(), 100), [])
        self.assertEqual(idle_stations(idle, remote, set(), 100 + KICK_DELAY), [])
        self.assertEqual(idle_stations(idle, remote, set(), 101 + KICK_DELAY), ["20:9b:a9:68:9e:20"])

    def test_connecting_in_time_resets_the_wait(self):
        idle = {}
        remote = {"20:9b:a9:68:9e:20"}
        idle_stations(idle, remote, set(), 100)
        self.assertEqual(idle_stations(idle, remote, remote, 110), [])  # connected
        self.assertEqual(idle_stations(idle, remote, set(), 120), [])  # lost again: the wait starts over
        self.assertEqual(idle_stations(idle, remote, set(), 121 + KICK_DELAY), ["20:9b:a9:68:9e:20"])

    def test_station_that_left_is_forgotten(self):
        idle = {}
        idle_stations(idle, {"20:9b:a9:68:9e:20"}, set(), 100)
        idle_stations(idle, set(), set(), 105)
        self.assertEqual(idle, {})


if __name__ == "__main__":
    unittest.main()
