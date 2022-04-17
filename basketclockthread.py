import pygame
import sys
import time
import math
import os
from time import sleep
import socket
import threading

# Set the default path to the python directory
sourceFileDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(sourceFileDir)

#pygame library initiation
pygame.init()
scr = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN)
#scr = pygame.display.set_mode((1280, 720))
pygame.display.set_caption('Basketbal Clock')
fontScore = pygame.font.Font('fonts/LED.ttf', 200)
fontScoreSmall = pygame.font.Font('fonts/LED.ttf', 90)
fontLabel = pygame.font.Font(
    'fonts/DejaVuSans-Bold.ttf', 80)
fontLabelSmall = pygame.font.Font(
    'fonts/DejaVuSans-Bold.ttf', 40)
LogoClub = pygame.image.load('image/hageland.png')
Manual = pygame.image.load('image/handleidingScoreboard.png')
textLabelHome = fontLabel.render('HOME', True, (100, 100, 100), (0, 0, 0))
textLabelAway = fontLabel.render('VISITOR', True, (100, 100, 100), (0, 0, 0))
textLabelFouls = fontLabel.render('FOULS', True, (100, 100, 100), (0, 0, 0))
textLabelPeriod = fontLabel.render('P', True, (100, 100, 100), (0, 0, 0))
TimeOutText = ("", "*", "**")

color = (100, 255, 255)

#All variables required for the clock
startTime = time.time()
ResetCounter = 600
# startcounter is reset to remaining time when clock is stopped
StartCounter = ResetCounter
RemainingTime = ResetCounter
ClockPauze = True  # check if the clock is active
ScoreHome = 0
ScoreAway = 0
FoolsHome = 0
FoolsAway = 0
Period = 1
EndSound = pygame.mixer.Sound('sounds/BUZZER.WAV')
EndSoundPlayed = False  # required to only play 1 time

TimeOut = 60
TimeOutRunning = False
TimeOutHome = 0
TimeOutAway = 0
TimeOutRemaining = 0
StartupScreen = True  # allow configuration
ResetCounterOptions = (600, 360, 300)
TimerChoice = 0  # to allow selection of the Timer

#function for the changing digits
def ScoreBoardUpdate(ScoreHome, ScoreAway, FoulsHome, FoulsAway, Clock, Period, TimeOutRemaining):
    global textLabelHome, textLabelAway, textLabelFouls, textLabelPeriod

    textScoreHome = fontScore.render(
        str(ScoreHome), True, (255, 255, 0), (0, 0, 0))
    textScoreAway = fontScore.render(
        str(ScoreAway), True, (255, 255, 0), (0, 0, 0))
    textClock = fontScore.render(str(Clock), True, (255, 0, 0), (0, 0, 0))

    # Put the fools in red if 4 to indicate free shots
    if FoolsHome < 4:
        textFoulsHome = fontScore.render(
            str(FoulsHome), True, (255, 255, 0), (0, 0, 0))
    else:
        textFoulsHome = fontScore.render(
            str(FoulsHome), True, (255, 0, 0), (0, 0, 0))
    if FoolsAway < 4:
        textFoulsAway = fontScore.render(
            str(FoulsAway), True, (255, 255, 0), (0, 0, 0))
    else:
        textFoulsAway = fontScore.render(
            str(FoulsAway), True, (255, 0, 0), (0, 0, 0))

    textTimeOut = fontScore.render(
        str(TimeOutRemaining), True, (255, 255, 0), (0, 0, 0))
    textPeriod = fontScoreSmall.render(
        str(Period), True, (255, 255, 0), (0, 0, 0))

    textTimeOutHome = fontScore.render(
        TimeOutText[TimeOutHome], True, (255, 255, 0), (0, 0, 0))
    textTimeOutAway = fontScore.render(
        TimeOutText[TimeOutAway], True, (255, 255, 0), (0, 0, 0))

#Fixed text
    textRectLabelHome = textLabelHome.get_rect(center=(200, 50))
    textRectLabelAway = textLabelAway.get_rect(center=(1080, 50))
    textRectFoulsLabelHome = textLabelFouls.get_rect(center=(200, 480))
    textRectFoulsLabelAway = textLabelFouls.get_rect(center=(1080, 480))
    textRectLabelPeriod = textLabelPeriod.get_rect(center=(600, 50))

#Variable text
    textRectScoreHome = textScoreHome.get_rect(center=(200, 200))
    textRectScoreAway = textScoreAway.get_rect(center=(1080, 200))
    textRectClock = textClock.get_rect(center=(640, 200))
    textRectFoulsHome = textFoulsHome.get_rect(center=(200, 600))
    textRectFoulsAway = textFoulsAway.get_rect(center=(1080, 600))
    textRectTimeOut = textTimeOut.get_rect(center=(640, 600))
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
    scr.blit(textPeriod, textRectPeriod)
    scr.blit(textTimeOutHome, textRectTimeOutHome)
    scr.blit(textTimeOutAway, textRectTimeOutAway)
    scr.blit(LogoClub, (390, 350))

    pygame.draw.rect(scr, color, pygame.Rect(50, 120, 300, 200), 5)
    pygame.draw.rect(scr, color, pygame.Rect(930, 120, 300, 200), 5)
    pygame.display.flip()

