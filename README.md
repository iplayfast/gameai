# Game AI Simulation Environment

This project implements a simulation environment consisting of a game engine and backend server that communicate via REST APIs. The system simulates entities (people, houses, stores) in a 3D space with various interaction capabilities.

## System Architecture

The system consists of three main components:

1. **Game Engine** (Port 8001)
   - Maintains the simulation state
   - Handles entity movement and actions
   - Provides real-time visualization
   - Processes commands from the backend

2. **Backend Server** (Port 8000)
   - Provides an interactive control interface
   - Manages communication with the game engine
   - Handles state synchronization
   - Logs all events and commands

3. **Start Script**
   - Manages the startup sequence
   - Launches components in the correct order
   - Handles process management

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

## Prerequisites

- Python 3.8 or higher
- Virtual environment tool (venv recommended)
- Operating System: Linux, macOS, or Windows

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd game-ai-simulation
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Linux/macOS:
   source venv/bin/activate
   # On Windows:
   .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Simulation

1. Start the simulation using the start script:
   ```bash
   python code/start.py
   ```
   This will:
   - Launch the game engine in a new terminal window
   - Start the backend server with an interactive interface

2. The backend interface provides the following commands:
   - Wake: Wake up an entity
   - Sleep: Put an entity to sleep
   - Walk: Make an entity walk to coordinates
   - Run: Make an entity run to coordinates
   - Teleport: Instantly move an entity to coordinates
   - Display current state: Show all entity positions
   - View log file: Display the simulation log
   - Exit: Shut down all components

## Command Examples

1. Moving an entity:
   - Select "Walk" (5) from the menu
   - Choose an entity from the list
   - Enter target coordinates (x, y, z)

2. Viewing entity states:
   - Select "Display current state" (7) from the menu
   - This shows all entities and their current positions

3. Checking logs:
   - Select "View log file" (8) from the menu
   - Press Enter to return to the interface

## API Documentation

Detailed API documentation can be found in `docs/game-engine-api-docs.md`. This includes:
- Command formats
- Event types
- Response structures
- Error codes

## Logging

All system events are logged to `logs/simulation.log`, including:
- Command processing
- Entity state changes
- Server events
- Errors and warnings

## Troubleshooting

1. If the game engine fails to start:
   - Check if port 8001 is already in use
   - Look for error messages in the log file
   - Ensure Python environment is properly set up

2. If commands aren't working:
   - Verify both servers are running
   - Check the log file for error messages
   - Ensure coordinates are valid numbers

3. If the display isn't updating:
   - The game engine window should show real-time entity states
   - If not visible, try restarting the simulation

## Shutdown

To properly shut down the simulation:
1. Select "Exit" (9) from the backend interface
2. This will automatically shut down the game engine
3. Close any remaining terminal windows

## Development Notes

- The game engine uses FastAPI for the REST interface
- Entity states update at 0.5-second intervals
- Movement speeds: Walk = 2.0 units/sec, Run = 5.0 units/sec
- All coordinates use a 3D space (x, y, z)

## Contributing

When adding new features:
1. Follow the existing code structure
2. Update API documentation
3. Add appropriate logging
4. Test all changes with the interactive interface
