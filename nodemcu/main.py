import time
import usocket
from machine import Pin

# Server settings
SERVER_IP = '10.3.141.1'
SERVER_PORT = 8080

# LED color definitions for different states
COLOR_SERVER_CONNECTED = (0, 50, 0)  # Green
COLOR_KEYPRESSED = (0, 0, 50)  # Blue

# A key state must be stable this long before it is accepted (filters contact bounce)
DEBOUNCE_MS = 30
SCAN_INTERVAL_MS = 5

# Key mapping of the keyboard matrix
MATRIX = [
    ["TimeOutHome", "Periode-", "RestartTimer", "Periode+", "TimeOutAway"],
    ["FoulHome-", "FoulHome+", "Buzzer", "FoulAway-", "FoulAway+"],
    ["ScoreHome-", "ScoreHome+", "StartStop", "ScoreAway-", "ScoreAway+"]
]

# Pin configuration
INPUT_PINS = [12, 14, 27, 26, 25]
OUTPUT_PINS = [17, 16, 4]

def initialize_pins():
    inputs = [Pin(pin, Pin.IN, Pin.PULL_UP) for pin in INPUT_PINS]
    outputs = [Pin(pin, Pin.OUT, value=1) for pin in OUTPUT_PINS]
    return inputs, outputs

def connect_to_server(ip, port):
    client = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    try:
        client.connect((ip, port))
        client.send(b'Nothing\n')
        return client
    except OSError as e:
        print("Error connecting to server:", e)
        client.close()
        return None

def check_inputs(inputs, outputs, matrix):
    keypushed = ""
    for i, output in enumerate(outputs):
        output.value(0)
        for j, input_pin in enumerate(inputs):
            if input_pin.value() == 0:
                keypushed = matrix[i][j]
                break
        output.value(1)
        if keypushed:
            break
    return keypushed

def main():
    inputs, outputs = initialize_pins()

    while True:
        client = connect_to_server(SERVER_IP, SERVER_PORT)
        if client:
            set_color(*COLOR_SERVER_CONNECTED)  # Green when connected
            stable_key = ""  # debounced key state ("" = nothing pressed)
            candidate = ""
            candidate_since = time.ticks_ms()
            while True:
                key = check_inputs(inputs, outputs, MATRIX)
                now = time.ticks_ms()
                if key != candidate:
                    # State changed (or bounced): restart the stability timer
                    candidate = key
                    candidate_since = now
                elif key != stable_key and time.ticks_diff(now, candidate_since) >= DEBOUNCE_MS:
                    stable_key = key
                    if key:
                        # Send only on the press edge, so holding a button does not repeat
                        print("Pressed key:", key)
                        try:
                            client.send((key + "\n").encode())
                        except OSError:
                            client.close()
                            break  # Exit inner loop to reconnect
                        set_color(*COLOR_KEYPRESSED)  # Blue while pushed
                    else:
                        set_color(*COLOR_SERVER_CONNECTED)  # Green when released
                time.sleep_ms(SCAN_INTERVAL_MS)
        else:
            set_color(*COLOR_ERROR)  # Red on error
            time.sleep(RETRY_DELAY)

if __name__ == "__main__":
    main()
