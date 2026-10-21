# Game state and rules of the basketball clock.
# No pygame or hardware in here, so the rules can be tested on any computer (see tests/).
# All methods that need the time get it passed as `now` (time.monotonic() seconds).
import math
import re

# Commands from the keyboard and the remote
COMMANDS = (
    "StartStop", "RestartTimer", "Periode+", "Periode-", "Possession", "Buzzer",
    "ScoreHome+", "ScoreHome-", "ScoreAway+", "ScoreAway-",
    "FoulHome+", "FoulHome-", "FoulAway+", "FoulAway-",
    "TimeOutHome", "TimeOutAway",
)
TEAMS = ("Home", "Away")

PERIOD_OPTIONS = (60, 120, 180, 240, 300, 360, 420, 480, 540, 600, 660, 720)  # period lengths to choose from (s)
DEFAULT_PERIOD_CHOICE = 9  # 10 min
# From 10 min periods on it is a full game: overtime is shown as "E", overtime is half a period
# and the last 2 minutes time-out rule applies (shorter periods are youth games with more quarters)
FULL_GAME_CHOICE = 9
TIMEOUT_WARNING = 10  # signal this many seconds before the end of a time-out
LAST_MINUTES = 120  # last 2 minutes of the 4th period: max 2 time-outs per team
LAST_MINUTES_TIMEOUTS = 2
FOUL_PENALTY = 4  # from this many team fouls the next foul gives free throws (shown in red)

_SCORE_FOUL = re.compile(r"(Score|Foul)(Home|Away)([+-])$")


def format_clock(seconds, tenths=True):
    """MM:SS, or SS.t in the last minute. Rounded up, so 00:00 / 0.0 only shows when time is really up."""
    seconds = max(0.0, seconds)
    tenth_count = math.ceil(round(seconds * 10, 6))  # round() removes float noise like 59.900000001
    if tenths and tenth_count < 600:
        return f"{tenth_count // 10}.{tenth_count % 10}"
    whole = math.ceil(round(seconds, 6))
    return f"{whole // 60:02d}:{whole % 60:02d}"


