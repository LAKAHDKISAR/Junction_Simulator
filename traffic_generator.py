import random
from traffic_management import lane_queues, LANES


vehicle_id = 0
def Generate_vehicle():
    global vehicle_id

    for lane in LANES:
        if random.random() < 0.5:      # 50% chance 
            vehicle_id += 1
            lane_queues[lane].append(vehicle_id)
