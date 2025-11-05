def arm(conn):
    print("Arming aircraft...")
    conn.arducopter_arm()
    conn.motors_armed_wait()
    print("CAUTION: Aircraft armed")

def disarm(conn):
    print("Disarming aircraft...")
    conn.arducopter_disarm()
    conn.motors_disarmed_wait()
    print("Aircraft safe (disarmed)")

def wait_for_GPS_fix(conn):
    print("Waiting for GPS...")
    conn.wait_gps_fix()
    print("GPS fixed")