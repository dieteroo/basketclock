# Basketball clock with HDMI display
A basketball clock is an important investment for a lot of clubs so this project is intended to build a basketball clock using any HDMI enabled device.

The Raspberry Pi device is plugged into the HDMI port of a TV (or any HDMI enabled device) and can use the TV speakers or any audio amplifyer connected to the Pi.
When booting up the Raspberry, you get a startscreen that allows you to select the default time of a period.  This is required because U8/U10/all above, have different period durations.

After selecting the period, you get to the actual scoreboard:

![Scoreboard](/photo/scoreboard.jpg)

The supported features are:
- Main clock with start/stop and button for reset
- Fouls home/guest
- Score home/guest
- TimeOut home/guest
- Period

## What is required?
The basketball scoreboard with clock can be controlled with a wireless keyboard or via a WiFi network.
* Keyboard control only 
  * Raspberry PI
* WiFi control + Keyboard control
  * Raspberry PI
  * Micropython micro controller
  * Box + 14 buttons for the controls

![Scoreboard](/photo/startscreen.jpg)

![Scoreboard](/photo/controlpanel.jpg)

## Howto build this project
### Raspberry
[Installation manual](install/install.md)
  
### Remote keyboard
The Remote keyboard is based upon a button matrix of 3x5.  The micropython device will scan this matrix and use a network socket to send the button pressed, to the Raspbian. Note that the Raspbian handles the button pushed in the same way as a command from the keyboard.
The button matrix to be build is 3 horizontal wires and 5 vertical wires following this design:

 Matrix      | Vertical 1 | Vertical 2 | Vertical 3 | Vertical 4 | Vertical 5
 ------      | ---------- | ---------- | ---------- | -----------| ----------
Horizontal 1 | TimeOutHome | Periode- | RestartTimer | Periode+ | TimeOutAway
Horizontal 2 | FoulHome- | FoulHome+ | Nothing  | FoulAway- | FoulAway+"
Horizontal 3 | ScoreHome- | ScoreHome+ | StartStop | ScoreAway- | ScoreAway+

### Pycom
In the folder *pycom*, you can find the code for the Pycom microPython device.

### NodeMCU
In the folder *nodemcu*, you can find the code for the NodeMCU microPython device.

