import pygame # type: ignore
import sys
import time
import math
import os
from time import sleep
import socket
import threading
from gpiozero import Buzzer # type: ignore
import select
import queue
import re

# Set the default path to the python directory
sourceFileDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(sourceFileDir)

# Pygame library initiation
pygame.init()
scr = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN)
pygame.display.set_caption('Basketbal Clock')
pygame.mouse.set_visible(0)

# Fonts
fontScore = pygame.font.Font('fonts/LED.ttf', 200)
fontScoreSmall = pygame.font.Font('fonts/LED.ttf', 90)
fontLabel = pygame.font.Font('fonts/DejaVuSans-Bold.ttf', 80)
fontLabelSmall = pygame.font.Font('fonts/DejaVuSans-Bold.ttf', 40)
fontLabelExtraSmall = pygame.font.Font('fonts/DejaVuSans-Bold.ttf', 30)

# Images
LogoClub = pygame.image.load('image/logo.svg')
Loading1 = pygame.image.load('image/loading1.svg')
Loading2 = pygame.image.load('image/loading2.svg')

# Colors
cyan = (100, 255, 255)
red = (255, 0, 0)
yellow = (255, 255, 0)
grey = (100, 100, 100)
black = (0, 0, 0)
white = (255, 255, 255)

# Text
textLabelHome = fontLabel.render('HOME', True, grey, black)
textLabelAway = fontLabel.render('AWAY', True, grey, black)
textLabelFouls = fontLabel.render('FOULS', True, grey, black)
textLabelPeriod = fontLabel.render('P', True, grey, black)
TimeOutText = ("", "*", "**", "***")
PauzeCounterString = ""
Extra = "E"

# All variables required for the clock
# time.monotonic() is used for all timing: time.time() jumps when NTP corrects the clock (the Pi has no RTC)
startTime = time.monotonic()
ResetCounter = 600
PauzeCounter = 0
StartCounter = ResetCounter  # Startcounter is reset to remaining time when clock is stopped
RemainingTime = ResetCounter
ClockPauze = True  # Check if the clock is active

# Game variables
ScoreHome = 0
ScoreAway = 0
FoulsHome = 0
FoulsAway = 0
TimeOutHome = 0
TimeOutAway = 0
Period = 1
Possession = 0

# TimeOut Variables
TimeOut = 60
TimeOutRunning = False
TimeOutRemaining = 0

# Sound variables
EndSound = pygame.mixer.Sound('sounds/BUZZER.WAV')
EndSoundPlayed = False  # required to only play 1 time
buzzer = Buzzer(16)  # Buzzer - Connect your piezobuzzer to ground and GPIO pin16
def PiezoBuzzer():
    buzzer.on()
    sleep(0.5)
    buzzer.off()

# StartupScreen Variables
StartupScreen = True  # allow configuration
ResetCounterOptions = (60, 120, 180, 240, 300, 360, 420, 480, 540, 600, 660, 720)
TimerChoice = 9  # to allow selection of the Timer - default = 10 min

# SplashScreen
scr.fill(black)
scr.blit(LogoClub, (350, 330))
pygame.display.flip()
Loading = 0
while Loading < 5:
    scr.blit(Loading1, (500, 460))
    pygame.display.flip()
    time.sleep(1)
    scr.blit(Loading2, (500, 460))
    pygame.display.flip()
    time.sleep(1)
    Loading += 1

