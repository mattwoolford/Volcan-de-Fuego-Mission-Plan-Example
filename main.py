import argparse
import os
import platform

from colorama import just_fix_windows_console
from pymavlink import mavutil

from aircraft import Aircraft
from defaults import DEFAULTS
from mission import Mission

if platform.system() == "Windows":
    os.system("color")  # Necessary to print terminal colours in some versions of Windows

just_fix_windows_console()  # Fix windows console terminal colours

# Set possible CLI arguments
argsParser = argparse.ArgumentParser()
argsParser.add_argument("-v", "--verbose", action="store_true", help="Set to see enhanced logging of communications.")
argsParser.add_argument("--protocol",
                        help=f"The protocol to use for connecting to the aircraft (TCP/UDP). Default: {DEFAULTS['CONNECTION']['PROTOCOL']}")
argsParser.add_argument("--host",
                        help=f"The host IP address for connecting to the aircraft. Default: {DEFAULTS['CONNECTION']['HOST']}")
argsParser.add_argument("-p",
                        "--port",
                        help=f"The port number to use for connecting to the aircraft. Default: {DEFAULTS['CONNECTION']['PORT']}")

# Get supplied CLI arguments
args = argsParser.parse_args()
enable_verbose_logging = True if args.verbose is not None else False
protocol = args.protocol if args.protocol is not None else DEFAULTS["CONNECTION"]["PROTOCOL"]
host = args.host if args.host is not None else DEFAULTS["CONNECTION"]["HOST"]
port = args.port if args.port is not None else DEFAULTS["CONNECTION"]["PORT"]

if enable_verbose_logging:
    print("Verbose logging enabled")

mavlink = mavutil.mavlink
target = (14.4746372, -90.8800006)

# Connect to MAVLink aircraft
ac = Aircraft(protocol=protocol, host=host, port=port)
ac.connect(protocol=protocol, host=host, port=port)

# Create a mission
mission = Mission(ac,
                  (14.4324619, -90.9353372, 0),
                  [(14.4980096, -90.9123802, 4000), (14.4536310, -90.8512688, 4000)],
                  enable_verbose_logs=enable_verbose_logging)

# Start the mission
mission.start()
