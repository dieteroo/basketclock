import machine
import network
import time
import uos

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
        time.sleep_ms(100)  # wait for connection
        print ('... ')

print('Connected to Wi-Fi:', wlan.ifconfig())