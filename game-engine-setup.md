# Game Engine Simulation Setup Guide

## System Overview
This is a game engine simulation system consisting of three main components:
1. A backend server that manages entity states and provides an interactive interface
2. A game engine that simulates entity movement and behavior
3. A startup script that coordinates the launching of these components

## Prerequisites
- Python 3.x installed
- Required Python packages (install via pip):
  ```bash
  pip install -r requirements.txt
  ```

## Directory Structure
```
.
├── code
│   ├── backend
│   │   └── backend.py
│   ├── gameengine
│   │   └── gameengine.py
│   └── start.py
├── docs
│   └── game-engine-api-docs.md
├── logs
│   └── simulation.log
└── requirements.txt
```

## Starting the Simulation

1. Run the start script:
   ```bash
   python code/start.py
   ```
   This will:
   - Create a logs directory if it doesn't exist
   - Delete any existing simulation.log file
   - Launch the game engine in a new terminal window
   - Start the backend server with an interactive interface in the current terminal

## Using the Backend Interface

The backend provides an interactive menu with the following options:

1. Wake - Wake up an entity
2. Sleep - Put an entity to sleep
3. Move to - Move an entity to specific coordinates
4. Teleport - Instantly teleport an entity
5. Walk - Make an entity walk to coordinates
6. Run - Make an entity run to coordinates
7. Display current state - Show the current state of all entities
8. View log file - Display the contents of simulation.log
9. Exit - Shut down the simulation

For movement commands (3-6):
1. Select the command number
2. Choose an entity from the displayed list
3. Enter the target coordinates (x, y, z)

## Game Engine Features

The game engine simulates:
- Entity movement with walking and running speeds
- Sleep/wake cycles for entities
- Real-time position updates
- Collision detection
- Event logging

## Initial World Configuration

The simulation starts with:
- One Victorian Mansion (house_001)
- One General Store (store_001)
- Two NPCs:
  - John Walker (person_001)
  - Sarah Chen (person_002)

## Communication Protocol

- Backend Server: Runs on port 8000
- Game Engine: Runs on port 8001
- Communication happens via HTTP/REST with JSON payloads
- All events and state changes are logged to simulation.log

## Monitoring and Debugging

1. View real-time updates in the game engine terminal window
2. Check the simulation log:
   ```bash
   tail -f logs/simulation.log
   ```
3. Use option 7 in the backend interface to view current entity states
4. Use option 8 to view the complete log file

## Shutting Down

1. Select option 9 in the backend interface
2. The backend will send a shutdown signal to the game engine
3. Both components will terminate gracefully

## Error Handling

- If ports 8000 or 8001 are in use, the system will retry with delays
- Communication errors between components are automatically retried
- All errors are logged to simulation.log
- The game engine will attempt to reconnect to the backend if connection is lost

## Best Practices

1. Always use the backend interface to modify entity states
2. Monitor the simulation.log for errors and unexpected behavior
3. Use the display current state option to verify changes
4. Shut down properly using the exit option rather than force-quitting

## Common Issues and Solutions

1. If ports are already in use:
   - Check for running instances
   - Kill any existing Python processes using the ports
   - Restart the simulation

2. If components aren't communicating:
   - Check the simulation.log for errors
   - Verify both terminals are still running
   - Restart the simulation if necessary

3. If entities aren't moving:
   - Verify the target coordinates are reachable
   - Check the simulation.log for movement updates
   - Ensure the entity isn't in a sleep state
