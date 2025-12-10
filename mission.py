import time

from pymavlink import mavutil
from termcolor import cprint

from aircraft import Aircraft
from utils.print import sprint

type Waypoint = tuple[float, float, int]


class Mission:
    '''
    Mission

    This class is a controller for sending mission instructions
    '''

    def __init__(self,
                 ac: Aircraft,
                 start: Waypoint,
                 via: list[Waypoint] = [],
                 end: Waypoint | None = None,
                 enable_verbose_logs: bool = False):
        self._ac = ac
        self._start = start
        self._end = end if end is not None else start
        self._wp = [wp for wp in [self._start, *via, end] if wp is not None]
        self._verbose_logging_is_enabled = enable_verbose_logs

    def add_waypoint(self, waypoint: Waypoint, position: int | None = None):
        if position is None:
            position = len(self._wp)
        if position == len(self._wp):
            self._wp.append(waypoint)
            self._end = waypoint
        elif position < len(self._wp):
            if position <= 0:
                raise IndexError("The position must be greater than or equal to 1")
            elif position == 1:
                self._start = waypoint
            self._wp.insert(position - 1, waypoint)
        else:
            raise IndexError(f"Position {position} is out of range. The maximum position is {len(self._wp)}")

    def start(self):
        conn = self._ac.conn
        # Set home point to the end location (same as the start location if no end location was specified)
        if self._verbose_logging_is_enabled:
            print(f"Setting home location to end location (Lat: {self._end[0]}, Lon: {self._end[1]})")
        conn.mav.command_long_send(
                conn.target_system,
                conn.target_component,
                mavutil.mavlink.MAV_CMD_DO_SET_HOME,
                0,
                0,  # confirmation
                0,  # 0 = set home to the provided location / 1 = set home to the current location
                0,
                0,
                self._end[0],
                self._end[1],
                0,
        )
        msg = conn.recv_match(type=['COMMAND_ACK'], blocking=True)
        if self._verbose_logging_is_enabled:
            print(msg)
        cprint("Home location set", "green")
        # Upload waypoints to the aircraft
        cprint("Uploading waypoints...", "yellow")
        self.send_waypoints()
        # Arm the aircraft
        self._ac.arm()
        time.sleep(5)
        # Take off
        self._ac.takeoff()
        time.sleep(5)
        # Traverse mission
        self._ac.set_mode("AUTO")
        # Wait for mission to complete
        sprint("Mission in progress")
        msg = conn.recv_match(type=['MISSION_ACK'], blocking=True)
        if self._verbose_logging_is_enabled:
            print(msg)

    def send_waypoints(self):
        conn = self._ac.conn
        # Clear all current waypoints
        conn.waypoint_clear_all_send()
        # Send new waypoints
        conn.waypoint_count_send(len(self._wp))
        for i in range(0, len(self._wp)):
            # Wait for mission request before sending next waypoint
            msg = conn.recv_match(type=['MISSION_REQUEST_INT', 'MISSION_REQUEST'], blocking=True)
            # Send waypoint
            wp = self._wp[i]
            if self._verbose_logging_is_enabled:
                print(msg)
                print(f"Wp: {wp}")
                print(f"Sending waypoint {i}: Lat: {wp[0]}, Lon: {wp[1]}, Alt: {wp[2]}")
            # Build and send waypoint message (MISSION_ITEM_INT)
            conn.mav.send(mavutil.mavlink.MAVLink_mission_item_int_message(
                    conn.target_system,
                    conn.target_component,
                    i,
                    mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                    mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                    0,
                    1,
                    0.0,  # hold time - ignore by fixed wing so 0
                    10.0,  # acceptance radius (m)
                    0.0 if i == (len(self._wp) - 1) else 10.0,  # pass radius (m)
                    # 0 to pass through the WP, if > 0 radius to pass by WP. Positive value for clockwise orbit,
                    # negative value for counter-clockwise orbit. Allows trajectory control.
                    0,  # Desired yaw angle at waypoint (rotary wing). NaN to use the current system yaw heading mode
                    # (e.g. yaw towards next waypoint, yaw to home, etc.)
                    int(wp[0] * 10 ** 7),  # Lat
                    int(wp[1] * 10 ** 7),  # Long
                    wp[2],  # Altitude (m)
            ))
        sprint("Mission ready")
