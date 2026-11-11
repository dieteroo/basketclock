# TCP server for the WiFi remote. Received commands are put on a queue that the main loop reads.
import queue
import re
import select
import socket
import subprocess
import threading
import time

from game import COMMANDS

# "Nothing" is sent by the remote when it connects, "Ping" every few seconds as heartbeat
KNOWN_COMMANDS = COMMANDS + ("Nothing", "Ping")
_COMMAND_PATTERN = re.compile("|".join(re.escape(c) for c in sorted(KNOWN_COMMANDS, key=len, reverse=True)))
# A remote that has sent a heartbeat and then stays silent this long is considered gone
# (it sends one every 2 s, so this allows two lost heartbeats)
HEARTBEAT_TIMEOUT = 6
# Put on the command queue when a remote connection is lost: the game is paused, nobody can stop the clock
CONNECTION_LOST = "ConnectionLost"
# A device on the WiFi hotspot without a connection to the scoreboard for this long is logged off the hotspot.
# A remote that restarted (power, reset) does not log off itself, and the Pi's WiFi chip keeps refusing
# a remote it still thinks is connected: without this it never gets back in.
KICK_DELAY = 15
STATION_CHECK_INTERVAL = 5
_MAC = re.compile(r"^([0-9a-f]{2}:){5}[0-9a-f]{2}$")
# wpa_cli for the NetworkManager hotspot (Bookworm, Trixie), hostapd_cli for hostapd (Bullseye).
# The user running the program must be in the netdev group. Full paths: /usr/sbin is not in a user's PATH.
_WIFI_TOOLS = ("/usr/sbin/wpa_cli", "/usr/sbin/hostapd_cli")


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


def arp_lookup(ip, arp_table):
    """(MAC address, interface) of `ip` in the text of /proc/net/arp, or None."""
    for line in arp_table.splitlines()[1:]:
        fields = line.split()
        if len(fields) >= 6 and fields[0] == ip and fields[3] != "00:00:00:00:00:00":
            return fields[3], fields[5]
    return None


def _read_arp(ip):
    try:
        with open("/proc/net/arp") as f:
            return arp_lookup(ip, f.read())
    except OSError:
        return None


def parse_stations(all_sta_output):
    """MAC addresses in the output of `wpa_cli all_sta` / `hostapd_cli all_sta`."""
    return {line.strip() for line in all_sta_output.splitlines() if _MAC.match(line.strip())}


def idle_stations(idle_since, stations, connected_macs, now):
    """Track since when each hotspot station has no connection to the scoreboard (in `idle_since`)
    and return the ones idle longer than KICK_DELAY."""
    for mac in list(idle_since):
        if mac not in stations or mac in connected_macs:
            del idle_since[mac]
    for mac in stations - connected_macs:
        idle_since.setdefault(mac, now)
    return [mac for mac, since in idle_since.items() if now - since > KICK_DELAY]


def _wifi_tool(interface, *args):
    """Output of the first hotspot control tool that works, or None."""
    for tool in _WIFI_TOOLS:
        try:
            result = subprocess.run([tool, "-i", interface, *args], capture_output=True, text=True, timeout=5)
        except (OSError, subprocess.TimeoutExpired):
            continue
        # Not the exit code: "wpa_cli all_sta" ends with 255 also when it worked
        if "Failed to connect" not in result.stdout:
            return result.stdout
    return None


def _interface_of(ip):
    """Network interface that has address `ip` (wlan0 when it cannot be found)."""
    try:
        output = subprocess.run(["ip", "-o", "-4", "addr", "show"], capture_output=True, text=True, timeout=5).stdout
    except (OSError, subprocess.TimeoutExpired):
        return "wlan0"
    for line in output.splitlines():
        fields = line.split()
        if len(fields) >= 4 and fields[3].split("/")[0] == ip:
            return fields[1]
    return "wlan0"


class _Client:
    def __init__(self, ip):
        self.ip = ip
        self.station = _read_arp(ip)  # (MAC, interface) on the hotspot
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
        interface = _interface_of(self.ip)

        clients = {}
        idle_since = {}  # MAC -> since when that hotspot station has no connection to the scoreboard
        next_station_check = 0
        while True:
            readable, _, _ = select.select([sock] + list(clients), [], [], 1)
            now = time.monotonic()
            for s in readable:
                if s is sock:  # New connection
                    connection, client_address = s.accept()
                    print(f"Connection from {client_address} has been established!")
                    connection.setblocking(0)
                    clients[connection] = _Client(client_address[0])
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
            if now >= next_station_check:
                next_station_check = now + STATION_CHECK_INTERVAL
                self._log_off_idle_stations(interface, clients, idle_since, now)
            self.connected = len(clients)

    def _close(self, s, clients, reason):
        print(f"Connection {reason}")
        del clients[s]
        s.close()
        self.commands.put(CONNECTION_LOST)

    @staticmethod
    def _log_off_idle_stations(interface, clients, idle_since, now):
        output = _wifi_tool(interface, "all_sta")
        if output is None:  # no hotspot control available (e.g. not a Raspberry Pi): nothing to do
            return
        for client in clients.values():
            client.station = client.station or _read_arp(client.ip)  # ARP may not have had it at connect
        connected_macs = {client.station[0] for client in clients.values() if client.station}
        for mac in idle_stations(idle_since, parse_stations(output), connected_macs, now):
            del idle_since[mac]
            if "OK" in (_wifi_tool(interface, "deauthenticate", mac) or ""):
                print(f"Logged {mac} off the WiFi: no connection to the scoreboard, so it can connect again")
            else:
                print(f"Could not log {mac} off the WiFi")
