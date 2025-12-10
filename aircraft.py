from pymavlink import mavutil
from termcolor import cprint

from settings import SETTINGS
from utils.print import eprint, sprint, wprint


class Aircraft:
    '''
    Aircraft

    This class interfaces with the aircraft to connect, send, and receive commands.
    '''

    def __init__(self,
                 protocol: str = SETTINGS["CONNECTION"]["PROTOCOL"],
                 host: str = SETTINGS["CONNECTION"]["HOST"],
                 port: int | str = SETTINGS["CONNECTION"]["PORT"]):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.conn = None

    def arm(self):
        eprint("WARNING: Arming aircraft...")
        self._conn.arducopter_arm()
        self._conn.motors_armed_wait()
        wprint("CAUTION: Aircraft armed")
        sprint("Aircraft ready for takeoff")

    def check_mode(self, mode):
        if not mode in self._conn.mode_mapping():
            eprint(f"Unknown mode : {mode}")
            print(f"Mode must be one of: {list(self._conn.mode_mapping().keys())}")
            return False
        return True

    @property
    def conn(self):
        return self._conn

    @conn.setter
    def conn(self, connection_url: str):
        try:
            if connection_url is None:
                raise AttributeError("Connection URL is None")
            cprint(f"Connecting to MAVLink at {connection_url}...", "yellow")
            conn = mavutil.mavlink_connection(connection_url)
        except AttributeError:
            self._conn = None
            return
        except Exception as e:
            eprint(f"Error connecting to MAVLink at {connection_url}")
            raise Exception(e)
        conn.wait_heartbeat(True)
        cprint(f"Connected to MAVLink at {connection_url}", "green")
        sprint("Aircraft connected")
        self._conn = conn

    def connect(self,
                protocol: str = SETTINGS["CONNECTION"]["PROTOCOL"],
                host: str = SETTINGS["CONNECTION"]["HOST"],
                port: int | str = SETTINGS["CONNECTION"]["PORT"]):
        self.protocol = protocol.lower()
        self.host = host.lower()
        self.port = port
        connection_str = ":".join([self.protocol, self.host, self.port])
        self.conn = connection_str

    def disarm(self):
        wprint("Disarming aircraft...")
        self._conn.arducopter_disarm()
        self._conn.motors_disarmed_wait()
        sprint("Aircraft safe (disarmed)")

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, host: str):
        self._host = host.lower()

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, port: int | str):
        self._port = str(port).lower()

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, protocol: str):
        self._protocol = protocol.lower()

    def set_mode(self, mode):
        if not self.check_mode(mode):
            eprint(f"Unknown mode: {mode}")
            raise Exception(f"Unknown mode supplied: {mode}")
        print(f"Setting flight mode to {mode.upper()}...")
        self._conn.mav.set_mode_send(
                self._conn.target_system,
                mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                self._conn.mode_mapping()[mode]
        )
        self._conn.recv_match(type='COMMAND_ACK', blocking=True)
        wprint(f"Flight mode set to {mode.upper()}")

    def takeoff(self):
        eprint("WARNING: Aircraft taking off...")
        self.set_mode("TAKEOFF")

    def wait_for_gps_fix(self):
        cprint("Waiting for GPS...", "yellow")
        self._conn.wait_gps_fix()
        cprint("GPS fixed", "green")