class Game:
    def __init__(self, timeout_seconds=60):
        self.timeout_seconds = timeout_seconds
        self.period_choice = DEFAULT_PERIOD_CHOICE
        self.new_game()

    def new_game(self):
        """Back to the config screen with everything at zero (the chosen period length is kept)."""
        self.startup_screen = True
        self.score = dict.fromkeys(TEAMS, 0)
        self.fouls = dict.fromkeys(TEAMS, 0)
        self.timeouts = dict.fromkeys(TEAMS, 0)
        self.last_minutes_timeouts = dict.fromkeys(TEAMS, 0)
        self.period = 1
        self.possession = 0  # 0 = not set, 1 = home, 2 = away
        self.period_length = PERIOD_OPTIONS[self.period_choice]
        self.clock_base = float(self.period_length)  # remaining time when the clock was last started/stopped
        self.clock_started_at = None  # None = clock stopped
        self.end_signalled = False
        self.period_ended_at = None  # for the count-up pause timer
        self.timeout_started_at = None  # None = no time-out running
        self.timeout_warned = False

    # --- Clock ---

    @property
    def running(self):
        return self.clock_started_at is not None

    @property
    def timeout_running(self):
        return self.timeout_started_at is not None

    def remaining(self, now):
        if not self.running:
            return self.clock_base
        return max(0.0, self.clock_base - (now - self.clock_started_at))

    def timeout_left(self, now):
        if not self.timeout_running:
            return 0
        return max(0, math.ceil(round(self.timeout_seconds - (now - self.timeout_started_at), 6)))

    def full_game(self):
        return self.period_choice >= FULL_GAME_CHOICE

    def in_last_minutes(self, now):
        return self.full_game() and self.period == 4 and self.remaining(now) <= LAST_MINUTES

    def tick(self, now):
        """Advance the game to `now`. Returns True when the end signal (buzzer + sound) must be given."""
        signal = False
        if self.running and self.remaining(now) <= 0:
            self.clock_base = 0.0
            self.clock_started_at = None
        if self.clock_base <= 0 and not self.end_signalled:
            self.end_signalled = True
            self.period_ended_at = now
            signal = True
        if self.timeout_running:
            left = self.timeout_left(now)
            # Each signal is given once, also when a slow frame skips a second
            if not self.timeout_warned and left <= TIMEOUT_WARNING:
                self.timeout_warned = True
                signal = True
            if left <= 0:
                self.timeout_started_at = None
                signal = True
        return signal

    # --- Commands ---

    def handle(self, command, now):
        """Apply a keyboard/remote command. Returns True when the manual buzzer must sound."""
        if command == "Buzzer":
            return not self.startup_screen
        if self.startup_screen:
            self._handle_config(command)
            return False

        match = _SCORE_FOUL.match(command)
        if match:
            kind, team, sign = match.groups()
            counter = self.score if kind == "Score" else self.fouls
            counter[team] = max(0, counter[team] + (1 if sign == "+" else -1))
        elif command == "StartStop":
            if not self.timeout_running:
                if self.running:
                    self.clock_base = self.remaining(now)
                    self.clock_started_at = None
                else:
                    self.clock_started_at = now
        elif command == "Possession":
            self.possession = 0 if self.period == 0 else (2 if self.possession == 1 else 1)
        elif command == "Periode+":
            self.period += 1
            if self.period <= 4:
                self.fouls = dict.fromkeys(TEAMS, 0)
            if self.period == 3 or self.period >= 5:
                self.timeouts = dict.fromkeys(TEAMS, 0)
                self.last_minutes_timeouts = dict.fromkeys(TEAMS, 0)
            if self.period == 5:
                self.period_length = PERIOD_OPTIONS[self.period_choice]
                if self.full_game():
                    self.period_length = self.period_length / 2  # overtime
        elif command == "Periode-":
            if self.period >= 1:
                self.period -= 1
                if self.period == 4:
                    self.period_length = PERIOD_OPTIONS[self.period_choice]
        elif command in ("TimeOutHome", "TimeOutAway"):
            self._start_timeout(command[len("TimeOut"):], now)
        elif command == "RestartTimer":
            if not self.running:
                self.clock_base = float(self.period_length)
                self.end_signalled = False
                self.period_ended_at = None
                if self.period == 0:
                    self.new_game()
        return False

    def _handle_config(self, command):
        if command == "StartStop":
            self.startup_screen = False
        elif command == "Periode+":
            self.period_choice = min(self.period_choice + 1, len(PERIOD_OPTIONS) - 1)
        elif command == "Periode-":
            self.period_choice = max(self.period_choice - 1, 0)
        self.period_length = PERIOD_OPTIONS[self.period_choice]
        self.clock_base = float(self.period_length)

    def timeouts_allowed(self, team, now):
        """Can `team` take a time-out now (FIBA: 2 in the first half, 3 in the second half, 1 per overtime)?"""
        if self.running or self.timeout_running or self.remaining(now) <= 0:
            return False
        if self.period <= 2:
            limit = 2
        elif self.period <= 4:
            limit = 3
        else:
            limit = 1
        if self.timeouts[team] >= limit:
            return False
        if self.in_last_minutes(now) and self.last_minutes_timeouts[team] >= LAST_MINUTES_TIMEOUTS:
            return False
        return True

    def _start_timeout(self, team, now):
        if not self.timeouts_allowed(team, now):
            return
        if self.in_last_minutes(now):
            self.last_minutes_timeouts[team] += 1
        self.timeouts[team] += 1
        self.timeout_started_at = now
        self.timeout_warned = False

    # --- Display texts ---

    def clock_text(self, now, tenths=True):
        return format_clock(self.remaining(now), tenths)

    def period_text(self):
        if self.period >= 5 and self.full_game():
            return "E"
        return str(self.period)

    def pause_text(self, now):
        """Count-up time since the end of the period, "" while the period is not over."""
        if self.remaining(now) > 0 or self.period_ended_at is None:
            return ""
        return format_clock(int(now - self.period_ended_at), tenths=False)

    # --- Saving / restoring (so a restart of the program does not lose the game) ---

    _SAVED = ("startup_screen", "score", "fouls", "timeouts", "last_minutes_timeouts", "period", "possession",
              "period_choice", "period_length", "end_signalled", "period_ended_at",
              "timeout_started_at", "timeout_warned")

    def to_dict(self, now):
        state = {name: getattr(self, name) for name in self._SAVED}
        state["clock_base"] = self.remaining(now)  # restored with the clock stopped
        state["saved_at"] = now
        return state

    def load_dict(self, state, now):
        """Restore a saved game. Times are time.monotonic() values, which stay valid until a reboot."""
        for name in self._SAVED + ("clock_base",):
            if name in state:
                setattr(self, name, state[name])
        self.clock_started_at = None
        if state.get("saved_at", now + 1) > now:  # saved before a reboot: the saved times mean nothing now
            self.timeout_started_at = None
            self.period_ended_at = None
