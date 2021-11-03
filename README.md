# Basketball clock with HDMI display
A basketball clock is an important investment for a lot of clubs so this project is intended to build a basketball clock using any HDMI enabled device.

The Raspberry PI device is plugged into the HDMI port of a TV (or any HDMI enabled device) and can use the TV speakers or any audio amplifyer connected to the PI.
When booting up the Raspberry, you get a startscreen that allows you to select the default time of a period.  This is required because U8/U10/all above, have different period durations.  (8/6/10 min)

After selecting the period, you get to the actual scoreboard:

![Scoreboard](/photo/scoreboard.jpg)

To supported features are:
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
  * Micropython micro controller (I used the Pycom WiPy but any micropython device should work)
  * Box + 12 buttons for the controls

![Scoreboard](/photo/startscreen.jpg)

![Scoreboard](/photo/controlpanel.jpg)

## Howto build this project
### Raspberry
The Raspberry is installed with default Raspbian image.  
In the folder *Raspberry*, you can find the documentation on how to install the Raspbian, the RASP AP platform (for WiFi control) and how to autostart the python code.  Also note that it's advised to activate in Raspi-config the overlay file-system and Read-Only Boot partition.  This will make sure that the SDcard is not corrupted by rebooting the system or the code is changed.  The screen is build using hte pygame library.

The actual code can be found in basketclock.py.
  
### Remote keyboard
The Remote keyboard is based upon a button matrix of 3x5.  The Pycom will scan this matrix and use a network socket to send the button pressed, to the Raspbian.  Note that the Raspbian handles the button pushed in the same way as a command from the keyboard.

In the folder *Pycom*, you can find the code for the Pycom microPython device.

The button matrix to be build is 3 horizontal wires and 5 vertical wires following this design:

 Matrix      | Vertical 1 | Vertical 2 | Vertical 3 | Vertical 4 | Vertical 5
 ------      | ---------- | ---------- | ---------- | -----------| ----------
 Horizontal 1 | TimeOutHome | Periode- | RestartTimer | Periode+ | TimeOutAway
Horizontal 2 | FoulHome- | FoulHome+ | Nothing  | FoulAway- | FoulAway+"
Horizontal 3 | ScoreHome- | ScoreHome+ | StartStop | ScoreAway- | ScoreAway+
