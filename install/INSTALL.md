# Prepare the microSD card
## Use Raspberry Pi Imager(https://www.raspberrypi.com/software/) 
```
* CHOOSE DEVICE
  Select your device 
* CHOOSE OS
  Select Raspberry Pi OS (other) 
  Select Raspberry Pi OS (Legacy, 32-bit) Lite 
* CHOOSE STORAGE 
  Select your storage device 
* NEXT 
 
* Would you like to use OS customisation settings?
  EDIT SETTINGS
* Set hostname 
* Set username and password
! DO NOT CONFIGURE wireless LAN ! see notes below
* Set locale settings
  Select Time zone 
  Select Keyboard layout 
* SERVICES 
* Enable SSH 
* Allow public-key authentication only 
  Set authorized_key for 'user'
* SAVE 

* Would you like to use OS customisation settings?
* YES

* Would you like to prefill the wifi password from the system keychain?
* NO

* All existing data on 'your storage device' will be erased
* Are you sure you want to continue?
* YES

####
Raspberry Pi OS (Legacy) Lite
Release date: March 12th 2024
System: 32-bit
Kernel version: 6.1
Debian version: 11 (bullseye)
Size: 365MB
####
```
## Place micro SD in Raspberry Pi 
## Connect network cable, HDMI cable & power cable
## Let the device finish booting  (hostname login: )
## Connect to IP via SSH

# To install the program run
```bash
curl -sL https://raw.githubusercontent.com/dieteroo/basketclock/test/install/install.basket | bash
```

# If you want to autostart the program run
```bash
curl -sL https://raw.githubusercontent.com/dieteroo/basketclock/test/install/install.service | bash
```

# If you want to connect via a micropython device run
```bash
curl -sL https://raw.githubusercontent.com/dieteroo/basketclock/test/install/install.hostapd | bash
```
You will be asked for a SSID, a password and a WiFi-Channel

Afterwards use the files in *pycom* or *nodemcu* to configure the micropython device

```Don't forget to change _wifi_SSID_ & _wifi_PASS_ in /pycom/boot.py```

# After all is set and done, protect the boot partition
```bash
curl -sL https://raw.githubusercontent.com/dieteroo/basketclock/test/install/install.boot | bash
```