# Function for the changing digits
def ScoreBoardUpdate(ScoreHome, ScoreAway, FoulsHome, FoulsAway, Clock, Period, TimeOutRemaining, PauzeCounterString, Possession):
    global textLabelHome, textLabelAway, textLabelFouls, textLabelPeriod

    textScoreHome = fontScore.render(str(ScoreHome), True, yellow, black)
    textScoreAway = fontScore.render(str(ScoreAway), True, yellow, black)
    textClock = fontScore.render(str(Clock), True, red, black)
    # Put the fouls in red if 4 to indicate free shots
    if FoulsHome < 4:
        textFoulsHome = fontScore.render(str(FoulsHome), True, yellow, black)
    else:
        textFoulsHome = fontScore.render(str(FoulsHome), True, red, black)
    if FoulsAway < 4:
        textFoulsAway = fontScore.render(str(FoulsAway), True, yellow, black)
    else:
        textFoulsAway = fontScore.render(str(FoulsAway), True, red, black)
    textTimeOut = fontScore.render(str(TimeOutRemaining), True, yellow, black)
    textPauzeCounter = fontScore.render(str(PauzeCounterString), True, yellow, black)
    # Put an "E" to indicate overtime
    if Period >= 5:
        if TimerChoice >= 9:
            textPeriod = fontScoreSmall.render(str(Extra), True, yellow, black)
        else:
            textPeriod = fontScoreSmall.render(str(Period), True, yellow, black)
    else:
        textPeriod = fontScoreSmall.render(str(Period), True, yellow, black)
    textTimeOutHome = fontScore.render(TimeOutText[TimeOutHome], True, yellow, black)
    textTimeOutAway = fontScore.render(TimeOutText[TimeOutAway], True, yellow, black)

    # Fixed text
    textRectLabelHome = textLabelHome.get_rect(center=(200, 50))
    textRectLabelAway = textLabelAway.get_rect(center=(1080, 50))
    textRectFoulsLabelHome = textLabelFouls.get_rect(center=(200, 480))
    textRectFoulsLabelAway = textLabelFouls.get_rect(center=(1080, 480))
    textRectLabelPeriod = textLabelPeriod.get_rect(center=(590, 50))

    # Variable text
    textRectScoreHome = textScoreHome.get_rect(center=(200, 200))
    textRectScoreAway = textScoreAway.get_rect(center=(1080, 200))
    textRectClock = textClock.get_rect(center=(640, 200))
    textRectFoulsHome = textFoulsHome.get_rect(center=(200, 600))
    textRectFoulsAway = textFoulsAway.get_rect(center=(1080, 600))
    textRectTimeOut = textTimeOut.get_rect(center=(640, 600))
    textRectPauzeCounter = textPauzeCounter.get_rect(center=(640, 600))
    textRectPeriod = textPeriod.get_rect(center=(670, 50))
    textRectTimeOutHome = textTimeOutHome.get_rect(center=(200, 350))
    textRectTimeOutAway = textTimeOutAway.get_rect(center=(1080, 350))

    scr.fill(black)
    scr.blit(textLabelHome, textRectLabelHome)
    scr.blit(textLabelAway, textRectLabelAway)
    scr.blit(textLabelFouls, textRectFoulsLabelHome)
    scr.blit(textLabelFouls, textRectFoulsLabelAway)
    scr.blit(textLabelPeriod, textRectLabelPeriod)
    scr.blit(textScoreHome, textRectScoreHome)
    scr.blit(textScoreAway, textRectScoreAway)
    scr.blit(textClock, textRectClock)
    scr.blit(textFoulsHome, textRectFoulsHome)
    scr.blit(textFoulsAway, textRectFoulsAway)
    if not TimeOutRemaining == 0:
        scr.blit(textTimeOut, textRectTimeOut)
    if not PauzeCounterString == "":
        scr.blit(textPauzeCounter, textRectPauzeCounter)
    scr.blit(textPeriod, textRectPeriod)
    scr.blit(textTimeOutHome, textRectTimeOutHome)
    scr.blit(textTimeOutAway, textRectTimeOutAway)
    scr.blit(LogoClub, (350, 330))
    if Possession == 1:
        pygame.draw.rect(scr, red, (420, 40, 50, 10))
        pygame.draw.polygon(scr, red, [(390, 45), (420, 75), (420, 15)])
    if Possession == 2:
        pygame.draw.rect(scr, red, (810, 40, 50, 10))
        pygame.draw.polygon(scr, red, [(890,45),(860,75),(860,15)])
    pygame.draw.rect(scr, cyan, (50, 110, 300, 200), 5)
    pygame.draw.rect(scr, cyan, (930, 110, 300, 200), 5)
    pygame.display.flip()

