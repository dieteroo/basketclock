# Club settings, read from club/config.ini. Missing settings fall back to the defaults below.
import configparser

DEFAULTS = {
    "club": {
        "logo": "club/logo.svg",
    },
    "display": {
        "resolution": "auto",  # "auto" = the TV's resolution, or e.g. 1280x720
        "tenths": "yes",  # show tenths of a second in the last minute
    },
    "remote": {
        "enabled": "yes",  # also shows the connection indicator on the screen
        "listen_ip": "10.3.141.1",
        "port": "8080",
    },
    "game": {
        "timeout_seconds": "60",
        "buzzer_pin": "16",
        "state_file": "/dev/shm/basketclock-state.json",  # in memory: survives a program restart, not a reboot
    },
}


def load_config(path):
    config = configparser.ConfigParser(inline_comment_prefixes=("#", ";"))
    config.read_dict(DEFAULTS)
    config.read(path)  # a missing file just leaves the defaults
    return config
