import machine
from machine import Pin, PWM
import network
import time
import uos

# Set rgb led pins (red / ground - longest pin / green / blue - shortest pin)
frequency = 5000
# Pin initialization (starts 3rd pin on the right bottomside usb)
red = PWM(Pin(15), frequency)
green = PWM(Pin(2), frequency)
blue = PWM(Pin(4), frequency)
# info: # ground = machine.Pin(GND)

# Wi-Fi configuration
wlan = network.WLAN(network.STA_IF)  # create station interface
wlan.active(True)  # activate the interface

if machine.reset_cause() != machine.SOFT_RESET:
    wlan.active(True)  # ensure Wi-Fi is active on boot

# Set static IP configuration
wlan.ifconfig(('10.3.141.3', '255.255.255.0', '10.3.141.1', '10.3.141.1'))

if not wlan.isconnected():
    # Replace SSID and password with your network credentials
    wlan.connect('_wlan_SSID_', '_wlan_PASS_')

    while not wlan.isconnected():
        blue.duty(0)
        red.duty(256)
        green.duty(0)
        time.sleep_ms(100)  # wait for connection
        print ('... ')

print('Connected to Wi-Fi:', wlan.ifconfig())
blue.duty(0)
red.duty(256)
green.duty(0)