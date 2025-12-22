from collections import deque

LANES = ["AL2", "BL2", "CL2", "DL2", "AL1", "BL1", "CL1", "DL1", "AL3", "BL3", "CL3", "DL3"]

PRIORITY_LANE = "AL2"
PRIORITY_START_COUNT = 10
PRIORITY_END_COUNT = 5
TIME_PER_VEHICLE = 1  # unit time per vehicle 

# Queues
lane_queues = {
    lane: deque() for lane in LANES
}

# States of the traffic lights
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


# Lane Selection  
def select_lane(priority_active, last_active_lane=None):
    # Exception for priority otherwise selecting the lane with max vehicles
    if priority_active:
        return PRIORITY_LANE

    # When all lanes are empt then returining the last active lane
    if all(len(lane_queues[lane]) == 0 for lane in LANES):
        return last_active_lane

    return max(
        LANES,
        key=lambda lane: len(lane_queues[lane])
    )


#Vechicles to serve
def vehicles_to_move():

    total_vehicles = sum(len(q) for q in lane_queues.values())
    number_of_lanes = len(LANES)
    vehicles = total_vehicles // number_of_lanes
    return max(1, vehicles)


def release_vehicles(lane, count):

    for _ in range(count):
        if lane_queues[lane]:
            lane_queues[lane].popleft()


# Updating the traffic lights and green only for one active lane
def update_lights(active_lane):

    for lane in traffic_lights:
        traffic_lights[lane] = "GREEN" if lane == active_lane else "RED"


def lane_status():
    status = {}
    for lane in LANES:
        status[lane] = {
            "vehicles": len(lane_queues[lane]),
            "light": traffic_lights[lane]
        }
    return status