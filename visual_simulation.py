import pygame
import sys

from traffic_management import LANES_CONTROLLED, LEFT_TURNING_LANES, lane_queues, INCOMING_LANES
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
LANE_SCREEN_POS = {
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

def add_new_vehicles():
    for lane in LANES_CONTROLLED + LEFT_TURNING_LANES:
        queue = lane_queues[lane]
        lane_info = LANE_SCREEN_POS[lane]

        while queue:
            vehicle_id = queue.popleft()
            if lane_info["direction"] in ["down", "up"]:
                x = lane_info["x"] - Vehicle_Size // 2
                y = lane_info["y_start"]
            else:  # left or right
                x = lane_info["x_start"]
                y = lane_info["y"] - Vehicle_Size // 2

            moving_vehicles[lane].append({"id": vehicle_id, "x": x, "y": y})

def move_vehicles():
    for lane, vehicles in moving_vehicles.items():
        lane_info = LANE_SCREEN_POS[lane]
        new_list = []
        for v in vehicles:
            # Movving the vehciles based on the direction
            if lane_info["direction"] == "down":
                v["y"] += Vehicle_Speed
            elif lane_info["direction"] == "up":
                v["y"] -= Vehicle_Speed
            elif lane_info["direction"] == "right":
                v["x"] += Vehicle_Speed
            elif lane_info["direction"] == "left":
                v["x"] -= Vehicle_Speed
            if 0 <= v["x"] <= WIDTH and 0 <= v["y"] <= HEIGHT:
                new_list.append(v)
        moving_vehicles[lane] = new_list

def main():
    running = True
    last_gen_time = 0
    GEN_INTERVAL = 1000 

    while running:
        current_time = pygame.time.get_ticks()
        if current_time - last_gen_time > GEN_INTERVAL:
            add_new_vehicles()
            Generate_vehicle()
            last_gen_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        move_vehicles()
        roads_design()
        vehicle_design()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()