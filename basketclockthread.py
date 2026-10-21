# Basketball clock - main program: reads keyboard and remote, runs the game and draws the screen.
# Rules are in game.py, drawing in display.py, the remote server in network.py, settings in club/config.ini.
import json
import os
import sys
import threading
import time

import pygame # type: ignore

# Set the default path to the python directory
sourceFileDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(sourceFileDir)

from config import load_config
from display import Display
from game import Game
from network import RemoteServer

FPS = 20  # screen updates per second (tenths of a second need more than 10)

config = load_config('club/config.ini')
tenths = config.getboolean('display', 'tenths')

# Pygame library initiation
pygame.init()
display = Display(config.get('display', 'resolution'), config.get('club', 'logo'))

# Sound
EndSound = pygame.mixer.Sound('sounds/BUZZER.WAV')
try:
    from gpiozero import Buzzer # type: ignore
    buzzer = Buzzer(config.getint('game', 'buzzer_pin'))  # Connect your piezobuzzer to ground and the GPIO pin
except Exception as e:  # not on a Raspberry Pi (e.g. testing on a laptop): sound only
    print(f"No piezo buzzer: {e}")
    buzzer = None

def PiezoBuzzer():
    if buzzer:
        buzzer.on()
        time.sleep(0.5)
        buzzer.off()

def Signal(sound=True):
    """Buzzer (in a thread, so the display keeps updating) and optionally the sound over HDMI."""
    if sound:
        EndSound.play()
    threading.Thread(target=PiezoBuzzer, daemon=True).start()

# Keyboard key -> command mapping
KeyboardCommands = {
    pygame.K_SPACE: "StartStop",
    pygame.K_s: "ScoreHome+",
    pygame.K_x: "ScoreHome-",
    pygame.K_d: "FoulHome+",
    pygame.K_c: "FoulHome-",
    pygame.K_j: "ScoreAway+",
    pygame.K_n: "ScoreAway-",
    pygame.K_h: "FoulAway+",
    pygame.K_b: "FoulAway-",
    pygame.K_v: "Possession",
    pygame.K_y: "Periode+",
    pygame.K_r: "Periode-",
    pygame.K_e: "TimeOutHome",
    pygame.K_u: "TimeOutAway",
    pygame.K_t: "RestartTimer",
    pygame.K_g: "Buzzer",
}

def GetKeyboardInput():
    """Every command pressed since the last call, so no presses are dropped."""
    keystrokes = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key in KeyboardCommands:
            keystrokes.append(KeyboardCommands[event.key])
    return keystrokes

# Game state, restored when the program was restarted (e.g. after a crash) during a game
game = Game(config.getint('game', 'timeout_seconds'))
StateFile = config.get('game', 'state_file')
SavedState = None
try:
    with open(StateFile) as f:
        game.load_dict(json.load(f), time.monotonic())
    print("Restored the saved game")
except (OSError, ValueError) as e:
    print(f"No saved game restored: {e}")

def SaveState(now):
    global SavedState
    state = json.dumps(game.to_dict(now))
    if state != SavedState:
        try:
            with open(StateFile + ".tmp", "w") as f:
                f.write(state)
            os.replace(StateFile + ".tmp", StateFile)  # atomic, so a crash never leaves half a file
            SavedState = state
        except OSError as e:
            print(f"Cannot save the game: {e}")

# Start network thread
remote = None
if config.getboolean('remote', 'enabled'):
    remote = RemoteServer(config.get('remote', 'listen_ip'), config.getint('remote', 'port'))
    remote.start()

# SplashScreen (only on a fresh start, not when a game was restored)
if game.startup_screen:
    for step in range(10):
        display.splash(step)
        time.sleep(1)

# The actual program
clock = pygame.time.Clock()
while True:
    now = time.monotonic()

    commands = GetKeyboardInput()
    if remote:
        while not remote.commands.empty():
            commands.append(remote.commands.get_nowait())
    for command in commands:
        if game.handle(command, now):
            Signal(sound=False)  # manual buzzer

    if game.tick(now):
        Signal()

    connected = remote.connected > 0 if remote else None
    if game.startup_screen:
        display.config_screen(game.period_length, connected)
    else:
        display.scoreboard(game, now, tenths, connected)
    SaveState(now)
    clock.tick(FPS)