# Take actions depending on the feedback from any channel (keyboard, IO or network)
def HandleFeedback(keystroke):
    global ClockPauze, TimeOutRunning, TimeOutRemaining, ScoreHome, FoulsHome, ScoreAway, FoulsAway, Period, TimeOutHome, TimeOutAway, TimeOutStart, RemainingTime, ResetCounter, TimerChoice, ResetCounterOptions, StartupScreen, Possession, EndSoundPlayed

    if keystroke == "StartStop":
        if StartupScreen:
            StartupScreen = False
        else:
            if not TimeOutRunning:
                ClockPauze = not(ClockPauze)
    if keystroke == "ScoreHome+":
        if not(StartupScreen):
            ScoreHome += 1
    if keystroke == "ScoreHome-":
        if not(StartupScreen):
            if ScoreHome >= 1:
                ScoreHome -= 1
    if keystroke == "FoulHome+":
        if not(StartupScreen):
            FoulsHome += 1
    if keystroke == "FoulHome-":
        if not(StartupScreen):
            if FoulsHome >= 1:
                FoulsHome -= 1
    if keystroke == "ScoreAway+":
        if not(StartupScreen):
            ScoreAway += 1
    if keystroke == "ScoreAway-":
        if not(StartupScreen):
            if ScoreAway >= 1:
                ScoreAway -= 1
    if keystroke == "FoulAway+":
        if not(StartupScreen):
            FoulsAway += 1
    if keystroke == "FoulAway-":
        if not(StartupScreen):
            if FoulsAway >= 1:
                FoulsAway -= 1
    if keystroke == "Possession":
        if not(StartupScreen):
            if Possession == 0:
                Possession = 2
            Possession = 3 - Possession
            if Period == 0:
                Possession = 0
    if keystroke == "Periode+":
        if TimerChoice < len(ResetCounterOptions)-1 and StartupScreen:
            TimerChoice += 1
        if not(StartupScreen):
            # Possession = 3 - Possession
            Period += 1
            if Period <= 4:
                FoulsHome = 0
                FoulsAway = 0
            if Period == 3 or Period >= 5:
                TimeOutHome, TimeOutAway = 0, 0
            if Period == 5:
                ResetCounter = ResetCounterOptions[TimerChoice]
                if ResetCounter >= 600:
                    ResetCounter = ResetCounter / 2
    if keystroke == "Periode-":
        if TimerChoice > 0 and StartupScreen:
            TimerChoice -= 1
        if not(StartupScreen):
            if Period >= 1:
                Period -= 1
                if Period == 4:
                    ResetCounter = ResetCounterOptions[TimerChoice]
    if keystroke == "TimeOutHome":
        if not(StartupScreen):
            if ClockPauze and not(TimeOutRunning) and not(StartupScreen) and RemainingTime != 0:
                if Period <= 2 and TimeOutHome < 2:
                    TimeOutHome += 1
                    TimeOutRemaining = TimeOut
                    TimeOutStart = time.monotonic()
                    TimeOutRunning = True
                if Period > 2 and Period <= 4 and TimeOutHome < 3:
                    TimeOutHome += 1
                    TimeOutRemaining = TimeOut
                    TimeOutStart = time.monotonic()
                    TimeOutRunning = True
                if Period > 4 and TimeOutHome == 0:
                    TimeOutHome += 1
                    TimeOutRemaining = TimeOut
                    TimeOutStart = time.monotonic()
                    TimeOutRunning = True
    if keystroke == "TimeOutAway":
        if not(StartupScreen):
            if ClockPauze and not(TimeOutRunning) and RemainingTime != 0:
                if Period <= 2 and TimeOutAway < 2:
                    TimeOutAway += 1
                    TimeOutRemaining = TimeOut
                    TimeOutStart = time.monotonic()
                    TimeOutRunning = True
                if Period > 2 and Period <= 4 and TimeOutAway < 3:
                    TimeOutAway += 1
                    TimeOutRemaining = TimeOut
                    TimeOutStart = time.monotonic()
                    TimeOutRunning = True
                if Period > 4 and TimeOutAway == 0:
                    TimeOutAway += 1
                    TimeOutRemaining = TimeOut
                    TimeOutStart = time.monotonic()
                    TimeOutRunning = True
    if keystroke == "RestartTimer":
        EndSoundPlayed = False
        if not(StartupScreen):
            if ClockPauze:
                RemainingTime = ResetCounter
                EndSoundPlayed = False
                if Period == 0:
                    StartupScreen = True
                    ScoreHome = 0
                    ScoreAway = 0
                    FoulsHome = 0
                    FoulsAway = 0
                    TimeOutHome = 0
                    TimeOutAway = 0
                    Period = 1
                    Possession = 0
    if keystroke == "Buzzer":
        if not(StartupScreen):
            threading.Thread(target=PiezoBuzzer).start()

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
}

