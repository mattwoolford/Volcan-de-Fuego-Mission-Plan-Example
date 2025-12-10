import argparse
import os
import platform

from colorama import just_fix_windows_console
from pymavlink import mavutil

from aircraft import Aircraft
from geometry import add_polar_waypoints
from mission import Mission
from settings import SETTINGS

if platform.system() == "Windows":
    os.system("color")  # Necessary to print terminal colours in some versions of Windows

just_fix_windows_console()  # Fix windows console terminal colours

# Set possible CLI arguments
argsParser = argparse.ArgumentParser()
argsParser.add_argument("-v", "--verbose", action="store_true", help="Set to see enhanced logging of communications.")
argsParser.add_argument("--protocol",
                        help=f"The protocol to use for connecting to the aircraft (TCP/UDP). Default: {SETTINGS['CONNECTION']['PROTOCOL']}")
argsParser.add_argument("--host",
                        help=f"The host IP address for connecting to the aircraft. Default: {SETTINGS['CONNECTION']['HOST']}")
argsParser.add_argument("-p",
                        "--port",
                        help=f"The port number to use for connecting to the aircraft. Default: {SETTINGS['CONNECTION']['PORT']}")

# Get supplied CLI arguments
args = argsParser.parse_args()
enable_verbose_logging = True if args.verbose is not None else False
protocol = args.protocol if args.protocol is not None else SETTINGS["CONNECTION"]["PROTOCOL"]
host = args.host if args.host is not None else SETTINGS["CONNECTION"]["HOST"]
port = args.port if args.port is not None else SETTINGS["CONNECTION"]["PORT"]

if enable_verbose_logging:
    print("Verbose logging enabled")

mavlink = mavutil.mavlink

start = SETTINGS["MISSION"]["START"]
target = SETTINGS["MISSION"]["TARGET"]

# Connect to MAVLink aircraft
ac = Aircraft(protocol=protocol, host=host, port=port)
ac.connect(protocol=protocol, host=host, port=port)

# Calculate polar waypoint lat/long coordinates
waypoints = add_polar_waypoints(start, target)
waypoints.pop()
start_3d_waypoint = (start[0], start[1], 0)
via_3d_waypoints = [(wp[0], wp[1], target[2]) for wp in waypoints]

# Create a mission
mission = Mission(ac,
                  start_3d_waypoint,
                  via_3d_waypoints,
                  enable_verbose_logs=enable_verbose_logging)

# Start the mission
mission.start()
