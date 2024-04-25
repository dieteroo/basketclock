import pygame
import sys
import time
import math
import os
from time import sleep
import socket
import threading
from gpiozero import Buzzer

# Set the default path to the python directory
sourceFileDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(sourceFileDir)

# Pygame library initiation
pygame.init()
scr = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN)
pygame.display.set_caption('Basketbal Clock')
pygame.mouse.set_visible(0)
fontScore = pygame.font.Font('fonts/LED.ttf', 200)
fontScoreSmall = pygame.font.Font('fonts/LED.ttf', 90)
fontLabel = pygame.font.Font('fonts/DejaVuSans-Bold.ttf', 80)
fontLabelSmall = pygame.font.Font('fonts/DejaVuSans-Bold.ttf', 40)
LogoClub = pygame.image.load('image/logo.png')
Manual = pygame.image.load('image/handleidingScoreboard.png')
textLabelHome = fontLabel.render('HOME', True, (100, 100, 100), (0, 0, 0))
textLabelAway = fontLabel.render('AWAY', True, (100, 100, 100), (0, 0, 0))
textLabelFouls = fontLabel.render('FOULS', True, (100, 100, 100), (0, 0, 0))
textLabelPeriod = fontLabel.render('P', True, (100, 100, 100), (0, 0, 0))
TimeOutText = ("", "*", "**")
PauzeCounterString = ""
cyan = (100, 255, 255)
red = (255, 0, 0)
# All variables required for the clock
startTime = time.time()
ResetCounter = 600
# Startcounter is reset to remaining time when clock is stopped
StartCounter = ResetCounter
RemainingTime = ResetCounter
ClockPauze = True  # check if the clock is active
ScoreHome = 0
ScoreAway = 0
FoulsHome = 0
FoulsAway = 0
Period = 1
Possession = 0
EndSound = pygame.mixer.Sound('sounds/BUZZER.WAV')
EndSoundPlayed = False  # required to only play 1 time
# Buzzer - Connect your piezobuzzer to ground and GPIO pin16
buzzer = Buzzer(16)
def PiezoBuzzer():
    buzzer.on()
    sleep(0.5)
    buzzer.off()
TimeOut = 60
TimeOutRunning = False
TimeOutHome = 0
TimeOutAway = 0
TimeOutRemaining = 0
StartupScreen = True  # allow configuration
ResetCounterOptions = (720, 660, 600, 540, 480, 420, 360, 300, 240, 180, 120, 60)
TimerChoice = 2  # to allow selection of the Timer - default = 10 min
PauzeCounter = 0
time.sleep(15)

#function for the changing digits
def ScoreBoardUpdate(ScoreHome, ScoreAway, FoulsHome, FoulsAway, Clock, Period, TimeOutRemaining, PauzeCounterString, Possession):
    global textLabelHome, textLabelAway, textLabelFouls, textLabelPeriod

    textScoreHome = fontScore.render(str(ScoreHome), True, (255, 255, 0), (0, 0, 0))
    textScoreAway = fontScore.render(str(ScoreAway), True, (255, 255, 0), (0, 0, 0))
    textClock = fontScore.render(str(Clock), True, (255, 0, 0), (0, 0, 0))
    # Put the fouls in red if 4 to indicate free shots
    if FoulsHome < 4:
        textFoulsHome = fontScore.render(str(FoulsHome), True, (255, 255, 0), (0, 0, 0))
    else:
        textFoulsHome = fontScore.render(str(FoulsHome), True, (255, 0, 0), (0, 0, 0))
    if FoulsAway < 4:
        textFoulsAway = fontScore.render(str(FoulsAway), True, (255, 255, 0), (0, 0, 0))
    else:
        textFoulsAway = fontScore.render(str(FoulsAway), True, (255, 0, 0), (0, 0, 0))
    textTimeOut = fontScore.render(str(TimeOutRemaining), True, (255, 255, 0), (0, 0, 0))
    textPauzeCounter = fontScore.render(str(PauzeCounterString), True, (255, 255, 0), (0, 0, 0))
    textPeriod = fontScoreSmall.render(str(Period), True, (255, 255, 0), (0, 0, 0))
    textTimeOutHome = fontScore.render(TimeOutText[TimeOutHome], True, (255, 255, 0), (0, 0, 0))
    textTimeOutAway = fontScore.render(TimeOutText[TimeOutAway], True, (255, 255, 0), (0, 0, 0))

