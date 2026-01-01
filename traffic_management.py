from collections import deque
import random

LANES_CONTROLLED = ["AL2", "BL2", "CL2", "DL2"]
LEFT_TURNING_LANES = ["AL3", "BL3", "CL3", "DL3"]
INCOMING_LANES = ["AL1", "BL1", "CL1", "DL1"]
LANES = LEFT_TURNING_LANES + LANES_CONTROLLED
ALL_LANES = INCOMING_LANES + LANES

PRIORITY_LANE = "AL2"
PRIORITY_START_COUNT = 5
PRIORITY_END_COUNT = 4


def time_for_vehicles():
    return random.choice([0.5, 1.0, 1.2, 1.5])  # seconds per vehicle

# Queues
lane_queues = {
    lane: deque() for lane in LANES
}

traffic_lights = {
    lane: "RED" for lane in LANES
}

# Priority Lane: 
def priority_lane_active():
    # True if Priority lane has more than set vehicles (ie 10)
    return len(lane_queues[PRIORITY_LANE]) > PRIORITY_START_COUNT


def priority_should_end():
    # True if Priority lane has less than set vehicles (ie 5)
    return len(lane_queues[PRIORITY_LANE]) < PRIORITY_END_COUNT

LANE_ORDER = ["AL2", "CL2", "BL2", "DL2"]
last_served_index = -1  

def select_lane(priority_active):
    global last_served_index

    if priority_active:
        return PRIORITY_LANE

    non_empty_lanes = [lane for lane in LANE_ORDER if len(lane_queues[lane]) > 0]
    if not non_empty_lanes:
        return None

    # in a round manner
    n = len(LANE_ORDER)
    for i in range(n):
        check_index = (last_served_index + 1 + i) % n
        lane = LANE_ORDER[check_index]
        if lane in non_empty_lanes:
            last_served_index = check_index
            return lane

    return None

VEHICLES_RELEASE_LIMIT = 15
MIN_GREEN_TIME = 2
MAX_GREEN_TIME = 15

def vehicles_to_move(lane):
    active_lane = [l for l in LANES_CONTROLLED if len(lane_queues[l]) > 0]
    if not active_lane :
        return 0

    total_vehicles = sum(len(lane_queues[l]) for l in LANES_CONTROLLED)
    n = len(active_lane)
    vehicles_per_lane = total_vehicles // n
    return min(vehicles_per_lane, VEHICLES_RELEASE_LIMIT)


def green_light_duration(lane, moving_vehicles, Time_per_vehicle):
    moving_count = len(moving_vehicles[lane])  
    queued_count = len(lane_queues[lane])
    total_vehicles = moving_count + queued_count

    total_vehicles = min(total_vehicles, VEHICLES_RELEASE_LIMIT) #release limit

    # Total duration needed
    duration = total_vehicles * Time_per_vehicle

    # Clamp duration
    if duration < MIN_GREEN_TIME:
        duration = MIN_GREEN_TIME
    elif duration > MAX_GREEN_TIME:
        duration = MAX_GREEN_TIME

    print(f"Green light duration: {duration}s for {lane} ({total_vehicles} vehicles)")
    return duration

vehicles_exited = 0
def release_vehicles(lane, count):
    global vehicles_exited

    if lane in LANES_CONTROLLED:
        released = min(count, len(lane_queues[lane]))
        for i in range(released):
            lane_queues[lane].popleft()
            vehicles_exited += 1

    for left_lane in LEFT_TURNING_LANES:
        while lane_queues[left_lane]:
            lane_queues[left_lane].popleft()
            vehicles_exited += 1

# Updating the traffic lights and green only for one active lane and also the left trun lanes
def update_lights(active_lane):

    for lane in traffic_lights:
        if lane.endswith("3"):
            traffic_lights[lane] = "GREEN"
        else: 
            traffic_lights[lane] = "GREEN" if lane == active_lane else "RED"


def lane_status():
    status = {}
    for lane in LANES:
        status[lane] = {
            "vehicles": len(lane_queues[lane]),
            "light": traffic_lights[lane]
        }
    return status