# Get keyboard inputs - returns every key pressed since the last call, so no presses are dropped
def GetKeyboardInput():
    keystrokes = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key in KeyboardCommands:
            keystrokes.append(KeyboardCommands[event.key])
    return keystrokes

# Function to configure the initial settings
def ConfigScreen():
    global ResetCounter, ResetCounterOptions, TimerChoice, RemainingTime
    if StartupScreen:
        ResetCounter = ResetCounterOptions[TimerChoice]
        RemainingTime = ResetCounter

        textDuration = fontLabel.render('Duration Period', True, white, black)
        textRecDuration = textDuration.get_rect(topleft=(50, 75))
        textChange = fontLabelSmall.render('Use PERIOD - or + to change value', True, white, black)
        textRecChange = textChange.get_rect(topleft=(50, 200))
        textStart = fontLabelSmall.render('Use START - STOP to confirm', True, white, black)
        textRecStart = textStart.get_rect(topleft=(50, 250))
        textResetCounter = fontScore.render(str(int(ResetCounter/60)), True, yellow, black)
        textRecResetCounter = textResetCounter.get_rect(center=(1000, 100))
        textCont = fontLabelExtraSmall.render(' min - continuous clock', True, white, black)
        textCrono = fontLabelExtraSmall.render(' min - cronostop', True, white, black)
        text5 = fontLabelExtraSmall.render('5', True, yellow, black)
        text6 = fontLabelExtraSmall.render('6', True, yellow, black)
        text8 = fontLabelExtraSmall.render('8', True, yellow, black)
        text10 = fontLabelExtraSmall.render('10', True, yellow, black)
        textU6 = fontLabelExtraSmall.render('U6:  1 match - ', True, white, black)
        textU8 = fontLabelExtraSmall.render('U8:  8 quarters - ', True, white, black)
        textU10 = fontLabelExtraSmall.render('U10: 8 quarters - ', True, white, black)
        textU12 = fontLabelExtraSmall.render('U12 & above: 4 quarters - ', True, white, black)

        scr.fill(black)
        scr.blit(textDuration, textRecDuration)
        scr.blit(textChange, textRecChange)
        scr.blit(textStart, textRecStart)
        scr.blit(textResetCounter, textRecResetCounter)
        scr.blit(LogoClub, (350, 330))
        scr.blit(textU6, (50, 520))
        scr.blit(text8, (50 + textU6.get_width(), 520))
        scr.blit(textCont, (50 + textU6.get_width() + text8.get_width(), 520))
        scr.blit(textU8, (50, 560))
        scr.blit(text6, (50 + textU8.get_width(), 560))
        scr.blit(textCont, (50 + textU8.get_width() + text6.get_width(), 560))
        scr.blit(textU10, (50, 600))
        scr.blit(text5, (50 + textU10.get_width(), 600))
        scr.blit(textCrono, (50 + textU10.get_width() + text5.get_width(), 600))
        scr.blit(textU12, (50, 640))
        scr.blit(text10, (50 + textU12.get_width(), 640))
        scr.blit(textCrono, (50 + textU12.get_width() + text10.get_width(), 640))
        pygame.display.flip()

# Commands received from the network, consumed by the main loop (thread-safe, nothing gets overwritten)
NetworkCommands = queue.Queue()
KnownCommands = ["Nothing", "Buzzer"] + list(KeyboardCommands.values())
CommandPattern = re.compile("|".join(re.escape(c) for c in sorted(KnownCommands, key=len, reverse=True)))