#take actions depending on the feedback from any channel (keyboard, IO or network)
def HandleFeedback(keystroke):
    global ClockPauze, TimeOutRunning, TimeOutRemaining, ScoreHome, FoolsHome, ScoreAway, FoolsAway, Period, TimeOutHome, TimeOutAway, TimeOutStart, RemainingTime, ResetCounter, TimerChoice, ResetCounterOptions, StartupScreen

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
        FoolsHome += 1
    if keystroke == "FoulHome-":
        FoolsHome -= 1
    if keystroke == "ScoreAway+":
        ScoreAway += 1
    if keystroke == "ScoreAway-":
        ScoreAway -= 1
    if keystroke == "FoulAway+":
        FoolsAway += 1
    if keystroke == "FoulAway-":
        FoolsAway -= 1
    if keystroke == "Periode+":
        Period += 1
        FoolsHome = 0
        FoolsAway = 0
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

#get keyboard inputs
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
            if event.key == pygame.K_q:
                keystroke = "ScoreHome+"
                return keystroke
            if event.key == pygame.K_w:
                keystroke = "ScoreHome-"
                return keystroke
            if event.key == pygame.K_s:
                keystroke = "FoulHome+"
                return keystroke
            if event.key == pygame.K_x:
                keystroke = "FoulHome-"
                return keystroke
            if event.key == pygame.K_m:
                keystroke = "ScoreAway+"
                return keystroke
            if event.key == pygame.K_COLON:
                keystroke = "ScoreAway-"
                return keystroke
            if event.key == pygame.K_l:
                keystroke = "FoulAway+"
                return keystroke
            if event.key == pygame.K_SEMICOLON:
                keystroke = "FoulAway-"
                return keystroke
            if event.key == pygame.K_u:
                keystroke = "Periode+"
                return keystroke
            if event.key == pygame.K_r:
                keystroke = "Periode-"
                return keystroke
            if event.key == pygame.K_a:
                keystroke = "TimeOutHome"
                return keystroke
            if event.key == pygame.K_p:
                keystroke = "TimeOutAway"
                return keystroke
            if event.key == pygame.K_t:
                keystroke = "RestartTimer"
                return keystroke

def GetNetworkInput():
    time.sleep(10)   # make sure the network is stable before starting server
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind(('10.3.141.1', 8080))
    serv.listen(5)
    while True:
        clientsocket, clientAddress = serv.accept()
        #dual threading
        dualthread = threading.Thread(target=handle_client, args=(clientsocket, clientAddress))
        dualthread.start()

def handle_client(clientsocket, clientAddress):
    global keystroke
    while True:
        data = clientsocket.recv(2048)
        if not data:
            break
        keystroke = str(data.decode())
    clientsocket.close()

def ConfigScreen():
    global ResetCounter, ResetCounterOptions, TimerChoice, RemainingTime

    if StartupScreen:
        ResetCounter = ResetCounterOptions[TimerChoice]
        RemainingTime = ResetCounter
        textSetCounter = fontLabelSmall.render(
            'Duration Period (use HomeScore Up/Down + Clockstop)', True, (100, 100, 100), (0, 0, 0))
        textRecSetCounter = textSetCounter.get_rect(center=(640, 50))
        textResetCounter = fontScore.render(
            str(int(ResetCounter/60)), True, (255, 255, 100), (0, 0, 0))
        textRecResetCounter = textResetCounter.get_rect(center=(640, 150))
        scr.fill((0, 0, 0))
        scr.blit(textSetCounter, textRecSetCounter)
        scr.blit(textResetCounter, textRecResetCounter)
        scr.blit(Manual, (250, 280))
        pygame.display.flip()

# start the network threat to get socket commands
newthread = threading.Thread(target=GetNetworkInput)
newthread.start()

#The actual program
running = True
keystroke = ""
while running:
    if StartupScreen:
        ConfigScreen()

#Handle feedback from keyboard
    HandleFeedback(GetKeyboardInput())
    #ReadOutKeyboard()
#Handle feedback from network
    HandleFeedback(keystroke)
    keystroke = ""

#Start/Stop of the clock and count down
    if ClockPauze:
        StartCounter = RemainingTime
        startTime = time.time()
    else:
        RemainingTime = StartCounter - round(time.time()-startTime)

    if RemainingTime == 0:
        ClockPauze = True
        if not(EndSoundPlayed):
            EndSoundPlayed = True
            EndSound.play()

    RemainingMin = math.floor(RemainingTime/60)
    RemainingSec = RemainingTime - RemainingMin*60
    RemainingString = str(int(RemainingMin)) + \
        " : " + str(int(RemainingSec))

#TimeOut token
    if TimeOutRunning:
        if TimeOutRemaining <= 0:
            TimeOutRunning = False
            EndSound.play()
        else:
            TimeOutRemaining = TimeOut - int(round(time.time()-TimeOutStart))
            if TimeOutRemaining == 10:
                EndSound.play()

    if not(StartupScreen):
        ScoreBoardUpdate(ScoreHome, ScoreAway, FoolsHome,
                         FoolsAway, RemainingString, Period, TimeOutRemaining)

newthread.stop()
