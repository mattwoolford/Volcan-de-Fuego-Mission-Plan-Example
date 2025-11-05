from MavLink_messages import *
from pymavlink import mavutil

# Connect to MAVLink
protocol = "TCP"
host = "127.0.0.1"
port = 5760
protocol = protocol.lower()
connection_str = ":".join([protocol, host, str(port)])
print(connection_str)
print(f"Connecting to MAVLink at {protocol}://{host}:{port}...")
conn = mavutil.mavlink_connection(connection_str)
conn.wait_heartbeat()
print(f"Connected to MAVLink at {protocol}://{host}:{port}")

while True:
    msg = conn.recv_msg()
    if not msg:
        continue
    if msg.get_type() == HEARTBEAT:
        print(f"HEARTBEAT: {msg}")