# Extract all complete commands from the received data, return the unparsed remainder.
# Works for newline separated commands as well as for older remotes that send commands without separator
# (TCP can deliver several of those in one packet, e.g. "ScoreHome+ScoreHome+").
def ParseCommands(buffer):
    commands = []
    end = 0
    for match in CommandPattern.finditer(buffer):
        commands.append(match.group())
        end = match.end()
    remainder = buffer[end:].rsplit("\n", 1)[-1]  # anything before a newline is an unknown command: drop it
    if len(remainder) > 64:  # garbage without newline: drop it
        remainder = ""
    return commands, remainder

# Function to handle network communication
def handle_network_thread():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reusing the socket
    # wlan0 may not have its address yet when the program starts at boot: keep retrying
    while True:
        try:
            sock.bind(('10.3.141.1', 8080))
            break
        except OSError as e:
            print(f"Cannot bind network socket yet ({e}), retrying")
            sleep(5)
    sock.listen(5)

    # Create lists to keep track of sockets for select()
    inputs = [sock]
    buffers = {}  # received but not yet parsed data per connection

    while True:
        # Use select to multiplex between sockets
        readable, _, _ = select.select(inputs, [], [])

        for s in readable:
            if s is sock:  # New connection
                connection, client_address = s.accept()
                print(f"Connection from {client_address} has been established!")
                connection.setblocking(0)  # Set socket to non-blocking
                inputs.append(connection)  # Add new connection to inputs list
                buffers[connection] = ""
            else:  # Existing connection with incoming data
                try:
                    data = s.recv(64)
                except OSError:
                    data = b""
                if data:
                    commands, buffers[s] = ParseCommands(buffers[s] + data.decode(errors="ignore"))
                    for command in commands:
                        if command != "Nothing":
                            NetworkCommands.put(command)
                else:  # Connection closed
                    print("Connection closed")
                    inputs.remove(s)  # Remove closed connection from inputs list
                    del buffers[s]
                    s.close()  # Close the socket

# Start network thread
network_thread = threading.Thread(target=handle_network_thread)
network_thread.daemon = True
network_thread.start()

# Play the end sound and the piezo buzzer (piezo in a thread so the display keeps updating)
def Signal():
    EndSound.play()
    threading.Thread(target=PiezoBuzzer).start()

# Format seconds as MM:SS, rounding up so the clock shows 00:00 only when time is really up
def FormatTime(seconds):
    seconds = math.ceil(seconds)
    return str(seconds // 60).zfill(2) + ":" + str(seconds % 60).zfill(2)

# The actual program
while True:
    if StartupScreen:
        ConfigScreen()

# Handle feedback from keyboard
    for keystroke in GetKeyboardInput():
        HandleFeedback(keystroke)

# Handle feedback from network
    while not NetworkCommands.empty():
        HandleFeedback(NetworkCommands.get_nowait())

# Start/Stop of the clock and count down
# RemainingTime is kept as a float so stopping the clock does not round away fractions of seconds
    if ClockPauze:
        StartCounter = RemainingTime
        startTime = time.monotonic()
    else:
        RemainingTime = max(0, StartCounter - (time.monotonic()-startTime))
    if RemainingTime <= 0:
        ClockPauze = True
        if EndSoundPlayed == False:
            Signal()
            EndSoundPlayed = True

        # Counter that will count up to show pauze time
        PauzeCounterString = FormatTime(int(time.monotonic()-PauzeCounter))

    else:
        PauzeCounter = time.monotonic()
        PauzeCounterString = ""

    RemainingString = FormatTime(RemainingTime)

# TimeOut token
    if TimeOutRunning:
        if TimeOutRemaining <= 0:
            TimeOutRunning = False
            Signal()
        else:
            PreviousTimeOutRemaining = TimeOutRemaining
            TimeOutRemaining = max(0, math.ceil(TimeOut - (time.monotonic()-TimeOutStart)))
            # Signal once when passing 10 seconds (not on every frame while 10 is shown)
            if PreviousTimeOutRemaining > 10 >= TimeOutRemaining:
                Signal()
    if not(StartupScreen):
        ScoreBoardUpdate(ScoreHome, ScoreAway, FoulsHome, FoulsAway, RemainingString, Period, TimeOutRemaining, PauzeCounterString, Possession)
    time.sleep(0.1)  # Control the update rate (also for the config screen)
