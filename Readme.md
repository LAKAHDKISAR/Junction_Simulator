# Traffic Junction Simulation

## Overview

This system simulates an intelligent traffic management system for a four-way intersection. It dynamically controls traffic lights based on real-time queue lengths, implements priority lane logic based on academic traffic management principles, ensures fair distribution of green light time across all lanes, and provides a rich visual simulation with animated vehicles, traffic lights, and road markings.

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
- Environmental Elements: Trees and lake scenery around the intersection
- Traffic Log Sidebar: Real-time event logging (vehicle releases, stop line crossings)
- Smooth Vehicle Movement: Physics-based vehicle spacing and collision avoidance

## System Architecture

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

## File Structure

.
├── traffic_management.py  
├── traffic_generator.py  
├── simulator.py  
├── visual_simulation.py  
└── asset/  
 ├── Ambulance.png  
 ├── Audi.png  
 ├── Black_viper.png  
 ├── Car.png  
 ├── Mini_truck.png  
 ├── Mini_van.png  
 ├── Police.png  
 ├── taxi.png  
 ├── truck.png  
 ├── RE_01.png  
 ├── RE_02.png  
 └── Lake.png

## Usage Guide

- Running the Console Simulation
  python simulator.py

- Running the Visual Simulation
  python visual_simulation.py

## Requirements

- Python 3.6+
- pygame>=2.0.0

* Install dependencies:
  bash
  pip install pygame

## Performance Notes

- Visual simulation runs at 60 FPS
- Vehicle generation occurs every 3 seconds
- Traffic light updates happen based on calculated green duration

## Limitations

- Currently there is no collision detection and control implemented, there might be vehicles that appear to collide.
- Currently there are only 2 traffic light phases and the indicator traffic light for right turn is yet to be implemented.

## License

This project is licensed under the MIT License.
