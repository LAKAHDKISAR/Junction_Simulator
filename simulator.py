import time
from traffic_management import (
    lane_queues,
    priority_lane_active,
    priority_should_end,
    select_lane,
    vehicles_to_move,
    release_vehicles,
    update_lights,
    LANES,
    traffic_lights,
)
from traffic_generator import Generate_vehicle

priority_active = False
SIMULATION_STEPS = 30
last_active_lane = None  # To remember the last active lane when all are empty so as to avoid green light for empty lanes.

for step in range(SIMULATION_STEPS):
    print("\n-----------------------------")

    # Generating vehicles
    Generate_vehicle()

    # Checking priority condition
    if priority_lane_active():
        priority_active = True
    elif priority_should_end():
        priority_active = False

    # Selecting the lane
    active_lane = select_lane(priority_active, last_active_lane)

    # Calculating the vehicles to serve
    vehicles_to_release = vehicles_to_move()

    # Updating the lights and vehicles to serve
    update_lights(active_lane)
    release_vehicles(active_lane, vehicles_to_release)

    if active_lane:
        last_active_lane = active_lane

    # Displaying state
    for lane in LANES:
        print("{}: {} vehicles -------> {}".format(lane, len(lane_queues[lane]), traffic_lights[lane]))

    time.sleep(1)