# Fixed text
    textRectLabelHome = textLabelHome.get_rect(center=(200, 50))
    textRectLabelAway = textLabelAway.get_rect(center=(1080, 50))
    textRectFoulsLabelHome = textLabelFouls.get_rect(center=(200, 480))
    textRectFoulsLabelAway = textLabelFouls.get_rect(center=(1080, 480))
    textRectLabelPeriod = textLabelPeriod.get_rect(center=(600, 50))

# Variable text
    textRectScoreHome = textScoreHome.get_rect(center=(200, 200))
    textRectScoreAway = textScoreAway.get_rect(center=(1080, 200))
    textRectClock = textClock.get_rect(center=(640, 200))
    textRectFoulsHome = textFoulsHome.get_rect(center=(200, 600))
    textRectFoulsAway = textFoulsAway.get_rect(center=(1080, 600))
    textRectTimeOut = textTimeOut.get_rect(center=(640, 600))
    textRectPauzeCounter = textPauzeCounter.get_rect(center=(640, 600))
    textRectPeriod = textPeriod.get_rect(center=(660, 50))
    textRectTimeOutHome = textTimeOutHome.get_rect(center=(200, 350))
    textRectTimeOutAway = textTimeOutAway.get_rect(center=(1080, 350))

    scr.fill((0, 0, 0))
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
    scr.blit(LogoClub, (390, 330))
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
    global ClockPauze, TimeOutRunning, TimeOutRemaining, ScoreHome, FoulsHome, ScoreAway, FoulsAway, Period, TimeOutHome, TimeOutAway, TimeOutStart, RemainingTime, ResetCounter, TimerChoice, ResetCounterOptions, StartupScreen, Possession

    if keystroke == "StartStop":
        if StartupScreen:
            StartupScreen = False
        else:
            if not TimeOutRunning:
                ClockPauze = not(ClockPauze)
    if keystroke == "ScoreHome+":
        if TimerChoice < len(ResetCounterOptions)-1 and StartupScreen:
            TimerChoice += 1
        if not(StartupScreen):
            ScoreHome += 1
    if keystroke == "ScoreHome-":
        if TimerChoice > 0 and StartupScreen:
            TimerChoice -= 1
        if not(StartupScreen):
            ScoreHome -= 1
    if keystroke == "FoulHome+":
        FoulsHome += 1
    if keystroke == "FoulHome-":
        FoulsHome -= 1
    if keystroke == "ScoreAway+":
        ScoreAway += 1
    if keystroke == "ScoreAway-":
        ScoreAway -= 1
    if keystroke == "FoulAway+":
        FoulsAway += 1
    if keystroke == "FoulAway-":
        FoulsAway -= 1
    if keystroke == "Possession":
        if Possession == 0:
            Possession = 2
        Possession = 3 - Possession
    if keystroke == "Periode+":
        # Possession = 3 - Possession
        Period += 1
        FoulsHome = 0
        FoulsAway = 0
        if Period > 2:
            TimeOutHome, TimeOutAway = 0, 0
    if keystroke == "Periode-":
        Period -= 1
    if keystroke == "TimeOutHome":
        if ClockPauze and not(TimeOutRunning) and not(StartupScreen):
            TimeOutHome += 1
            TimeOutRemaining = TimeOut
            TimeOutStart = time.time()
            TimeOutRunning = True
    if keystroke == "TimeOutAway":
        if ClockPauze and not(TimeOutRunning) and not(StartupScreen):
            TimeOutAway += 1
            TimeOutRemaining = TimeOut
            TimeOutStart = time.time()
            TimeOutRunning = True
    if keystroke == "RestartTimer":
        if ClockPauze:
            RemainingTime = ResetCounter
            EndSoundPlayed = False

