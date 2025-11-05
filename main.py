import time

from pymavlink import mavutil

from actions import *

mavlink = mavutil.mavlink

# Connect to MAVLink
protocol = "TCP"
host = "127.0.0.1"
port = 14550
protocol = protocol.lower()
connection_str = ":".join([protocol, host, str(port)])
print(f"Connecting to MAVLink at {protocol}://{host}:{port}...")
conn = mavutil.mavlink_connection(connection_str)
conn.wait_heartbeat()
print(f"Connected to MAVLink at {protocol}://{host}:{port}")
wait_for_GPS_fix(conn)
arm(conn)
time.sleep(10)
disarm(conn)