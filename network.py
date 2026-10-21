# TCP server for the WiFi remote. Received commands are put on a queue that the main loop reads.
import queue
import re
import select
import socket
import threading
import time

from game import COMMANDS

# "Nothing" is sent by the remote when it connects, "Ping" every few seconds as heartbeat
KNOWN_COMMANDS = COMMANDS + ("Nothing", "Ping")
_COMMAND_PATTERN = re.compile("|".join(re.escape(c) for c in sorted(KNOWN_COMMANDS, key=len, reverse=True)))
# A remote that has sent a heartbeat and then stays silent this long is considered gone
HEARTBEAT_TIMEOUT = 10


def parse_commands(buffer):
    """Extract all complete commands from received data, return (commands, unparsed remainder).

    Works for newline separated commands as well as for older remotes that send commands without
    separator (TCP can deliver several of those in one packet, e.g. "ScoreHome+ScoreHome+").
    """
    commands = []
    end = 0
    for match in _COMMAND_PATTERN.finditer(buffer):
        commands.append(match.group())
        end = match.end()
    remainder = buffer[end:].rsplit("\n", 1)[-1]  # anything before a newline is an unknown command: drop it
    if len(remainder) > 64:  # garbage without newline: drop it
        remainder = ""
    return commands, remainder


class _Client:
    def __init__(self):
        self.buffer = ""
        self.last_seen = time.monotonic()
        self.heartbeat = False  # True once the remote has sent a "Ping"


class RemoteServer(threading.Thread):
    def __init__(self, ip, port):
        super().__init__(daemon=True)
        self.ip = ip
        self.port = port
        self.commands = queue.Queue()
        self.connected = 0  # number of connected remotes, read by the display

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reusing the socket
        # wlan0 may not have its address yet when the program starts at boot: keep retrying
        while True:
            try:
                sock.bind((self.ip, self.port))
                break
            except OSError as e:
                print(f"Cannot bind network socket yet ({e}), retrying")
                time.sleep(5)
        sock.listen(5)

        clients = {}
        while True:
            readable, _, _ = select.select([sock] + list(clients), [], [], 1)
            now = time.monotonic()
            for s in readable:
                if s is sock:  # New connection
                    connection, client_address = s.accept()
                    print(f"Connection from {client_address} has been established!")
                    connection.setblocking(0)
                    clients[connection] = _Client()
                    continue
                client = clients[s]
                try:
                    data = s.recv(64)
                except OSError:
                    data = b""
                if not data:  # Connection closed
                    self._close(s, clients, "closed")
                    continue
                client.last_seen = now
                commands, client.buffer = parse_commands(client.buffer + data.decode(errors="ignore"))
                for command in commands:
                    if command == "Ping":
                        client.heartbeat = True
                    elif command != "Nothing":
                        self.commands.put(command)
            # A remote that lost power or WiFi does not close its connection: detect it by the missing heartbeat
            for s, client in list(clients.items()):
                if client.heartbeat and now - client.last_seen > HEARTBEAT_TIMEOUT:
                    self._close(s, clients, "timed out")
            self.connected = len(clients)

    @staticmethod
    def _close(s, clients, reason):
        print(f"Connection {reason}")
        del clients[s]
        s.close()
