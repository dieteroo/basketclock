# boot.py -- run on boot-up
import os
from machine import Pin
import machine
import usocket
import time
import pycom

uart = UART(0, 115200)
os.dupterm(uart)

from network import WLAN
wlan = WLAN() # get current object, without changing the mode

if machine.reset_cause() != machine.SOFT_RESET:
    wlan.init(mode=WLAN.STA, antenna=WLAN.INT_ANT)

if not wlan.isconnected():
    # change the line below to match your network ssid, security and password
    wlan.connect('_wifi_SSID_', auth=(WLAN.WPA2, '_wifi_PASS_'), timeout=5000)
    while not wlan.isconnected():
        machine.idle() # save power while waiting