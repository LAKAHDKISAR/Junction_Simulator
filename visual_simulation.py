import pygame
import sys
import random
import math

from traffic_management import LANES_CONTROLLED, LEFT_TURNING_LANES, lane_queues, INCOMING_LANES, priority_lane_active, priority_should_end, select_lane, update_lights, traffic_lights, green_light_duration, vehicles_to_move, release_vehicles

from traffic_generator import Generate_vehicle


pygame.init()
clock = pygame.time.Clock()
WIDTH, HEIGHT = 1500, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Traffic Simulation")
clock = pygame.time.Clock()

current_light = None  
light_start_time = pygame.time.get_ticks() / 1000 
YELLOW_DURATION = 2.0
ALL_RED_DURATION = 1.0

Background_Color = Army_green = (69, 75, 27)
Road_Color = Dark_grey =(169, 169, 169)
Intersection_Color = Dark_grey =(169, 169, 169)
Lane_Color = White = (255, 255, 255)

CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
ROAD_WIDTH = 200
LANE_WIDTH = ROAD_WIDTH // 3
DASH_LEN = 18
GAP_LEN = 12

CENTER_ZONE = {
    "x_min": CENTER_X - ROAD_WIDTH//2,
    "x_max": CENTER_X + ROAD_WIDTH//2,
    "y_min": CENTER_Y - ROAD_WIDTH//2,
    "y_max": CENTER_Y + ROAD_WIDTH//2
}

def in_center(v):
    return (CENTER_ZONE["x_min"] <= v["x"] <= CENTER_ZONE["x_max"] and CENTER_ZONE["y_min"] <= v["y"] <= CENTER_ZONE["y_max"])

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

Vehicle_Spacing = 20
Vehicle_Speed = 120 
Vehicle_Color = black = (0, 0, 0)

# empty lane initially , for moving vehicles
moving_vehicles = {lane: [] for lane in lane_queues}

INCOMING_LANES = ["AL1", "BL1", "CL1", "DL1"]

