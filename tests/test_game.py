import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from game import Game, format_clock, PERIOD_OPTIONS


def started_game(period_choice=9):
    """A game past the config screen, at time 0."""
    game = Game()
    game.period_choice = period_choice
    game.handle("StartStop", 0)  # confirm config screen
    game.period_length = PERIOD_OPTIONS[period_choice]
    game.clock_base = float(game.period_length)
    return game


class FormatClockTest(unittest.TestCase):
    def test_minutes_and_seconds(self):
        self.assertEqual(format_clock(600), "10:00")
        self.assertEqual(format_clock(599.01), "10:00")  # rounded up
        self.assertEqual(format_clock(599.0), "09:59")
        self.assertEqual(format_clock(60.0), "01:00")

    def test_tenths_in_last_minute(self):
        self.assertEqual(format_clock(59.95), "01:00")  # 59.95 rounds up to 60.0
        self.assertEqual(format_clock(59.9), "59.9")
        self.assertEqual(format_clock(12.41), "12.5")
        self.assertEqual(format_clock(0.01), "0.1")
        self.assertEqual(format_clock(0), "0.0")

    def test_without_tenths(self):
        self.assertEqual(format_clock(12.41, tenths=False), "00:13")
        self.assertEqual(format_clock(0, tenths=False), "00:00")


class ClockTest(unittest.TestCase):
    def test_runs_and_stops_without_losing_fractions(self):
        game = started_game()
        game.handle("StartStop", 100)
        self.assertAlmostEqual(game.remaining(103.3), 596.7)
        game.handle("StartStop", 103.3)
        self.assertAlmostEqual(game.remaining(200), 596.7)  # stopped: no time passes
        game.handle("StartStop", 200)
        self.assertAlmostEqual(game.remaining(200.7), 596.0)

    def test_end_of_period_signals_once(self):
        game = started_game(0)  # 1 minute
        game.handle("StartStop", 0)
        self.assertFalse(game.tick(59.9))
        self.assertTrue(game.tick(60.05))  # a slow frame past 0 still ends the period
        self.assertFalse(game.running)
        self.assertEqual(game.clock_text(60.05), "0.0")
        self.assertFalse(game.tick(60.1))
        self.assertFalse(game.tick(70))

    def test_pause_counter_after_end(self):
        game = started_game(0)
        game.handle("StartStop", 0)
        game.tick(60)
        self.assertEqual(game.pause_text(60), "00:00")
        self.assertEqual(game.pause_text(135.5), "01:15")

    def test_restart_timer_only_when_stopped(self):
        game = started_game()
        game.handle("StartStop", 0)
        game.handle("RestartTimer", 10)
        self.assertAlmostEqual(game.remaining(10), 590)
        game.handle("StartStop", 10)
        game.handle("RestartTimer", 10)
        self.assertEqual(game.remaining(10), 600)

    def test_new_game_from_period_zero(self):
        game = started_game(5)
        game.score["Home"] = 20
        game.handle("Periode-", 0)
        game.handle("RestartTimer", 0)
        self.assertTrue(game.startup_screen)
        self.assertEqual(game.score["Home"], 0)
        self.assertEqual(game.period, 1)
        self.assertEqual(game.period_choice, 5)  # period length is kept


class ConfigScreenTest(unittest.TestCase):
    def test_choose_period_length(self):
        game = Game()
        self.assertEqual(game.period_length, 600)
        for _ in range(20):
            game.handle("Periode-", 0)
        self.assertEqual(game.period_length, 60)
        game.handle("Periode+", 0)
        self.assertEqual(game.remaining(0), 120)
        game.handle("ScoreHome+", 0)  # ignored on the config screen
        game.handle("StartStop", 0)
        self.assertFalse(game.startup_screen)
        self.assertEqual(game.score["Home"], 0)
        self.assertFalse(game.running)


class ScoreAndFoulsTest(unittest.TestCase):
    def test_never_below_zero(self):
        game = started_game()
        for command in ("ScoreHome-", "FoulAway-"):
            game.handle(command, 0)
        game.handle("ScoreAway+", 0)
        game.handle("ScoreAway+", 0)
        game.handle("FoulHome+", 0)
        self.assertEqual(game.score, {"Home": 0, "Away": 2})
        self.assertEqual(game.fouls, {"Home": 1, "Away": 0})

    def test_possession_cycle(self):
        game = started_game()
        states = []
        for _ in range(3):
            game.handle("Possession", 0)
            states.append(game.possession)
        self.assertEqual(states, [1, 2, 1])


