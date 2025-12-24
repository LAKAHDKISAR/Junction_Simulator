from collections import deque
import random

LANES = ["AL2", "BL2", "CL2", "DL2", "AL1", "BL1", "CL1", "DL1", "AL3", "BL3", "CL3", "DL3"]

PRIORITY_LANE = "AL2"
PRIORITY_START_COUNT = 10
PRIORITY_END_COUNT = 5


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


last_served=-1
def select_lane(priority_active, last_active_lane=None):
    global last_served
    # Exception for priority
    if priority_active:
        return PRIORITY_LANE
    
    #only control needing lanes 
    control_needing_lanes = [lane for lane in LANES if lane.endswith(("1","2"))] 

    # When all lanes are empt then returining the last active lane
    if all(len(lane_queues[lane]) == 0 for lane in control_needing_lanes):
        return last_active_lane
    

    # Selecting in a circular manner for each lane. (Circular Queue type approach)
    n = len(control_needing_lanes)
    for i in range(n):
        last_served = (last_served + 1) % n
        lane = control_needing_lanes[last_served]
        if len(lane_queues[lane]) > 0:
            return lane

    return last_active_lane


VEHICLES_RELEASE_LIMIT = 15
MIN_GREEN_TIME = 2
MAX_GREEN_TIME = 15

def vehicles_to_move(lane):
    normal_lanes = [l for l in LANES if l.endswith(("1","2"))]
    total_vehicles = sum(len(lane_queues[lane]) for l in normal_lanes)
    n = len(normal_lanes)
    vehicles_per_lane = total_vehicles // n
    return min(vehicles_per_lane, VEHICLES_RELEASE_LIMIT)


def green_light_duration(lane):

    count = vehicles_to_move(lane)
    TIME_PER_VEHICLE = time_for_vehicles()
    duration =  count * TIME_PER_VEHICLE

    if duration < MIN_GREEN_TIME:
        duration = MIN_GREEN_TIME
    elif duration > MAX_GREEN_TIME:
        duration = MAX_GREEN_TIME

    print(f"Green light duration: {duration} seconds for {lane}. Vehicles released: {count}")
    return duration


def release_vehicles(lane, count):
    for i in range(count):
        if lane_queues[lane]:
            lane_queues[lane].popleft()

    # For free lane (left trun lanes that dont need to be controlled)


    left_trun_lanes = [l for l in LANES if l.endswith("3")]
    for left_lane in left_trun_lanes:
        # Such as how it is in real world now bound by time constraint. Only vehicles that can pass in certain time released.
        vehicles_to_move = min(count, len(lane_queues[left_lane]))
        for i in range(vehicles_to_move):
            lane_queues[left_lane].popleft()


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