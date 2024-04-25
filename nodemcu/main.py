import machine
from machine import Pin, PWM
import network
import time
from time import sleep
import usocket

# Set rgb led pins (red / ground - longest pin / green / blue - shortest pin)
frequency = 5000
# Pin initialization (starts 4th pin on the right bottomside usb)
blue = PWM(Pin(2), frequency)
red = PWM(Pin(4), frequency)
green = PWM(Pin(16), frequency)
# info: # ground = machine.Pin(GND)

blue.duty(256)
red.duty(0)
green.duty(0)

print('Starting Pin Input initialization')
# Pin initialization (starts 3th pin left below - side usb)
Input1 = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
Input2 = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
Input3 = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
Input4 = machine.Pin(27, machine.Pin.IN, machine.Pin.PULL_UP)
Input5 = machine.Pin(26, machine.Pin.IN, machine.Pin.PULL_UP)
print('Starting Pin Output initialization')
Output1 = machine.Pin(25, machine.Pin.OUT)
Output1.value(1)
Output2 = machine.Pin(33, machine.Pin.OUT)
Output2.value(1)
Output3 = machine.Pin(32, machine.Pin.OUT)
Output3.value(1)

keypushed = ""

# Key mapping of the keyboard matrix
Matrix = [["TimeOutHome","Periode-","RestartTimer","Periode+","TimeOutAway"],
          ["FoulHome-","FoulHome+","Possession","FoulAway-","FoulAway+"],
          ["ScoreHome-","ScoreHome+","StartStop","ScoreAway-","ScoreAway+"]]

print('Starting connection to server 10.3.141.1:8080')
client = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
try:
    client.connect(('10.3.141.1', 8080))  # IP address and port of the server
    client.send(b'Nothing')
except OSError as e:
    print("Error connecting to server:", e)
    client.close()
    machine.reset()
print('Connection established')

while True:
    blue.duty(0)
    red.duty(0)
    green.duty(256)
    # Test all buttons
    Output1.value(0)
    if Input1.value() == 0:
        keypushed = "TimeOutHome"
    elif Input2.value() == 0:
        keypushed = "Periode-"
    elif Input3.value() == 0:
        keypushed = "RestartTimer"
    elif Input4.value() == 0:
        keypushed = "Periode+"
    elif Input5.value() == 0:
        keypushed = "TimeOutAway"
    Output1.value(1)

    Output2.value(0)
    if Input1.value() == 0:
        keypushed = "FoulHome-"
    elif Input2.value() == 0:
        keypushed = "FoulHome+"
    elif Input3.value() == 0:
        keypushed = "Possession"
    elif Input4.value() == 0:
        keypushed = "FoulAway-"
    elif Input5.value() == 0:
        keypushed = "FoulAway+"
    Output2.value(1)

    Output3.value(0)
    if Input1.value() == 0:
        keypushed = "ScoreHome-"
    elif Input2.value() == 0:
        keypushed = "ScoreHome+"
    elif Input3.value() == 0:
        keypushed = "StartStop"
    elif Input4.value() == 0:
        keypushed = "ScoreAway-"
    elif Input5.value() == 0:
        keypushed = "ScoreAway+"
    Output3.value(1)

    if keypushed:
        green.duty(0)
        blue.duty(256)
        print("Pressed key:", keypushed)
        try: 
            client.send(keypushed.encode())
        except client.error:
            client.close()
        keypushed = ""
        time.sleep(0.3)
        blue.duty(0)
        green.duty(256)

client.close()