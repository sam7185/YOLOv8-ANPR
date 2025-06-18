# utils/tracking.py

# This module defines two virtual lines and checks if a vehicle's center
# point crosses both in order (entry and exit).

crossed_vehicles = set()

# Example boundaries
ENTRY_LINE_Y = 300
EXIT_LINE_Y = 400

def check_crossing(center):
    x, y = center

    if ENTRY_LINE_Y < y < EXIT_LINE_Y:
        vehicle_id = f"{x}-{y}"
        if vehicle_id not in crossed_vehicles:
            crossed_vehicles.add(vehicle_id)
            return True

    return False
