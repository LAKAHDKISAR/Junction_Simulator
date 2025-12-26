import random
from traffic_management import lane_queues, LEFT_TURNING_LANES, LANES_CONTROLLED, INCOMING_LANES


vehicle_id = 0
def Generate_vehicle():
    global vehicle_id

    for lane in LANES_CONTROLLED + LEFT_TURNING_LANES:
        num_vehicles = random.randint(0, 3) 
        for i in range(num_vehicles):
            if random.random() < 0.5:
                vehicle_id += 1
                lane_queues[lane].append(vehicle_id)