# Get keyboard inputs
def GetKeyboardInput():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            GPIO.cleanup()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
                GPIO.cleanup()
            if event.key == pygame.K_SPACE:
                keystroke = "StartStop"
                return keystroke
            if event.key == pygame.K_s:
                keystroke = "ScoreHome+"
                return keystroke
            if event.key == pygame.K_x:
                keystroke = "ScoreHome-"
                return keystroke
            if event.key == pygame.K_d:
                keystroke = "FoulHome+"
                return keystroke
            if event.key == pygame.K_c:
                keystroke = "FoulHome-"
                return keystroke
            if event.key == pygame.K_j:
                keystroke = "ScoreAway+"
                return keystroke
            if event.key == pygame.K_n:
                keystroke = "ScoreAway-"
                return keystroke
            if event.key == pygame.K_h:
                keystroke = "FoulAway+"
                return keystroke
            if event.key == pygame.K_b:
                keystroke = "FoulAway-"
                return keystroke
            if event.key == pygame.K_v:
                keystroke = "Possession"
                return keystroke
            if event.key == pygame.K_y:
                keystroke = "Periode+"
                return keystroke
            if event.key == pygame.K_r:
                keystroke = "Periode-"
                return keystroke
            if event.key == pygame.K_e:
                keystroke = "TimeOutHome"
                return keystroke
            if event.key == pygame.K_u:
                keystroke = "TimeOutAway"
                return keystroke
            if event.key == pygame.K_t:
                keystroke = "RestartTimer"
                return keystroke

def GetNetworkInput():
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind(('10.3.141.1', 8080))
    serv.listen(5)
    while True:
        clientsocket, clientAddress = serv.accept()
        # Dual threading
        dualthread = threading.Thread(target=handle_client, args=(clientsocket, clientAddress))
        dualthread.start()

def handle_client(clientsocket, clientAddress):
    global keystroke
    while True:
        data = clientsocket.recv(64)
        if not data:
            break
        keystroke = str(data.decode())
    clientsocket.close()

def ConfigScreen():
    global ResetCounter, ResetCounterOptions, TimerChoice, RemainingTime
    if StartupScreen:
        ResetCounter = ResetCounterOptions[TimerChoice]
        RemainingTime = ResetCounter
        textSetCounter = fontLabelSmall.render('Duration Period (use HomeScore Up/Down + Clockstop)', True, (100, 100, 100), (0, 0, 0))
        textRecSetCounter = textSetCounter.get_rect(center=(640, 50))
        textResetCounter = fontScore.render(str(int(ResetCounter/60)), True, (255, 255, 100), (0, 0, 0))
        textRecResetCounter = textResetCounter.get_rect(center=(640, 150))
        scr.fill((0, 0, 0))
        scr.blit(textSetCounter, textRecSetCounter)
        scr.blit(textResetCounter, textRecResetCounter)
        scr.blit(Manual, (250, 280))
        pygame.display.flip()

# Start the network threat to get socket commands
newthread = threading.Thread(target=GetNetworkInput)
newthread.start()

# The actual program
running = True
keystroke = ""
while running:
    if StartupScreen:
        ConfigScreen()

# Handle feedback from keyboard
    HandleFeedback(GetKeyboardInput())
# Handle feedback from network
    HandleFeedback(keystroke)
    keystroke = ""

# Start/Stop of the clock and count down
    if ClockPauze:
        StartCounter = RemainingTime
        startTime = time.time()
    else:
        RemainingTime = StartCounter - round(time.time()-startTime)
    if RemainingTime == 0:
        ClockPauze = True
        #Counter that will count up to show pauze time
        PauzeCounterUp = round(time.time()-PauzeCounter)
        PauzeCounterMin = math.floor(PauzeCounterUp/60)
        PauzeCounterSec = PauzeCounterUp - PauzeCounterMin*60
        PauzeCounterString = str(int(PauzeCounterMin)).zfill(2) + ":" + str(int(PauzeCounterSec)).zfill(2)
        if not(EndSoundPlayed):
            EndSoundPlayed = True
            EndSound.play()
            PiezoBuzzer()
    else:
        PauzeCounter = time.time()
        PauzeCounterString = ""
    RemainingMin = math.floor(RemainingTime/60)
    RemainingSec = RemainingTime - RemainingMin*60
    RemainingString = str(int(RemainingMin)).zfill(2) + ":" + str(int(RemainingSec)).zfill(2)

# TimeOut token
    if TimeOutRunning:
        if TimeOutRemaining <= 0:
            TimeOutRunning = False
            EndSound.play()
            PiezoBuzzer()
        else:
            TimeOutRemaining = TimeOut - int(round(time.time()-TimeOutStart))
            if TimeOutRemaining == 10:
                EndSound.play()
                PiezoBuzzer()
    if not(StartupScreen):
        ScoreBoardUpdate(ScoreHome, ScoreAway, FoulsHome, FoulsAway, RemainingString, Period, TimeOutRemaining, PauzeCounterString, Possession)

newthread.stop()