Ligtht_offset = 70
TRAFFIC_LIGHT_POSITION = {
    "AL2": (CENTER_X, CENTER_Y - ROAD_WIDTH//2 + Ligtht_offset), 
    "BL2": (CENTER_X, CENTER_Y + ROAD_WIDTH//2 - Ligtht_offset),
    "CL2": (CENTER_X + ROAD_WIDTH//2 - Ligtht_offset, CENTER_Y),  
    "DL2": (CENTER_X - ROAD_WIDTH//2 + Ligtht_offset, CENTER_Y),  
}
RIGHT_TURN_ARROW_OFFSET = 22
RIGHT_TURN_ARROW_CONFIG = {
    "AL2": {"dx": -RIGHT_TURN_ARROW_OFFSET, "dy": 0,  "dir": "left"},
    "BL2": {"dx":  RIGHT_TURN_ARROW_OFFSET, "dy": 0,  "dir": "right"},
    "CL2": {"dx": 0, "dy": -RIGHT_TURN_ARROW_OFFSET, "dir": "up"},
    "DL2": {"dx": 0, "dy":  RIGHT_TURN_ARROW_OFFSET, "dir": "down"},
}

LIGHT_BOX_WIDTH = 30
LIGHT_BOX_HEIGHT = 70
LIGHT_BOX_RADIUS = 5
BULB_RADIUS = 7
BULB_SPACING = 20
LIGHT_BOX_PADDING =  BULB_RADIUS + 3

all_lanes = set(LANES_CONTROLLED) | set(LEFT_TURNING_LANES)
current_time = pygame.time.get_ticks() / 1000
last_release_time = {lane: current_time for lane in all_lanes}

Time_per_vehicle = 1.0
Release_interval = Time_per_vehicle

Turn_offset = 85  #--- for left turning vehicles

MIDDLE_LANE_SHIFT = {
    "AL2": +LANE_WIDTH,   
    "BL2": -LANE_WIDTH,   
    "DL2": -LANE_WIDTH,   
    "CL2": +LANE_WIDTH,
}

Shift_start_offset = 30  #---- for middle lane shifting to enter through incoming
Shift_speed = 40

pygame.font.init()
FONT = pygame.font.SysFont('Arial', 20)

TARGET_HEIGHT = 60

CAR_IMAGES = [
    pygame.image.load("asset/Ambulance.png").convert_alpha(),
    pygame.image.load("asset/Audi.png").convert_alpha(),
    pygame.image.load("asset/Black_viper.png").convert_alpha(),
    pygame.image.load("asset/Car.png").convert_alpha(),
    pygame.image.load("asset/Mini_truck.png").convert_alpha(),
    pygame.image.load("asset/Mini_van.png").convert_alpha(),
    pygame.image.load("asset/Police.png").convert_alpha(),
    pygame.image.load("asset/taxi.png").convert_alpha(),
    pygame.image.load("asset/truck.png").convert_alpha()
]

CAR_IMAGES = [
    pygame.transform.smoothscale(img, (int(img.get_width() * TARGET_HEIGHT / img.get_height()), TARGET_HEIGHT))
    for img in CAR_IMAGES
]

Vehicle_Width, Vehicle_Height = CAR_IMAGES[0].get_size()
Vehicle_Spacing = Vehicle_Height // 3

Stop_line = {
    "down": CENTER_Y - ROAD_WIDTH // 2 - Vehicle_Height,
    "up": CENTER_Y + ROAD_WIDTH // 2 + Vehicle_Height,
    "left": CENTER_X + ROAD_WIDTH // 2 + Vehicle_Height,
    "right": CENTER_X - ROAD_WIDTH // 2 - Vehicle_Height,
}

SIDEBAR_WIDTH = 350   
SIDEBAR_HEIGHT = 250  
SIDEBAR_BG_COLOR = (40, 40, 40)
LOG_TEXT_COLOR = (220, 220, 220)
LOG_PADDING = 10
MAX_LOG_LINES = 10

log_messages = []

OPPOSITE_DIRECTION = {
    "up": "down",
    "down": "up",
    "left": "right",
    "right": "left"
}
ARROW_BODY = 26     
ARROW_KINK = 10  
ARROW_HEAD = 10
ARROW_WIDTH = 4

Indicator_req_middle_lanes = ["BL2", "CL2", "DL2"]
Indicator_req_left_turn_lanes = ["AL3", "BL3", "CL3", "DL3"]

TREE_IMAGES = [
    pygame.image.load("Asset/RE_01.png").convert_alpha(),
    pygame.image.load("Asset/RE_02.png").convert_alpha()
]
TREE_SIZE = 60 
TREE_IMAGES = [
    pygame.transform.smoothscale(img, (TREE_SIZE, TREE_SIZE))
    for img in TREE_IMAGES
]

LAKE_IMAGE = pygame.image.load("Asset/Lake.png").convert_alpha()
LAKE_WIDTH = 200
LAKE_HEIGHT = 150
LAKE_IMAGE = pygame.transform.smoothscale(LAKE_IMAGE, (LAKE_WIDTH, LAKE_HEIGHT))
LAKE_POSITION = (
    CENTER_X + ROAD_WIDTH//2 + 40,  
    CENTER_Y + ROAD_WIDTH//2 + 40    
)
screen.blit(LAKE_IMAGE, LAKE_POSITION)

Grass_Image = pygame.image.load("Asset/grass.png").convert_alpha()
Grass_width, Grass_height = Grass_Image.get_size()
Grass_scale = 0.15
Grass_Image = pygame.transform.scale(Grass_Image,(int(Grass_Image.get_width() * Grass_scale),int(Grass_Image.get_height() * Grass_scale)))

Middle_Circle_Radius = 40
Middle_Circle_Color = grey =(128, 128, 128)

Road_border_color = (54,79,69)  
Road_border_width = 2

Crosswalk_stip_width= 4 
Crosswalk_stip_gap = 4
Crosswalk_thickness = 15
Crosswalk_color = (255, 255, 255)
Crosswalk_offset = 2

Lane_mark_offset= Crosswalk_thickness + Crosswalk_offset + 5

NUM_RAINDROPS = 200
raindrops = [{"x": random.randint(0, WIDTH), "y": random.randint(0, HEIGHT), "speed": random.randint(4, 10)} for i in range(NUM_RAINDROPS)]
rain_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
rain_surface.fill((0,0,0,0))

time_of_day = 12
time_speed = 0.01

Day_Background = (135, 206, 235)
Night_Background = (20, 24, 82)

Day_road = (50, 50, 50)
Night_road = (30, 30, 30)

Day_light = 180
Night_light = 255

def add_log(message):
    global log_messages
    log_messages.append(message)
    if len(log_messages) > MAX_LOG_LINES:
        log_messages.pop(0)

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "

    if current_line:
        lines.append(current_line.strip())

    return lines

def straight_arrow(x, y, direction, color=(245,245,245)):
    shaft = ARROW_BODY
    head = ARROW_HEAD
    w = ARROW_WIDTH

    if direction == "down":
        pygame.draw.line(screen, color, (x, y - shaft), (x, y), w)
        pygame.draw.polygon(
            screen, color,
            [(x, y + head),
             (x - head, y),
             (x + head, y)]
        )

    elif direction == "up":
        pygame.draw.line(screen, color, (x, y + shaft), (x, y), w)
        pygame.draw.polygon(
            screen, color,
            [(x, y - head),
             (x - head, y),
             (x + head, y)]
        )

    elif direction == "right":
        pygame.draw.line(screen, color, (x - shaft, y), (x, y), w)
        pygame.draw.polygon(
            screen, color,
            [(x + head, y),
             (x, y - head),
             (x, y + head)]
        )

    elif direction == "left":
        pygame.draw.line(screen, color, (x + shaft, y), (x, y), w)
        pygame.draw.polygon(
            screen, color,
            [(x - head, y),
             (x, y - head),
             (x, y + head)]
        )

def middle_lane_combined_arrow(x, y, direction, color=(245,245,245)):
    main_length = ARROW_BODY * 2
    small_arrow_length = ARROW_BODY // 2
    w = ARROW_WIDTH
    head = ARROW_HEAD
    kink = ARROW_KINK

    # Main straight arrow
    if direction == "down":
        pygame.draw.line(screen, color, (x, y - main_length), (x, y), w)
        pygame.draw.polygon(
            screen, color,
            [(x, y + head),
             (x - head, y),
             (x + head, y)]
        )
        # Small right-turn arrow points left (opposite)
        mid_y = y - main_length // 2
        pygame.draw.line(screen, color, (x, mid_y), (x - small_arrow_length, mid_y), w)
        pygame.draw.polygon(screen, color, [
            (x - small_arrow_length - head, mid_y),
            (x - small_arrow_length, mid_y - head),
            (x - small_arrow_length, mid_y + head)
        ])

    elif direction == "up":
        pygame.draw.line(screen, color, (x, y + main_length), (x, y), w)
        pygame.draw.polygon(screen, color,
                            [(x, y - head),
                             (x - head, y),
                             (x + head, y)])
        # Small right-turn arrow points right (opposite)
        mid_y = y + main_length // 2
        pygame.draw.line(screen, color, (x, mid_y), (x + small_arrow_length, mid_y), w)
        pygame.draw.polygon(screen, color, [
            (x + small_arrow_length + head, mid_y),
            (x + small_arrow_length, mid_y - head),
            (x + small_arrow_length, mid_y + head)
        ])

    elif direction == "right":
        pygame.draw.line(screen, color, (x - main_length, y), (x, y), w)
        pygame.draw.polygon(screen, color,
                            [(x + head, y),
                             (x, y - head),
                             (x, y + head)])
        # Small right-turn arrow points down (opposite)
        mid_x = x - main_length // 2
        pygame.draw.line(screen, color, (mid_x, y), (mid_x, y + small_arrow_length), w)
        pygame.draw.polygon(screen, color, [
            (mid_x, y + small_arrow_length + head),
            (mid_x - head, y + small_arrow_length),
            (mid_x + head, y + small_arrow_length)
        ])

    elif direction == "left":
        pygame.draw.line(screen, color, (x + main_length, y), (x, y), w)
        pygame.draw.polygon(screen, color,
                            [(x - head, y),
                             (x, y - head),
                             (x, y + head)])
        # Small right-turn arrow points up (opposite)
        mid_x = x + main_length // 2
        pygame.draw.line(screen, color, (mid_x, y), (mid_x, y - small_arrow_length), w)
        pygame.draw.polygon(screen, color, [
            (mid_x, y - small_arrow_length - head),
            (mid_x - head, y - small_arrow_length),
            (mid_x + head, y - small_arrow_length)
        ])


def left_turn_arrow(x, y, direction, color=(245,245,245)):
    shaft = ARROW_BODY
    kink = ARROW_KINK
    head = ARROW_HEAD
    w = ARROW_WIDTH

    if direction == "down":
        pygame.draw.line(screen, color, (x, y - shaft), (x, y), w)
        pygame.draw.line(screen, color, (x, y), (x + kink, y), w)
        pygame.draw.polygon(
            screen, color,
            [(x + kink + head, y),
             (x + kink, y - head),
             (x + kink, y + head)]
        )

    elif direction == "up":
        pygame.draw.line(screen, color, (x, y + shaft), (x, y), w)
        pygame.draw.line(screen, color, (x, y), (x - kink, y), w)
        pygame.draw.polygon(
            screen, color,
            [(x - kink - head, y),
             (x - kink, y - head),
             (x - kink, y + head)]
        )

    elif direction == "right":
        pygame.draw.line(screen, color, (x - shaft, y), (x, y), w)
        pygame.draw.line(screen, color, (x, y), (x, y - kink), w)
        pygame.draw.polygon(
            screen, color,
            [(x, y - kink - head),
             (x - head, y - kink),
             (x + head, y - kink)]
        )

    elif direction == "left":
        pygame.draw.line(screen, color, (x + shaft, y), (x, y), w)
        pygame.draw.line(screen, color, (x, y), (x, y + kink), w)
        pygame.draw.polygon(
            screen, color,
            [(x, y + kink + head),
             (x - head, y + kink),
             (x + head, y + kink)]
        )


def incoming_lane_arrows():
    offset = 60

    for lane in INCOMING_LANES:
        info = LANE_SCREEN_POSITION[lane]
        d = info["direction"]

        if d == "down":
            x = info["x"]
            y = Stop_line["down"] - offset

        elif d == "up":
            x = info["x"]
            y = Stop_line["up"] + offset

        elif d == "right":
            x = Stop_line["right"] - offset
            y = info["y"]

        elif d == "left":
            x = Stop_line["left"] + offset
            y = info["y"]

        straight_arrow(x, y, OPPOSITE_DIRECTION[d])

def middle_lane_arrows():
    offset = 20

    for lane in Indicator_req_middle_lanes:
        info = LANE_SCREEN_POSITION[lane]
        d = info["direction"]

        if d == "down":
            x = info["x"]
            y = Stop_line["down"] - offset

        elif d == "up":
            x = info["x"]
            y = Stop_line["up"] + offset

        elif d == "right":
            x = Stop_line["right"] - offset
            y = info["y"]

        elif d == "left":
            x = Stop_line["left"] + offset
            y = info["y"]

        middle_lane_combined_arrow(x, y, d)

def left_turn_lane_arrows():
    offset = 45

    for lane in Indicator_req_left_turn_lanes:
        info = LANE_SCREEN_POSITION[lane]
        d = info["direction"]

        if d == "down":
            x = info["x"]
            y = Stop_line["down"] - offset

        elif d == "up":
            x = info["x"]
            y = Stop_line["up"] + offset

        elif d == "right":
            x = Stop_line["right"] - offset
            y = info["y"]

        elif d == "left":
            x = Stop_line["left"] + offset
            y = info["y"]

        left_turn_arrow(x, y, d)

def sidebar():
    sidebar_rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, SIDEBAR_HEIGHT)
    pygame.draw.rect(screen, SIDEBAR_BG_COLOR, sidebar_rect)

    title_surface = FONT.render("Traffic Log", True, LOG_TEXT_COLOR)
    screen.blit(title_surface, (LOG_PADDING, LOG_PADDING))

    y = LOG_PADDING + 30
    line_height = FONT.get_height() + 4
    max_text_width = SIDEBAR_WIDTH - 2 * LOG_PADDING

    logs_to_show = log_messages[-MAX_LOG_LINES:]

    for log in logs_to_show:
        wrapped_lines = wrap_text(log, FONT, max_text_width)
        for line in wrapped_lines:
            if y + line_height > SIDEBAR_HEIGHT - LOG_PADDING:
                return 
            log_surface = FONT.render(line, True, LOG_TEXT_COLOR)
            screen.blit(log_surface, (LOG_PADDING, y))
            y += line_height

def lane_names():
    for lane, info in LANE_SCREEN_POSITION.items():
        text_surface = FONT.render(lane, True, (54, 69, 79))
        if info["direction"] in ["down", "up"]:
            x = info["x"] - text_surface.get_width() // 2
            y = 10 if info["direction"] == "down" else HEIGHT - 30
        else:
            x = WIDTH - text_surface.get_width() - 10 if info["direction"] == "left" else 10
            y = info["y"] - text_surface.get_height() // 2

        screen.blit(text_surface, (x, y))

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

def priority_triangles_al2():
    lane_info = LANE_SCREEN_POSITION["AL2"]
    x = lane_info["x"]
    junction_y = CENTER_Y - ROAD_WIDTH // 2  
    offset_back = 25 
    
    start_y = junction_y - offset_back 
    
    triangle_color = (255, 215, 0) 
    
    base = 20
    height = 30
    spacing = 40
    
    for i in range(3):
        y = start_y - i * spacing
        
        points = [
            (x, y),                    
            (x - base // 2, y - height),
            (x + base // 2, y - height)
        ]
        
        pygame.draw.polygon(screen, triangle_color, points)

TREE_INSTANCES = []

def generate_tree_instances():
    spacing = 120
    buffer = 100 
    TREE_INSTANCES.clear()
    for y in range(0, HEIGHT, spacing):
        if y < CENTER_Y - ROAD_WIDTH//2 or y > CENTER_Y + ROAD_WIDTH//2:
            TREE_INSTANCES.append((CENTER_X - ROAD_WIDTH//2 - TREE_SIZE - 10, y, random.choice(TREE_IMAGES)))
            TREE_INSTANCES.append((CENTER_X + ROAD_WIDTH//2 + 10, y, random.choice(TREE_IMAGES)))
    for x in range(0, WIDTH, spacing):
        if x < CENTER_X - ROAD_WIDTH//2 - buffer or x > CENTER_X + ROAD_WIDTH//2 + buffer:
            TREE_INSTANCES.append((x, CENTER_Y - ROAD_WIDTH//2 - TREE_SIZE - 10, random.choice(TREE_IMAGES)))
            TREE_INSTANCES.append((x, CENTER_Y + ROAD_WIDTH//2 + 10, random.choice(TREE_IMAGES)))

generate_tree_instances()

def trees():
    for x, y, tree in TREE_INSTANCES:
        screen.blit(tree, (x, y))

def crosswalk(x, y, length, horizontal=True, offset=0, margin=5):
    if horizontal:
        for i in range(0, length - 2*margin, Crosswalk_stip_width + Crosswalk_stip_gap):
            pygame.draw.rect(screen, Crosswalk_color, (x + margin + i, y + offset, Crosswalk_stip_width, Crosswalk_thickness))
    else:
        for i in range(0, length - 2*margin, Crosswalk_stip_width + Crosswalk_stip_gap):
            pygame.draw.rect(screen, Crosswalk_color, (x + offset, y + margin + i, Crosswalk_thickness, Crosswalk_stip_width))

def rain():
    for drop in raindrops:
        pygame.draw.line(screen, (173, 216, 230), (drop["x"], drop["y"]), (drop["x"] + 2, drop["y"] + 5), 1)
        drop["y"] += drop["speed"]
        if drop["y"] > HEIGHT:
            drop["y"] = -5
            drop["x"] = random.randint(0, WIDTH)

def lerp(a, b, t):
    return int(a + (b - a) * t)

def background_color(time_of_day):
    if 6 <= time_of_day < 18:
        if 6 <= time_of_day < 8:
            t = (time_of_day - 6) / 2
            return tuple(lerp(Night_Background[i], Day_Background[i], t) for i in range(3))
        elif 16 <= time_of_day < 18:  # Dusk
            t = (time_of_day - 16) / 2
            return tuple(lerp(Day_Background[i], Night_Background[i], t) for i in range(3))
        else:
            return Day_Background
    else:
        return Night_Background

def road_color(time_of_day):
    if 6 <= time_of_day < 18:
        if 6 <= time_of_day < 8:
            t = (time_of_day - 6) / 2
            return tuple(lerp(Night_road[i], Day_road[i], t) for i in range(3))
        elif 16 <= time_of_day < 18:
            t = (time_of_day - 16) / 2
            return tuple(lerp(Day_road[i], Night_road[i], t) for i in range(3))
        else:
            return Day_road
    else:
        return Night_road

def light_brightness(time_of_day):
    if 6 <= time_of_day < 18:
        if 6 <= time_of_day < 8:
            t = (time_of_day - 6) / 2
            return lerp(Night_light, Day_light, t)
        elif 16 <= time_of_day < 18:
            t = (time_of_day - 16) / 2
            return lerp(Day_light, Night_light, t)
        else:
            return Day_light
    else:
        return Night_light
    
def night_overlay_alpha(time_of_day):
    if 6 <= time_of_day < 8:
        t = (time_of_day - 6) / 2
        return int(100 * (1 - t))
    elif 16 <= time_of_day < 18:
        t = (time_of_day - 16) / 2
        return int(100 * t)
    elif 8 <= time_of_day < 16:
        return 0
    else:
        return 100

def roads_design():
    Background_Color = background_color(time_of_day)
    screen.fill(Background_Color)

    for x in range(0, WIDTH, Grass_Image.get_width()):
            for y in range(0, HEIGHT, Grass_Image.get_height()):
                screen.blit(Grass_Image, (x, y))

    intersection_rect = pygame.Rect(CENTER_X - ROAD_WIDTH // 2, CENTER_Y - ROAD_WIDTH // 2, ROAD_WIDTH, ROAD_WIDTH)

    # -------- A --------
    road_a_rect = pygame.Rect(CENTER_X - ROAD_WIDTH // 2, 0, ROAD_WIDTH, CENTER_Y - ROAD_WIDTH // 2)
    pygame.draw.rect(screen, Road_Color, road_a_rect)
    lane_end = road_a_rect.bottom - Lane_mark_offset
    pygame.draw.line(screen, Lane_Color, (road_a_rect.left + LANE_WIDTH, road_a_rect.top), (road_a_rect.left + LANE_WIDTH, lane_end), 2) 
    dashed_lane_line_vertical(road_a_rect.left + 2 * LANE_WIDTH, road_a_rect.top, lane_end)  
    pygame.draw.line(screen, Road_border_color, (road_a_rect.left, road_a_rect.top), (road_a_rect.left, road_a_rect.bottom), Road_border_width)
    pygame.draw.line(screen, Road_border_color, (road_a_rect.right - 1, road_a_rect.top), (road_a_rect.right - 1, road_a_rect.bottom), Road_border_width)

    # ------ B --------
    road_b_rect = pygame.Rect(CENTER_X - ROAD_WIDTH // 2, CENTER_Y + ROAD_WIDTH // 2, ROAD_WIDTH, HEIGHT - (CENTER_Y + ROAD_WIDTH // 2))
    pygame.draw.rect(screen, Road_Color, road_b_rect)
    lane_end = road_b_rect.top + Lane_mark_offset
    pygame.draw.line(screen, Lane_Color, (road_b_rect.left + 2 * LANE_WIDTH, lane_end), (road_b_rect.left + 2 * LANE_WIDTH, road_b_rect.bottom), 2)
    dashed_lane_line_vertical(road_b_rect.left + LANE_WIDTH, lane_end, road_b_rect.bottom)
    pygame.draw.line(screen, Road_border_color, (road_b_rect.left, road_b_rect.top), (road_b_rect.left, road_b_rect.bottom), Road_border_width)
    pygame.draw.line(screen, Road_border_color, (road_b_rect.right - 1, road_b_rect.top), (road_b_rect.right - 1, road_b_rect.bottom), Road_border_width)
    # -------- C --------
    road_c_rect = pygame.Rect(CENTER_X + ROAD_WIDTH // 2, CENTER_Y - ROAD_WIDTH // 2, WIDTH - (CENTER_X + ROAD_WIDTH // 2), ROAD_WIDTH)
    pygame.draw.rect(screen, Road_Color, road_c_rect)
    lane_end = road_c_rect.left + Lane_mark_offset
    dashed_lane_line_horizontal(lane_end, road_c_rect.right, road_c_rect.top + 2 * LANE_WIDTH)
    pygame.draw.line(screen, Lane_Color,(lane_end, road_c_rect.top + LANE_WIDTH), (road_c_rect.right, road_c_rect.top + LANE_WIDTH), 2)
    pygame.draw.line(screen, Road_border_color, (road_c_rect.left, road_c_rect.top), (road_c_rect.right, road_c_rect.top), Road_border_width)
    pygame.draw.line(screen, Road_border_color, (road_c_rect.left, road_c_rect.bottom - 1), (road_c_rect.right, road_c_rect.bottom - 1), Road_border_width)

    # -------- D --------
    road_d_rect = pygame.Rect(0, CENTER_Y - ROAD_WIDTH // 2, CENTER_X - ROAD_WIDTH // 2, ROAD_WIDTH)
    pygame.draw.rect(screen, Road_Color, road_d_rect)
    lane_end = road_d_rect.right - Lane_mark_offset
    dashed_lane_line_horizontal(road_d_rect.left, lane_end, road_d_rect.top + LANE_WIDTH)
    pygame.draw.line(screen, Lane_Color, (road_d_rect.left, road_d_rect.top + 2 * LANE_WIDTH), (lane_end, road_d_rect.top + 2 * LANE_WIDTH), 2)
    pygame.draw.line(screen, Road_border_color, (road_d_rect.left, road_d_rect.top), (road_d_rect.right, road_d_rect.top), Road_border_width)
    pygame.draw.line(screen, Road_border_color, (road_d_rect.left, road_d_rect.bottom - 1), (road_d_rect.right, road_d_rect.bottom - 1), Road_border_width)

    crosswalk(road_a_rect.left, road_a_rect.bottom - Crosswalk_thickness - Crosswalk_offset, road_a_rect.width, horizontal=True, margin=5)
    crosswalk(road_b_rect.left, road_b_rect.top + Crosswalk_offset, road_b_rect.width, horizontal=True, margin=5)
    crosswalk(road_c_rect.left + Crosswalk_offset, road_c_rect.top, road_c_rect.height, horizontal=False, margin=5)
    crosswalk(road_d_rect.right - Crosswalk_thickness - Crosswalk_offset, road_d_rect.top, road_d_rect.height, horizontal=False, margin=5)

    # - Centre box -
    pygame.draw.rect(screen, Intersection_Color, intersection_rect)

    MIDDLE_BOX_SIZE = 30  
    middle_rect = pygame.Rect( CENTER_X - MIDDLE_BOX_SIZE // 2, CENTER_Y - MIDDLE_BOX_SIZE // 2, MIDDLE_BOX_SIZE, MIDDLE_BOX_SIZE)
    circle_x = CENTER_X
    circle_y = CENTER_Y
    pygame.draw.circle(screen, Middle_Circle_Color, (circle_x, circle_y), Middle_Circle_Radius)
    pygame.draw.circle(screen, (0,0,0), (circle_x, circle_y), Middle_Circle_Radius -1, width= 1)
    pygame.draw.rect(screen, (53,57,53), middle_rect, border_radius=8)

    priority_triangles_al2()
    incoming_lane_arrows()
    middle_lane_arrows()
    left_turn_lane_arrows()
    screen.blit(LAKE_IMAGE, LAKE_POSITION)
    trees()

    alpha = night_overlay_alpha(time_of_day)
    if alpha > 0:
            night_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            night_overlay.fill((0, 0, 50, alpha))
            screen.blit(night_overlay, (0, 0))
        
def vehicle_design():
    for vehicles in moving_vehicles.values():
        for v in vehicles:
            img = v["sprite"]

            if v["direction"] == "down":
                img = pygame.transform.rotate(img, 180)
            elif v["direction"] == "right":
                img = pygame.transform.rotate(img, -90)
            elif v["direction"] == "left":
                img = pygame.transform.rotate(img, 90)

            rect = img.get_rect(center=(v["x"], v["y"]))
            screen.blit(img, rect)

def add_new_vehicles(active_lane):
    lanes_to_release = LEFT_TURNING_LANES + ([active_lane] if active_lane else [])
    current_time = pygame.time.get_ticks() / 1000

    for lane in lanes_to_release:
        queue = lane_queues[lane]
        lane_info = LANE_SCREEN_POSITION[lane]
        if queue and current_time - last_release_time[lane] >= Release_interval:
            vehicle = queue.popleft()
            if lane_info["direction"] in ["down", "up"]:
                x = lane_info["x"]  
                y = lane_info["y_start"] - Vehicle_Height // 2
            else:
                x = lane_info["x_start"] + Vehicle_Width // 2 
                y = lane_info["y"]  


            if moving_vehicles[lane]:
                last = moving_vehicles[lane][-1]
                d = lane_info["direction"]

                if d in ["down", "up"] and abs(last["y"] - y) < Vehicle_Height + Vehicle_Spacing:
                    continue
                if d in ["left", "right"] and abs(last["x"] - x) < Vehicle_Width + Vehicle_Spacing:
                    continue

            moving_vehicles[lane].append({"id": vehicle["id"], "intent": vehicle["intent"], "x": x, "y": y, "turned": False, "direction": LANE_SCREEN_POSITION[lane]["direction"], "passed_stop": False, "shifted": False, "sprite": random.choice(CAR_IMAGES)})
            last_release_time[lane] = current_time
            add_log(f"Vehicle {vehicle['id']} released on lane {lane}")

def move_vehicles(dt):
    for lane, vehicles in moving_vehicles.items():
        stop = Stop_line[LANE_SCREEN_POSITION[lane]["direction"]] 

        new_list = []

        for i, v in enumerate(vehicles):
            light = traffic_lights.get(lane, "RED")
            if lane in LANES_CONTROLLED and light == "RED" and not v["passed_stop"]:
                d = v["direction"]
                stop = Stop_line[LANE_SCREEN_POSITION[lane]["direction"]]
                if d == "down" and v["y"] + Vehicle_Speed * dt >= stop:
                    v["y"] = stop
                    new_list.append(v)
                    continue
                if d == "up" and v["y"] - Vehicle_Speed * dt <= stop:
                    v["y"] = stop
                    new_list.append(v)
                    continue
                if d == "right" and v["x"] + Vehicle_Speed * dt >= stop:
                    v["x"] = stop
                    new_list.append(v)
                    continue
                if d == "left" and v["x"] - Vehicle_Speed * dt <= stop:
                    v["x"] = stop
                    new_list.append(v)
                    continue

            if v["intent"] == "left" and not v.get("turned") and ready_to_turn_left(v, lane):
                if v["direction"] == "up":
                    v["direction"] = "left"
                elif v["direction"] == "down":
                    v["direction"] = "right"
                elif v["direction"] == "left":
                    v["direction"] = "down"
                elif v["direction"] == "right":
                    v["direction"] = "up"
                v["turned"] = True

            if v["intent"] == "right" and not v.get("turned") and ready_to_turn_right(v, lane):
                if v["direction"] == "up":
                    v["direction"] = "right"
                elif v["direction"] == "down":
                    v["direction"] = "left"
                elif v["direction"] == "left":
                    v["direction"] = "up"
                elif v["direction"] == "right":
                    v["direction"] = "down"
                v["turned"] = True


            if i > 0:
                v_ahead = vehicles[i-1]

                if not v.get("turned") and not v_ahead.get("turned"):
                    d = v["direction"]

                    if d in ["down", "up"]:
                        if abs(v["y"] - v_ahead["y"]) < Vehicle_Height + Vehicle_Spacing:
                            v["y"] = (
                                v_ahead["y"] - (Vehicle_Height + Vehicle_Spacing)
                                if d == "down"
                                else v_ahead["y"] + (Vehicle_Height + Vehicle_Spacing)
                            )
                    else:
                        if abs(v["x"] - v_ahead["x"]) < Vehicle_Width + Vehicle_Spacing:
                            v["x"] = (
                                v_ahead["x"] - (Vehicle_Width + Vehicle_Spacing)
                                if d == "right"
                                else v_ahead["x"] + (Vehicle_Width + Vehicle_Spacing)
                            )

            if (lane in MIDDLE_LANE_SHIFT and not v.get("shifted") and not v.get("turned")):
                lane_info = LANE_SCREEN_POSITION[lane]
                shift_amount = MIDDLE_LANE_SHIFT[lane]
                d = v["direction"]

                if d in ("down", "up"):
                    if d == "down" and v["y"] < Stop_line["down"] - Shift_start_offset:
                        pass
                    elif d == "up" and v["y"] > Stop_line["up"] + Shift_start_offset:
                        pass
                    else:
                        target = lane_info["x"] + shift_amount
                        remaining = target - v["x"]

                        if abs(remaining) < 0.5:
                            v["x"] = target
                            v["shifted"] = True
                        else:
                            v["x"] += max(-Shift_speed * dt, min(Shift_speed * dt, remaining))

                elif d in ("left", "right"):
                    if d == "right" and v["x"] < Stop_line["right"] - Shift_start_offset:
                        pass
                    elif d == "left" and v["x"] > Stop_line["left"] + Shift_start_offset:
                        pass
                    else:
                        target = lane_info["y"] + shift_amount
                        remaining = target - v["y"]

                        if abs(remaining) < 0.5:
                            v["y"] = target
                            v["shifted"] = True
                        else:
                            v["y"] += max(-Shift_speed * dt, min(Shift_speed * dt, remaining))



            d = v["direction"]
            if d == "down":
                v["y"] += Vehicle_Speed * dt
            elif d == "up":
                v["y"] -= Vehicle_Speed * dt
            elif d == "right":
                v["x"] += Vehicle_Speed * dt
            elif d == "left":
                v["x"] -= Vehicle_Speed * dt

            if not v["passed_stop"]:
                d = v["direction"]
                if d == "down" and v["y"] > Stop_line["down"] + 5:
                    v["passed_stop"] = True
                    add_log(f"Vehicle {v['id']} passed stop line on lane {lane}")
                elif d == "up" and v["y"] < Stop_line["up"] - 5:
                    v["passed_stop"] = True
                    add_log(f"Vehicle {v['id']} passed stop line on lane {lane}")
                elif d == "right" and v["x"] > Stop_line["right"] + 5:
                    v["passed_stop"] = True
                    add_log(f"Vehicle {v['id']} passed stop line on lane {lane}")
                elif d == "left" and v["x"] < Stop_line["left"] - 5:
                    v["passed_stop"] = True
                    add_log(f"Vehicle {v['id']} passed stop line on lane {lane}")
                
            BUFFER = 50
            if -BUFFER <= v["x"] <= WIDTH + BUFFER and -BUFFER <= v["y"] <= HEIGHT + BUFFER:
                new_list.append(v)

        moving_vehicles[lane] = new_list

def ready_to_turn_left(v, lane):
    d = v["direction"]

    if d == "down":
        return v["y"] >= CENTER_Y - Turn_offset
    if d == "up":
        return v["y"] <= CENTER_Y + Turn_offset
    if d == "right":
        return v["x"] >= CENTER_X - Turn_offset
    if d == "left":
        return v["x"] <= CENTER_X + Turn_offset
    return False

def ready_to_turn_right(v, lane):
    d = v["direction"]
    FAR_OFFSET = ROAD_WIDTH // 2 - 50  
    if d == "down":
        return v["y"] >= CENTER_Y + FAR_OFFSET
    if d == "up":
        return v["y"] <= CENTER_Y - FAR_OFFSET
    if d == "right":
        return v["x"] >= CENTER_X + FAR_OFFSET
    if d == "left":
        return v["x"] <= CENTER_X - FAR_OFFSET
    return False

def traffic_light_box(main_pos, right_pos):
    x_min = min(main_pos[0], right_pos[0]) - LIGHT_BOX_PADDING
    x_max = max(main_pos[0], right_pos[0]) + LIGHT_BOX_PADDING
    y_min = min(main_pos[1], right_pos[1]) - LIGHT_BOX_PADDING
    y_max = max(main_pos[1], right_pos[1]) + LIGHT_BOX_PADDING

    width = x_max - x_min
    height = y_max - y_min

    rect = pygame.Rect(x_min, y_min, width, height)
    pygame.draw.rect(screen, (50,50,50), rect, border_radius=8)

def right_turn_light(x, y, direction, color):
    size = 4
    w = 3

    if direction == "left":
        pygame.draw.line(screen, color, (x + size, y), (x - size, y), w)
        pygame.draw.polygon(screen, color, [
            (x - size - 4, y),
            (x - size, y - 4),
            (x - size, y + 4),
        ])

    elif direction == "right":
        pygame.draw.line(screen, color, (x - size, y), (x + size, y), w)
        pygame.draw.polygon(screen, color, [
            (x + size + 4, y),
            (x + size, y - 4),
            (x + size, y + 4),
        ])

    elif direction == "up":
        pygame.draw.line(screen, color, (x, y + size), (x, y - size), w)
        pygame.draw.polygon(screen, color, [
            (x, y - size - 4),
            (x - 4, y - size),
            (x + 4, y - size),
        ])

    elif direction == "down":
        pygame.draw.line(screen, color, (x, y - size), (x, y + size), w)
        pygame.draw.polygon(screen, color, [
            (x, y + size + 4),
            (x - 4, y + size),
            (x + 4, y + size),
        ])

def traffic_lights_design():
    for lane, pos in TRAFFIC_LIGHT_POSITION.items():
        state = traffic_lights.get(lane, "RED")

        if state == "GREEN":
            color = (0, 255, 0)
        elif state == "YELLOW":
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)

        cfg = RIGHT_TURN_ARROW_CONFIG.get(lane, {"dx": 0, "dy": 0, "dir": None})
        dx, dy = cfg["dx"], cfg["dy"]

        center_x = pos[0]
        center_y = pos[1]

        main_bulb_pos = (center_x - dx / 2, center_y - dy / 2)
        right_bulb_pos = (main_bulb_pos[0] + dx, main_bulb_pos[1] + dy)

        traffic_light_box(main_bulb_pos, right_bulb_pos)

        pygame.draw.circle(screen, color, main_bulb_pos, BULB_RADIUS)

        if cfg["dir"]:
            right_turn_light(right_bulb_pos[0], right_bulb_pos[1], cfg["dir"], color)


def main():
    running = True
    last_gen_time = pygame.time.get_ticks() / 1000
    GEN_INTERVAL = 3.0
    phase = "GREEN"
    current_active_lane = None
    last_active_lane = None
    active_lane = None
    light_start_time = pygame.time.get_ticks() / 1000
    green_duration = 0
    current_time = pygame.time.get_ticks() / 1000
    phase_end_time = current_time
    global time_of_day

    current_active_lane = select_lane(priority_lane_active())
    if current_active_lane:
        update_lights(current_active_lane)

        green_duration = green_light_duration(current_active_lane, moving_vehicles, Release_interval)
        active_lane = current_active_lane
        phase = "GREEN"
        phase_end_time = current_time + green_duration

    while running:
        current_time = pygame.time.get_ticks() / 1000
        if current_time - last_gen_time > GEN_INTERVAL:
            Generate_vehicle()
            last_gen_time = current_time
        time_of_day += time_speed
        if time_of_day >= 24:
            time_of_day = 0

        if current_time >= phase_end_time:
            if phase == "GREEN":
                for l in traffic_lights:
                    if l == current_active_lane:
                        traffic_lights[l] = "YELLOW"
                    else:
                        traffic_lights[l] = "RED"

                phase = "YELLOW"
                phase_end_time = current_time + YELLOW_DURATION

            elif phase == "YELLOW":
                for l in traffic_lights:
                    traffic_lights[l] = "RED"
                phase = "ALL_RED"
                phase_end_time = current_time + ALL_RED_DURATION

            elif phase == "ALL_RED":
                current_active_lane = select_lane(priority_lane_active())

                if current_active_lane:
                    update_lights(current_active_lane)

                    green_duration = green_light_duration(current_active_lane, moving_vehicles, Release_interval)

                    active_lane = current_active_lane
                    phase = "GREEN"
                    phase_end_time = current_time + green_duration

        if active_lane:
            add_new_vehicles(active_lane)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        dt = clock.tick(60) / 1000
        move_vehicles(dt)
        roads_design()
        sidebar()
        rain()
        lane_names()
        vehicle_design()
        traffic_lights_design()
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()