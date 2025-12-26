import pygame
import sys

from traffic_management import LANES_CONTROLLED, LEFT_TURNING_LANES, lane_queues, INCOMING_LANES, priority_lane_active, priority_should_end, select_lane, update_lights, traffic_lights, green_light_duration, vehicles_to_move, release_vehicles

from traffic_generator import Generate_vehicle


pygame.init()
WIDTH, HEIGHT = 1500, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Traffic Simulation")
clock = pygame.time.Clock()

Background_Color = Army_green = (69, 75, 27)
Road_Color = Dark_grey =(169, 169, 169)
Intersection_Color = grey =(128, 128, 128)
Lane_Color = White = (255, 255, 255)


CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
ROAD_WIDTH = 200
LANE_WIDTH = ROAD_WIDTH // 3
DASH_LEN = 18
GAP_LEN = 12

# ---Mapping lane position ----------------------
LANE_SCREEN_POSITION = {
    "AL1": {"x": CENTER_X - LANE_WIDTH, "y_start": 0, "direction": "down"},
    "AL2": {"x": CENTER_X, "y_start": 0, "direction": "down"},
    "AL3": {"x": CENTER_X + LANE_WIDTH, "y_start": 0, "direction": "down"},

    "BL1": {"x": CENTER_X + LANE_WIDTH, "y_start": HEIGHT, "direction": "up"},
    "BL2": {"x": CENTER_X, "y_start": HEIGHT, "direction": "up"},
    "BL3": {"x": CENTER_X - LANE_WIDTH, "y_start": HEIGHT, "direction": "up"},

    "CL1": {"y": CENTER_Y - LANE_WIDTH, "x_start": WIDTH, "direction": "left"},   
    "CL2": {"y": CENTER_Y, "x_start": WIDTH, "direction": "left"},               
    "CL3": {"y": CENTER_Y + LANE_WIDTH, "x_start": WIDTH, "direction": "left"},

    "DL1": {"y": CENTER_Y + LANE_WIDTH, "x_start": 0, "direction": "right"},
    "DL2": {"y": CENTER_Y, "x_start": 0, "direction": "right"},             
    "DL3": {"y": CENTER_Y - LANE_WIDTH, "x_start": 0, "direction": "right"}
}

Vehicle_Size = 15
Vehicle_Spacing = 20
Vehicle_Speed = 2
Vehicle_Color = black = (0, 0, 0)

# empty lane initially , for moving vehicles
moving_vehicles = {lane: [] for lane in lane_queues}

INCOMING_LANES = ["AL1", "BL1", "CL1", "DL1"]

Stop_line = {
    "down": CENTER_Y - ROAD_WIDTH // 2 - Vehicle_Size,
    "up": CENTER_Y + ROAD_WIDTH // 2,
    "left": CENTER_X + ROAD_WIDTH // 2,
    "right": CENTER_X - ROAD_WIDTH // 2 - Vehicle_Size,
}

