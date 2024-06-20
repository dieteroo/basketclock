import machine
from machine import Pin, PWM
import network
import time
import uos

# Constants
FREQUENCY = 5000
RETRY_DELAY = 5  # seconds
SLEEP_DURATION = 0.25  # seconds

# Wi-Fi configuration
STATIC_IP = '10.3.141.3'
NETMASK = '255.255.255.0'
GATEWAY = '10.3.141.1'
DNS = '10.3.141.1'
SSID = '_wifi_SSID_'  # Replace with your network SSID
PASSWORD = '_wifi_PASS_'  # Replace with your network password

# LED color definitions for different states
COLOR_OFF = (0, 0, 0)
COLOR_CONNECTING = (50, 0, 50)  # Purple
COLOR_WIFI_CONNECTED = (0, 50, 50)  # Cyan
COLOR_ERROR = (50, 0, 0)  # Red

# Pin configuration
RED_PIN = 19  # (red / ground - longest pin / green / blue - shortest pin)
GREEN_PIN = 18
BLUE_PIN = 5
# info: # ground = machine.Pin(GND)

# Initialize PWM for RGB LED
red_pwm = PWM(Pin(RED_PIN), FREQUENCY)
green_pwm = PWM(Pin(GREEN_PIN), FREQUENCY)
blue_pwm = PWM(Pin(BLUE_PIN), FREQUENCY)

# Function to set PWM duty cycle (0-255 range)
def set_color(r, g, b):
    red_pwm.duty(r * 4)  # Scale 0-255 to 0-1023 for MicroPython PWM
    green_pwm.duty(g * 4)
    blue_pwm.duty(b * 4)

set_color(*COLOR_OFF)  # Initialize LED to off

# Ensure Wi-Fi is active on boot
if machine.reset_cause() != machine.SOFT_RESET:
    wlan = network.WLAN(network.STA_IF)  # Create station interface
    
# Wi-Fi configuration
wlan = network.WLAN(network.STA_IF)  # Create station interface

# Ensure Wi-Fi interface is active
if not wlan.active():
    wlan.active(True)  # Activate the interface

# Set static IP configuration
wlan.ifconfig((STATIC_IP, NETMASK, GATEWAY, DNS))

# Connect to Wi-Fi
if not wlan.isconnected():
    wlan.connect(SSID, PASSWORD)
    attempt = 0
    while not wlan.isconnected() and attempt < 12:
        set_color(*COLOR_CONNECTING)  # Purple while waiting for connection
        time.sleep(RETRY_DELAY)
        print('Connecting to network...')
        attempt += 1

if wlan.isconnected():
    print('Connected to Wi-Fi:', wlan.ifconfig())
    set_color(*COLOR_WIFI_CONNECTED)  # Cyan when connected
    time.sleep(SLEEP_DURATION)
else:
    print('Failed to connect to Wi-Fi')
    set_color(*COLOR_ERROR)  # Red when failed
    machine.reset()
