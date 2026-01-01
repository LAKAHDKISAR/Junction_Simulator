# Traffic Junction Simulation

## Overview

This system simulates an intelligent traffic management system for a four-way intersection. It dynamically controls traffic lights based on real-time queue lengths, implements priority lane logic based on traffic management theory inspired by academic models, ensures fair distribution of green light time across all lanes, and provides a rich visual simulation with animated vehicles, traffic lights, and road markings.

## Objective

- My main objective for this project was to gain hands-on experience in implementing complex systems while deepening my understanding of concepts such as data structures, algorithm design, and time complexity analysis.
- By simulating a traffic junction, I aimed to learn how to efficiently manage dynamic queues, prioritize tasks, and optimize system performance in real-time scenarios. The project also provided an opportunity to apply these concepts in Python and Pygame, reinforcing practical skills in both logic implementation and performance-aware software development.

## Table of Contents

- [Overview](#Overview)
- [Objective](#Objective)
- [Features](#Features)
- [System_Architecture](#System_Architecture)
- [Simulation_Demo](#Simulation_Demo)
- [Data_Structures_Used](#Data_Structures_Used)
- [Data_Structure_and_Function_Use](#Data_Structure_and_Function_Use)
- [Algorithm](#Algorithm)
- [Time_Complexity](#Time_Complexity)
- [Usage_Guide](#Usage_Guide)
- [Requirements](#Requirements)
- [Performance_Notes](#Performance_Notes)
- [Assets_Acknowledgements](#Assets_Acknowledgements)
- [Technical_References](#Technical_References)
- [License](#License)

## Features

Core Traffic Management :

- Dynamic Traffic Generation: Randomly generates vehicles with different intents (straight, left turn, right turn)
- Priority Lane System: Activates priority mode when a specific lane exceeds a threshold
- Average-Based Fair Scheduling: Distributes vehicles based on average queue length across normal lanes
- Adaptive Green Light Duration: Calculates optimal green light duration based on vehicle count
- Multi-Lane Support: Manages 12 lanes across 4 directions (A, B, C, D)
- Free Left Turn Lanes: Dedicated left-turn lanes that are always green

Visual Simulation (Pygame) :

- Real-time Vehicle Animation: Vehicles with various sprites (ambulance, police, taxi, trucks, etc.)
- Traffic Light Visualization: Color-coded traffic lights at each intersection
- Lane Indicators: Arrow markings showing permitted directions for each lane
- Straight arrows for incoming lanes
- Combined straight + right arrows for middle lanes
- Left turn arrows for third lanes
- Priority Lane Marking: Golden triangle markers on priority lane (AL2)
- Environmental Elements: Precipitation, trees and lake and other scenery around the intersection
- Day/Night Transition: Smooth visual changes to simulate different times of day
- Traffic Log Sidebar: Real-time event logging (vehicle releases, stop line crossings)
- Smooth Vehicle Movement: Physics-based vehicle spacing and collision avoidance

## System_Architecture

Traffic Management Theory
The system implements a mathematical model for fair traffic distribution:

- Normal Lane Operation
  All lanes operate as normal lanes until explicitly declared as priority. Vehicles are served based on the average waiting vehicles across all normal lanes.
  Vehicle Distribution Formula:
  |V| = (1/n) × Σ|Li|

Where:

- n: Total number of normal lanes (3 lanes: BL2, CL2, DL2)
- |Li|: Total number of vehicles waiting on ith lane
- |V|: Total number of vehicles to be served from active lane

* Green Light Duration Formula:
  T_green = |V| × t

Where:

- T_green: Total green light duration
- |V|: Number of vehicles to be served
- t: Estimated time per vehicle (randomly: 0.5, 1.0, 1.2, or 1.5 seconds)

* Priority Lane Operation

Lane AL2 is designated as the priority lane with special handling:

Activation: When queue length > 10 vehicles
Deactivation: When queue length < 5 vehicles
Special Case: With fewer than 5 vehicles, AL2 operates as a normal lane
Immediate Service: Priority lane is served immediately after current green cycle ends

- Lane Configuration

Road Structure (4 Roads × 3 Lanes = 12 Total Lanes)
Each road (A, B, C, D) has three distinct lanes:

Lane 1 (Incoming Lanes)

- Lanes: AL1, BL1, CL1, DL1
- Purpose: Incoming traffic feeder lanes
- Control: Not directly controlled by traffic lights
- Arrow Indicator: Straight arrow pointing in opposite direction

Lane 2 (Controlled Outgoing Lanes)

- Lanes: AL2, BL2, CL2, DL2
- Purpose: Main traffic lanes with signal control
- Control: Must obey RED/GREEN light conditions
- Special: AL2 is the priority lane
- Arrow Indicator: Combined straight + right turn arrow
- Behavior: Vehicles shift laterally to align with incoming lanes before intersection

Lane 3 (Free Left Turn Lanes)

- Lanes: AL3, BL3, CL3, DL3
- Purpose: Dedicated left-turn only lanes
- Control: Always GREEN (free flow)
- Arrow Indicator: Left turn arrow

Priority Lane Specification

- Default Priority Lane: AL2 (top road, middle lane)
- Visual Marker: Golden triangles on approach
- Activation Threshold: 10 vehicles
- Deactivation Threshold: 5 vehicles
- Behavior: Interrupts round-distribution when activated

## Simulation_Demo

[![Demo Video](https://img.shields.io/badge/Watch_Demo-Click_Here-red?style=for-the-badge&logo=play)](https://github.com/user-attachments/assets/06cb5f90-962b-404e-9b4c-40b3f54e7b54)

## Data_Structures_Used

| **Data Structure Type**  | **Program Elements Using It**                                                                                                                                        | **Implementation**           | **Why This Data Structure Is Used**                                                                                                                                 |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Queue**                | lane_queues                                                                                                                                                          | dict[str, collections.deque] | Since vehicles must leave lanes in first-come-first-served order and deque allows O(1) append() and popleft(), which is ideal for traffic queues.                   |
| **List**                 | INCOMING_LANES, LANES_CONTROLLED, LEFT_TURNING_LANES, LANE_ORDER, CAR_IMAGES, TREE_IMAGES, TREE_INSTANCES, raindrops, log_messages, vehicles_to_move                 | Python list                  | Lists preserve order and allow easy iteration. They have been used anywhere ordering matters such as in lane rotation, sprite selection, drawing, logs, animations. |
| **Dictionary**           | traffic_lights, moving_vehicles, last_release_time, LANE_SCREEN_POSITION, TRAFFIC_LIGHT_POSITION, RIGHT_TURN_ARROW_CONFIG, Stop_line, MIDDLE_LANE_SHIFT, CENTER_ZONE | dict[key → value]            | They provide fast O(1) lookup by lane name or direction and it is ideal for mapping lanes to states, positions, timing, and configuration data.                     |
| **List of Dictionaries** | Vehicle objects inside moving_vehicles, raindrops                                                                                                                    | list[dict]                   | Since they act as lightweight objects without defining classes, each dict stores dynamic attributes like position, direction, speed, intent, and sprite.            |
| **Tuple**                | Tree positions, traffic light coordinates, fixed (x, y) values                                                                                                       | (x, y) tuples                | Since coordinates should not be able change accidentally, Tuples which are immutable, lightweight, and safe for fixed positions, have been used.                    |
| **Set**                  | all_lanes, derived lane groups                                                                                                                                       | set([...])                   | Used when only membership checking is required since they are faster than lists for lookup.                                                                         |
| **Numeric Types**        | last_gen_time, light_start_time, time_of_day, GEN_INTERVAL, Vehicle_Speed, counters                                                                                  | int, float                   | They have been used for time tracking, animation interpolation, spacing logic, and statistics.                                                                      |
| **Pygame Rect**          | Roads, intersection box, light boxes, collision regions                                                                                                              | pygame.Rect(x, y, w, h)      | They have been used for efficient handling of screen areas, collision logic, and drawing boundaries using Pygame’s optimized structure.                             |
| **Pygame Surface**       | CAR_IMAGES, TREE_IMAGES, Grass_Image, LAKE_IMAGE, rain_surface, night_overlay                                                                                        | pygame.Surface               | They represents drawable image buffers and have been used to enable sprite rendering, background tiling, and visual effects.                                        |
| **State Variables**      | phase, active_lane                                                                                                                                                   | str                          | Simple readable control of system state (traffic phases and active lane) without complex structures.                                                                |

## Data_Structure_and_Function_Use

| **Data Structure**       | **Functions They Are Used In**                                                                                                                                                                    |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Queue**                | Generate_vehicle(), add_new_vehicles(active_lane), select_lane(), priority_lane_active()                                                                                                          |
| **List**                 | Generate_vehicle(), add_new_vehicles(active_lane), vehicle_design(), incoming_lane_arrows(), middle_lane_arrows(), left_turn_lane_arrows(), generate_tree_instances(), trees(), rain(), sidebar() |
| **Dictionary**           | move_vehicles(dt), add_new_vehicles(active_lane), update_lights(), traffic_lights_design(), ready_to_turn_left(), ready_to_turn_right(), green_light_duration(), select_lane()                    |
| **List of Dictionaries** | move_vehicles(dt), add_new_vehicles(active_lane), vehicle_design(), rain()                                                                                                                        |
| **Tuple**                | generate_tree_instances(), trees(), traffic_lights_design()                                                                                                                                       |
| **Set**                  | select_lane(), priority_lane_active()                                                                                                                                                             |
| **Numeric Types**        | move_vehicles(dt), rain(), green_light_duration(), main()                                                                                                                                         |
| **Pygame Rect**          | roads_design(), traffic_lights_design(), vehicle_design()                                                                                                                                         |
| **Pygame Surface**       | vehicle_design(), trees(), rain(), roads_design()                                                                                                                                                 |
| **State Variables**      | main(), update_lights(), add_new_vehicles(active_lane)                                                                                                                                            |

## Algorithm

Loop every frame:

    1. Generate vehicles
        - For each normal/control lane (LANES_CONTROLLED):
            - If number of vehicles in queue < 10:
                - Randomly generate 0–2 new vehicles
                - Assign "straight" (90%) or "right" (10%) intent
                - Append to lane queue
        - For each left-turn lane (LEFT_TURNING_LANES):
            - If number of vehicles in queue < 5 and random chance < 0.2:
                - Generate 1 vehicle with "left" intent
                - Append to lane queue

    2. Update simulation time
        - time_of_day += time_speed
        - Wrap around 24 hours if needed

    3. Check current traffic light phase
        a) GREEN phase ends → switch to YELLOW
        b) YELLOW phase ends → switch to ALL_RED
        c) ALL_RED phase ends → lane selection & green duration:
            i) Check priority lane (AL2):
                - If number of waiting vehicles ≥ threshold (>=5):
                    - Serve priority lane next
                - Else:
                    - Serve next normal lane in a round manner
            ii) Update traffic lights for selected lane
            iii) Calculate green duration:
                    |V| = sum of vehicles in served lanes / number of served lanes
                    T_green = |V| * t

    4. Release vehicles from active lane(s)
        - For each lane allowed to move:
            - Check spacing from last vehicle
            - Place vehicle at starting position
            - Mark time of release

    5. Move all vehicles
        - For each moving vehicle in each lane:
            1. If lane is controlled by traffic light and light is red:
                  - Straight or right-turn vehicles stop at the stop line
                  - Left-turn vehicles proceed without stopping since they are free lanes
            2. Execute left or right turn if vehicle reaches the turn point
            3. Perform lane shift to enter the road form their incoming lane
            4. Move vehicle along its direction based on speed and time delta
            5. Update passed_stop flag when vehicle crosses stop line
            6. Remove vehicle if it leaves the screen bounds

    6. Render simulation
        1. Draw roads, intersections, crosswalks
        2. Draw Sidebar
        3. Draw rain
        3. Draw lane names
        2. Draw vehicles with correct orientation for each lane
        3. Draw traffic lights
        4. Apply day/night overlay

    7. Update display
        - pygame.display.flip()

    8. Repeat next frame

## Time_Complexity

### 1. Vehicle Generation

- for lane in `LANES_CONTROLLED`:

  - if `len(lane_queues[lane]) < 10`:
    - for i in range(`num_vehicles`):
      - `lane_queues[lane].append(vehicle)`

- for lane in `LEFT_TURNING_LANES`:

  - if `len(lane_queues[lane]) < 5`:
    - `lane_queues[lane].append(vehicle)`

- Let L1 = number of normal/control lanes (LANES_CONTROLLED)
- Let L2 = number of left-turn lanes (LEFT_TURNING_LANES)
- Maximum number of vehicles generated per lane per frame is 2 (normal) or 1 (left-turn).

- **Time complexity** :

  1. For normal lanes: O(L1 × max_new_vehicles) : O(L1)
  2. For left-turn lanes: O(L2 × max_new_vehicles) : O(L2)

- Thus, **Combined**: O(L1 + L2) : O(L), where L = Total lanes

### 2. Updating_Simulation_Time

- `time_of_day += time_speed`
- Thus, **Time complexity**: O(1) (constant-time operation)

### 3. Traffic Light Phase Check & Lane Selection

- Checking if phase ended : O(1)
- Priority lane check: Count vehicles in AL2 : O(Vp), where Vp = number of vehicles in AL2
- Normal lanes for round manner: Sum vehicles in other lanes : O(Vn), Vn = total vehicles in normal lanes
- Updating lights : O(L), where L = total lanes

- Thus, **Time complexity**: O(Vp + Vn + L)

### 4. Releasing Vehicles

- for lane in `lanes_to_release`:

  - if `current_time - last_release_time[lane] >= Release_interval`:
    - `vehicle = queue.popleft()`
    - `moving_vehicles[lane].append(vehicle)`

- Maximum one vehicle per lane per frame is released
- Accessing queue and appending : O(1)
- For all lanes allowed to move : O(L)

- Thus, **Time complexity**: O(L)

### 5. Move Vehicles

- For each moving vehicle in each lane:

  1. If lane is controlled by traffic light and light is red:
     - Straight or right-turn vehicles stop at the stop line
     - Left-turn vehicles proceed without stopping (free lanes)
  2. Execute left or right turn if vehicle reaches the turn point
  3. Perform lane shift to enter the road from their incoming lane
  4. Move vehicle along its direction based on speed and time delta
  5. Update passed_stop flag when vehicle crosses stop line
  6. Remove vehicle if it leaves the screen bounds

- **Time complexity**:

  - Let V = total number of moving vehicles in all lanes
  - Check light & stop line : O(1) per vehicle
  - Check ready to turn left/right : O(1) per vehicle
  - Lane shift : O(1)
  - Update position : O(1)
  - Remove if out of bounds : O(1)
  - Spacing check with vehicle ahead : O(1)

- Per lane : O(number of vehicles in lane)
- Across all lanes : O(V)

### 6. Render Simulation

1.  `roads_design()`
2.  `sidebar()`
3.  `rain()`
4.  `lane_names()`
5.  `vehicle_design()`
6.  `traffic_lights_design()`
7.  `pygame.display.flip()`

- Road rendering: Draw background + lanes + intersections : O(WIDTH × HEIGHT / tile_size) : constant per frame (tile_size fixed)
- Sidebar : O(1)
- Rain drops : O(R), where R = number of raindrops
- Lane names : O(L), where L = number of lanes
- Vehicles rendering : O(V), where V = vehicles
- Traffic lights : O(L)

- Thus, **Time complexity**: O(V + L + R + constant_for_roads) : O(V + R)

### 7. Main Loop

- All the steps above happen once per frame
- Let F = number of frames simulated
- Total time complexity for F frames: O(F⋅(V+L+R))

- Where:

  1. V = number of moving vehicles (dynamic, depends on queue & release rate)
  2. L = number of lanes (small, constant in practice)
  3. R = number of raindrops

- Simplified per frame complexity : O(V + R) (dominated by vehicle movement and rendering)
- Thus, **Time Complexity**: O(F⋅(V+L+R))

## Usage_Guide

- Running the Console Simulation:
  python simulator.py

- Running the Visual Simulation:
  python visual_simulation.py

## Requirements

- Python 3.6+
- pygame>=2.0.0

* Install dependencies:
  `bash`
  `pip install pygame`

## Performance_Notes

- Visual simulation runs at 60 FPS
- Vehicle generation occurs every 3 seconds
- Traffic light updates happen based on calculated green duration

## Assets_Acknowledgements

- https://opengameart.org/content/free-top-down-car-sprites-by-unlucky-studio
- https://opengameart.org/content/grass-1
- https://opengameart.org/

## Technical_References

- Python official documentation: https://docs.python.org/3/
- Pygame documentation: https://www.pygame.org/docs/
- Time Complexity & Data Structure References:
- https://www.geeksforgeeks.org/dsa/understanding-time-complexity-simple-examples/
- https://www.mygreatlearning.com/blog/why-is-time-complexity-essential/

## License

This project is licensed under the MIT License.