Light_Radius = 10
TRAFFIC_LIGHT_POSITION = {
    "AL2": (CENTER_X - LANE_WIDTH, CENTER_Y - ROAD_WIDTH // 2 - 30),
    "BL2": (CENTER_X + LANE_WIDTH, CENTER_Y + ROAD_WIDTH // 2 + 30),
    "CL2": (CENTER_X + ROAD_WIDTH // 2 + 30, CENTER_Y - LANE_WIDTH),
    "DL2": (CENTER_X - ROAD_WIDTH // 2 - 30, CENTER_Y + LANE_WIDTH),
}
all_lanes = set(LANES_CONTROLLED) | set(LEFT_TURNING_LANES)
last_release_time = {lane: 0 for lane in all_lanes}
Release_interval = 200

def dashed_lane_line_vertical(x, start_y, end_y):
    y = start_y
    while y < end_y:
        pygame.draw.line(
            screen,
            Lane_Color,
            (x, y),
            (x, min(y + DASH_LEN, end_y)),
            2
        )
        y += DASH_LEN + GAP_LEN


def dashed_lane_line_horizontal(start_x, end_x, y):
    x = start_x
    while x < end_x:
        pygame.draw.line(
            screen,
            Lane_Color,
            (x, y),
            (min(x + DASH_LEN, end_x), y),
            2
        )
        x += DASH_LEN + GAP_LEN

def roads_design():
    screen.fill(Background_Color)

    intersection_rect = pygame.Rect(CENTER_X - ROAD_WIDTH // 2, CENTER_Y - ROAD_WIDTH // 2, ROAD_WIDTH, ROAD_WIDTH)

    # -------- A --------
    road_a_rect = pygame.Rect(CENTER_X - ROAD_WIDTH // 2, 0, ROAD_WIDTH, CENTER_Y - ROAD_WIDTH // 2)
    pygame.draw.rect(screen, Road_Color, road_a_rect)
    pygame.draw.line(screen, Lane_Color, (road_a_rect.left + LANE_WIDTH, road_a_rect.top), (road_a_rect.left + LANE_WIDTH, road_a_rect.bottom), 2) 
    dashed_lane_line_vertical(road_a_rect.left + 2 * LANE_WIDTH, road_a_rect.top, road_a_rect.bottom)  

    # ------ B --------
    road_b_rect = pygame.Rect(CENTER_X - ROAD_WIDTH // 2, CENTER_Y + ROAD_WIDTH // 2, ROAD_WIDTH, HEIGHT - (CENTER_Y + ROAD_WIDTH // 2))
    pygame.draw.rect(screen, Road_Color, road_b_rect)
    pygame.draw.line(screen, Lane_Color, (road_b_rect.left + 2 * LANE_WIDTH, road_b_rect.top), (road_b_rect.left + 2 * LANE_WIDTH, road_b_rect.bottom), 2)
    dashed_lane_line_vertical(road_b_rect.left + LANE_WIDTH, road_b_rect.top, road_b_rect.bottom)

    # -------- C --------
    road_c_rect = pygame.Rect(CENTER_X + ROAD_WIDTH // 2, CENTER_Y - ROAD_WIDTH // 2, WIDTH - (CENTER_X + ROAD_WIDTH // 2), ROAD_WIDTH)
    pygame.draw.rect(screen, Road_Color, road_c_rect)
    dashed_lane_line_horizontal(road_c_rect.left, road_c_rect.right, road_c_rect.top + 2 * LANE_WIDTH)
    pygame.draw.line(screen, Lane_Color,(road_c_rect.left, road_c_rect.top + LANE_WIDTH), (road_c_rect.right, road_c_rect.top + LANE_WIDTH), 2)

    # -------- D --------
    road_d_rect = pygame.Rect(0, CENTER_Y - ROAD_WIDTH // 2, CENTER_X - ROAD_WIDTH // 2, ROAD_WIDTH)
    pygame.draw.rect(screen, Road_Color, road_d_rect)
    dashed_lane_line_horizontal(road_d_rect.left, road_d_rect.right, road_d_rect.top + LANE_WIDTH)
    pygame.draw.line(screen, Lane_Color, (road_d_rect.left, road_d_rect.top + 2 * LANE_WIDTH), (road_d_rect.right, road_d_rect.top + 2 * LANE_WIDTH), 2)

    # - Centre box -
    pygame.draw.rect(screen, Intersection_Color, intersection_rect)


def vehicle_design():
    for lane, vehicles in moving_vehicles.items():
        for v in vehicles:
            pygame.draw.rect(screen, Vehicle_Color, (v["x"], v["y"], Vehicle_Size, Vehicle_Size))

def add_new_vehicles(active_lane):
    lanes_to_release = LEFT_TURNING_LANES + ([active_lane] if active_lane else [])
    current_time = pygame.time.get_ticks()

    for lane in lanes_to_release:
        queue = lane_queues[lane]
        lane_info = LANE_SCREEN_POSITION[lane]
        count = vehicles_to_move(lane)
        if queue and current_time - last_release_time[lane] >= Release_interval:
            vehicle = queue.popleft()
            if lane_info["direction"] in ["down", "up"]:
                x = lane_info["x"] - Vehicle_Size // 2
                y = lane_info["y_start"]
            else:
                x = lane_info["x_start"]
                y = lane_info["y"] - Vehicle_Size // 2

            moving_vehicles[lane].append({
                "id": vehicle["id"],
                "intent": vehicle["intent"],
                "x": x,
                "y": y
            })
            last_release_time[lane] = current_time

def move_vehicles():
    for lane, vehicles in moving_vehicles.items():
        lane_info = LANE_SCREEN_POSITION[lane]
        direction = lane_info["direction"]
        stop = Stop_line[direction]

        new_list = []

        for v in vehicles:
            light = traffic_lights.get(lane, "RED")
            if lane in LANES_CONTROLLED and light == "RED":
                if direction == "down" and v["y"] + Vehicle_Speed >= stop:
                    v["y"] = stop
                    new_list.append(v)
                    continue

                if direction == "up" and v["y"] - Vehicle_Speed <= stop:
                    v["y"] = stop
                    new_list.append(v)
                    continue

                if direction == "right" and v["x"] + Vehicle_Speed >= stop:
                    v["x"] = stop
                    new_list.append(v)
                    continue

                if direction == "left" and v["x"] - Vehicle_Speed <= stop:
                    v["x"] = stop
                    new_list.append(v)
                    continue

            if direction == "down":
                v["y"] += Vehicle_Speed
            elif direction == "up":
                v["y"] -= Vehicle_Speed
            elif direction == "right":
                v["x"] += Vehicle_Speed
            elif direction == "left":
                v["x"] -= Vehicle_Speed

            if 0 <= v["x"] <= WIDTH and 0 <= v["y"] <= HEIGHT:
                new_list.append(v)

        moving_vehicles[lane] = new_list

def traffic_lights_design():
    for lane, pos in TRAFFIC_LIGHT_POSITION.items():
        state = "RED"
        if lane in traffic_lights:
            state = traffic_lights[lane]

        color = (0, 255, 0) if state == "GREEN" else (255, 0, 0)
        pygame.draw.circle(screen, color, pos, Light_Radius)

def main():
    running = True
    last_gen_time = 0
    GEN_INTERVAL = 1000
    last_active_lane = None
    active_lane = None
    light_start_time = pygame.time.get_ticks()
    green_duration = 0

    while running:
        current_time = pygame.time.get_ticks()
        if current_time - last_gen_time > GEN_INTERVAL:
            Generate_vehicle()
            last_gen_time = current_time

        if priority_lane_active():
            active_lane = "AL2"
        elif priority_should_end():
            active_lane = select_lane(False, last_active_lane)
        else:
            active_lane = select_lane(False, last_active_lane)

        if active_lane != last_active_lane:
            update_lights(active_lane)
            green_duration = green_light_duration(active_lane) * 1000 
            light_start_time = current_time
            last_active_lane = active_lane

        if active_lane:
            add_new_vehicles(active_lane)

        if current_time - light_start_time >= green_duration:
            active_lane = select_lane(False, last_active_lane)
            update_lights(active_lane)
            green_duration = green_light_duration(active_lane) * 1000
            light_start_time = current_time
            last_active_lane = active_lane

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        move_vehicles()
        roads_design()
        vehicle_design()
        traffic_lights_design()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()