class PeriodTest(unittest.TestCase):
    def test_fouls_reset_in_regular_periods_only(self):
        game = started_game()
        for period in (2, 3, 4):
            game.fouls["Home"] = 3
            game.handle("Periode+", 0)
            self.assertEqual(game.period, period)
            self.assertEqual(game.fouls["Home"], 0)
        game.fouls["Home"] = 3
        game.handle("Periode+", 0)
        self.assertEqual(game.fouls["Home"], 3)  # overtime: fouls continue

    def test_overtime_is_half_a_period_and_shown_as_e(self):
        game = started_game()
        for _ in range(4):
            game.handle("Periode+", 0)
        self.assertEqual(game.period_length, 300)
        self.assertEqual(game.period_text(), "E")
        game.handle("Periode-", 0)
        self.assertEqual(game.period_length, 600)
        self.assertEqual(game.period_text(), "4")

    def test_youth_games_count_periods(self):
        game = started_game(5)  # 6 min: U8, 8 quarters
        for _ in range(4):
            game.handle("Periode+", 0)
        self.assertEqual(game.period_length, 360)
        self.assertEqual(game.period_text(), "5")


class TimeOutTest(unittest.TestCase):
    def take(self, game, team, now=0):
        before = game.timeouts[team]
        game.handle("TimeOut" + team, now)
        taken = game.timeouts[team] > before
        game.timeout_started_at = None  # end it immediately for the next one
        return taken

    def test_limits_per_half_and_overtime(self):
        game = started_game()
        self.assertEqual([self.take(game, "Home") for _ in range(3)], [True, True, False])
        game.handle("Periode+", 0)
        game.handle("Periode+", 0)  # period 3: time-outs reset
        self.assertEqual(game.timeouts["Home"], 0)
        self.assertEqual([self.take(game, "Home") for _ in range(4)], [True, True, True, False])
        game.handle("Periode+", 0)
        game.handle("Periode+", 0)  # overtime: 1
        self.assertEqual([self.take(game, "Away") for _ in range(2)], [True, False])

    def test_not_while_clock_runs_or_at_zero(self):
        game = started_game()
        game.handle("StartStop", 0)
        self.assertFalse(self.take(game, "Home", 5))
        game.handle("StartStop", 5)
        game.clock_base = 0.0
        self.assertFalse(self.take(game, "Home", 5))

    def test_max_two_in_last_two_minutes(self):
        game = started_game()
        for _ in range(3):
            game.handle("Periode+", 0)
        game.clock_base = 120.0
        self.assertEqual([self.take(game, "Home") for _ in range(3)], [True, True, False])
        # One taken before the last 2 minutes does not count for the 2
        game = started_game()
        for _ in range(3):
            game.handle("Periode+", 0)
        game.clock_base = 300.0
        self.assertTrue(self.take(game, "Away"))
        game.clock_base = 100.0
        self.assertEqual([self.take(game, "Away") for _ in range(2)], [True, True])

    def test_last_two_minutes_rule_not_for_youth_games(self):
        game = started_game(5)
        for _ in range(3):
            game.handle("Periode+", 0)
        game.clock_base = 60.0
        self.assertEqual([self.take(game, "Home") for _ in range(3)], [True, True, True])

    def test_signals_once_at_ten_seconds_and_at_the_end(self):
        game = started_game()
        game.handle("TimeOutHome", 0)
        self.assertTrue(game.timeout_running)
        self.assertFalse(game.handle("StartStop", 1))  # clock cannot start during a time-out
        self.assertFalse(game.running)
        signals = [t / 10 for t in range(0, 700) if game.tick(t / 10)]
        self.assertEqual(signals, [50.0, 60.0])
        self.assertFalse(game.timeout_running)


class SaveRestoreTest(unittest.TestCase):
    def test_round_trip_through_json_with_clock_stopped(self):
        game = started_game()
        game.score["Home"] = 12
        game.handle("Periode+", 0)
        game.handle("StartStop", 0)
        state = json.loads(json.dumps(game.to_dict(42.5)))

        restored = Game()
        restored.load_dict(state, 1000)
        self.assertFalse(restored.startup_screen)
        self.assertEqual(restored.score["Home"], 12)
        self.assertEqual(restored.period, 2)
        self.assertFalse(restored.running)
        self.assertAlmostEqual(restored.remaining(1000), 557.5)

    def test_running_timeout_continues(self):
        game = started_game()
        game.handle("TimeOutHome", 100)
        restored = Game()
        restored.load_dict(json.loads(json.dumps(game.to_dict(110))), 120)
        self.assertEqual(restored.timeout_left(120), 40)

    def test_times_dropped_after_reboot(self):
        game = started_game()
        game.handle("TimeOutHome", 5000)
        restored = Game()
        restored.load_dict(json.loads(json.dumps(game.to_dict(5010))), 30)  # monotonic restarted at boot
        self.assertFalse(restored.timeout_running)
        self.assertEqual(restored.timeouts["Home"], 1)


if __name__ == "__main__":
    unittest.main()
