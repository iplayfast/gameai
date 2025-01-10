# code/gameengine/gameengine.py
from fastapi import FastAPI, HTTPException, Request
import uvicorn
import httpx
import asyncio
from datetime import datetime
import random
from typing import Dict, Optional, List
import logging
import time
from pathlib import Path
import math
import os
import sys
from contextlib import contextmanager
import json
from typing import Optional
from starlette.responses import JSONResponse
import threading
import signal

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent.parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)
shutdown_event = asyncio.Event()
running = True
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'simulation.log'),
    ]
)
logger = logging.getLogger('GameEngine')
# Add these utility functions after the imports and before the FastAPI app definition:

def is_port_in_use(port: int) -> bool:
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return False
        except socket.error:
            return True

def find_available_port(start_port: int, max_attempts: int = 10) -> int:
    """Find an available port starting from start_port"""
    port = start_port
    for _ in range(max_attempts):
        if not is_port_in_use(port):
            return port
        port += 1
    raise RuntimeError(f"Could not find an available port after {max_attempts} attempts")

# Also make sure socket is imported at the top:
import socket

# The rest of the game engine code remains the same...
app = FastAPI()
BACKEND_URL = "http://127.0.0.1:8000"
GAME_ENGINE_PORT = 8001
MAX_RETRIES = 5
RETRY_DELAY = 2  # seconds
MOVEMENT_UPDATE_INTERVAL = 0.5  # seconds
DISPLAY_UPDATE_INTERVAL = 0.2  # seconds
WALK_SPEED = 2.0  # units per second
RUN_SPEED = 5.0  # units per second

class EntityState:
    def __init__(self, entity_id: str, name: str, initial_location: Dict):
        self.entity_id = entity_id
        self.name = name
        self.current_location = initial_location.copy()
        self.target_location = None
        self.is_moving = False
        self.movement_speed = 0
        self.is_sleeping = False
        self.wake_time = None
        self.last_update = time.time()
        self.movement_type = None  # "walk" or "run"

    def set_movement_target(self, target: Dict, command_type: str):
        self.target_location = target
        self.is_moving = True
        self.movement_type = command_type
        self.movement_speed = RUN_SPEED if command_type == "run" else WALK_SPEED

    def get_distance_to_target(self) -> Optional[float]:
        if not self.target_location:
            return None
        dx = self.target_location["x"] - self.current_location["x"]
        dy = self.target_location["y"] - self.current_location["y"]
        dz = self.target_location["z"] - self.current_location["z"]
        return math.sqrt(dx*dx + dy*dy + dz*dz)

    def update_position(self):
        if not self.is_moving or not self.target_location:
            return False

        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time

        # Calculate distance to move this update
        distance_to_move = self.movement_speed * dt

        # Calculate direction vector
        dx = self.target_location["x"] - self.current_location["x"]
        dy = self.target_location["y"] - self.current_location["y"]
        dz = self.target_location["z"] - self.current_location["z"]
        
        total_distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if total_distance <= distance_to_move:
            # We've arrived at the target
            self.current_location = self.target_location.copy()
            self.is_moving = False
            self.target_location = None
            self.movement_type = None
            return True
        
        # Move partially toward target
        move_fraction = distance_to_move / total_distance
        self.current_location["x"] += dx * move_fraction
        self.current_location["y"] += dy * move_fraction
        self.current_location["z"] += dz * move_fraction
        return True

    def sleep(self, duration: Optional[float] = None):
        self.is_sleeping = True
        if duration:
            self.wake_time = time.time() + duration
        else:
            self.wake_time = None

    def wake(self):
        self.is_sleeping = False
        self.wake_time = None

    def update_sleep_state(self):
        if self.is_sleeping and self.wake_time and time.time() >= self.wake_time:
            self.wake()
            return True
        return False

    def get_sleep_time_remaining(self) -> Optional[float]:
        if self.is_sleeping and self.wake_time:
            remaining = self.wake_time - time.time()
            return max(0, remaining)
        return None

class GameState:
    def __init__(self):
        self.entities: Dict[str, EntityState] = {}
        self.houses: List[Dict] = []
        self.stores: List[Dict] = []
        self.last_command: Optional[Dict] = None
        self.last_command_time: Optional[float] = None

    def add_entity(self, entity_id: str, name: str, location: Dict):
        self.entities[entity_id] = EntityState(entity_id, name, location)

    def get_entity(self, entity_id: str) -> Optional[EntityState]:
        return self.entities.get(entity_id)

    def record_command(self, command: Dict):
        self.last_command = command
        self.last_command_time = time.time()

class Display:
    def __init__(self):
        self.last_update = 0
        self.error_message = None
        self.error_time = None

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def format_location(self, loc: Dict) -> str:
        return f"({loc['x']:.1f}, {loc['y']:.1f}, {loc['z']:.1f})"

    def set_error(self, message: str):
        self.error_message = message
        self.error_time = time.time()

    def should_clear_error(self) -> bool:
        if self.error_time and time.time() - self.error_time > 5:
            self.error_message = None
            self.error_time = None
            return True
        return False

    def update(self, game_state: GameState):
        current_time = time.time()
        if current_time - self.last_update < DISPLAY_UPDATE_INTERVAL:
            return
        self.last_update = current_time

        self.clear_screen()
        print("=== Game Engine State ===\n")

        # Show last command if recent
        if game_state.last_command and current_time - game_state.last_command_time < 5:
            print("Last Command:")
            print(f"  {game_state.last_command}")
            print()

        # Show error message if exists
        if self.error_message:
            print("Error:")
            print(f"  {self.error_message}")
            print()
            self.should_clear_error()

        print("Entities:")
        for entity_id, entity in game_state.entities.items():
            status = []
            if entity.is_sleeping:
                remaining = entity.get_sleep_time_remaining()
                if remaining:
                    status.append(f"sleeping for {remaining:.1f}s")
                else:
                    status.append("sleeping")
            if entity.is_moving:
                distance = entity.get_distance_to_target()
                status.append(f"{entity.movement_type}ing - {distance:.1f} units to target")
            
            status_str = f" ({', '.join(status)})" if status else ""
            
            print(f"\n{entity.name} ({entity_id}):{status_str}")
            print(f"  Location: {self.format_location(entity.current_location)}")
            if entity.target_location:
                print(f"  Target: {self.format_location(entity.target_location)}")

        print("\nStatic Objects:")
        for house in game_state.houses:
            print(f"\n{house['name']} ({house['id']})")
            print(f"  Location: {self.format_location(house['location'])}")
        
        for store in game_state.stores:
            print(f"\n{store['name']} ({store['id']})")
            print(f"  Location: {self.format_location(store['location'])}")

# Initialize global state
game_state = GameState()
display = Display()

async def send_to_backend(endpoint: str, data: Dict, retries=MAX_RETRIES):
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BACKEND_URL}/{endpoint}", 
                    json=data, 
                    timeout=5.0
                )
                logger.info(f"Sent to backend ({endpoint}): {data}")
                return response.json()
        except Exception as e:
            if attempt < retries - 1:
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {RETRY_DELAY} seconds...")
                await asyncio.sleep(RETRY_DELAY)
            else:
                logger.error(f"All {retries} attempts failed: {e}")
                display.set_error(f"Failed to communicate with backend: {e}")
                raise

async def initialize_world():
    """Sends initial area configuration to backend"""
    config = {
        "timestamp": datetime.now().isoformat(),
        "area_id": "test_area",
        "houses": [
            {
                "id": "house_001",
                "name": "Victorian Mansion",
                "location": {"x": 100.0, "y": 0.0, "z": 100.0},
                "properties": {"style": "victorian", "rooms": 4}
            }
        ],
        "stores": [
            {
                "id": "store_001",
                "name": "General Store",
                "type": "retail",
                "location": {"x": 120.0, "y": 0.0, "z": 120.0},
                "properties": {"size": "medium"}
            }
        ],
        "people": [
            {
                "id": "person_001",
                "name": "John Walker",
                "sex": "male",
                "location": {"x": 100.0, "y": 0.0, "z": 100.0},
                "properties": {"age": 30},
                "state": "sleeping"
            },
            {
                "id": "person_002",
                "name": "Sarah Chen",
                "sex": "female",
                "location": {"x": 150.0, "y": 0.0, "z": 150.0},
                "properties": {"age": 25},
                "state": "sleeping"
            }
        ],
        "metadata": {
            "time_of_day": "morning",
            "weather": "sunny"
        }
    }
    
    # Store initial configuration in game state
    game_state.houses = config["houses"]
    game_state.stores = config["stores"]
    for person in config["people"]:
        game_state.add_entity(person["id"], person["name"], person["location"])
    
    # Keep trying to connect to backend
    while True:
        try:
            await send_to_backend("area-config", config)
            logger.info("Initial world configuration sent successfully")
            return True
        except Exception as e:
            logger.warning(f"Failed to send initial configuration: {e}")
            display.set_error(f"Waiting for backend to start...")
            await asyncio.sleep(2)
            continue

async def handle_command(command: Dict):
    """Process a command and update entity state"""
    game_state.record_command(command)
    entity_id = command["entity_id"]
    entity = game_state.get_entity(entity_id)
    
    if not entity:
        error_msg = f"Entity not found: {entity_id}"
        logger.error(error_msg)
        display.set_error(error_msg)
        return
    
    try:
        if command["command"] in ["walk", "run"]:
            # Ensure we have a destination
            if "destination" not in command:
                raise ValueError(f"{command['command']} command requires destination")
                
            # Update entity movement state
            entity.set_movement_target(command["destination"], command["command"])
            logger.info(f"Entity {entity_id} starting {command['command']} to {command['destination']}")
        
        elif command["command"] == "teleport":
            # Use either target or destination
            location = command.get("target") or command.get("destination")
            if not location:
                raise ValueError("Teleport command requires target location")
                
            # Update entity position immediately
            entity.current_location = location.copy()
            entity.is_moving = False
            entity.target_location = None
            logger.info(f"Entity {entity_id} teleported to {location}")
        
        elif command["command"] == "sleep":
            duration = command.get("duration")
            entity.sleep(duration)
            logger.info(f"Entity {entity_id} going to sleep" + 
                    (f" for {duration} seconds" if duration else ""))
        
        elif command["command"] == "wake":
            entity.wake()
            logger.info(f"Entity {entity_id} waking up")
        
        else:
            logger.warning(f"Unknown command type: {command['command']}")
            raise ValueError(f"Unknown command type: {command['command']}")

    except Exception as e:
        error_msg = f"Error processing command {command['command']}: {str(e)}"
        logger.error(error_msg)
        display.set_error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/shutdown")
async def shutdown():
    """Endpoint to trigger game engine shutdown"""
    global running
    logger.info("Received shutdown command from backend")
    print("Shutdown command received - initiating shutdown...")
    running = False
    shutdown_event.set()
    # Force exit after a brief delay
    asyncio.create_task(force_shutdown())
    return JSONResponse({"status": "success", "message": "Shutdown initiated"})

async def force_shutdown():
    """Force exit after a brief delay"""
    await asyncio.sleep(2)
    logger.info("Forcing shutdown...")
    sys.exit(0)

@app.post("/command")
async def receive_command(request: Request):
    """Endpoint to receive commands from the backend"""
    try:
        command_data = await request.json()
        logger.info(f"Received command from backend: {command_data}")
        
        # Validate required fields
        if not all(k in command_data for k in ["command", "entity_id"]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Format the command to match what handle_command expects
        formatted_command = {
            "command": command_data["command"],
            "entity_id": command_data["entity_id"]
        }
        
        # Handle different types of location data
        if "destination" in command_data:
            formatted_command["destination"] = command_data["destination"]
        if "target" in command_data:
            formatted_command["target"] = command_data["target"]
        
        # Add optional fields if present
        for field in ["direction", "target_name", "speed", "duration"]:
            if field in command_data:
                formatted_command[field] = command_data[field]
                
        # Process the command
        await handle_command(formatted_command)
        
        # Get updated state for response
        entity = game_state.get_entity(command_data["entity_id"])
        if entity:
            response_data = {
                "status": "success",
                "message": "Command processed",
                "entity_state": {
                    "location": entity.current_location,
                    "is_moving": entity.is_moving,
                    "is_sleeping": entity.is_sleeping,
                    "movement_type": entity.movement_type
                }
            }
        else:
            response_data = {
                "status": "success",
                "message": "Command processed"
            }
            
        return response_data
    
    except Exception as e:
        logger.error(f"Error processing command: {e}")
        display.set_error(f"Error processing command: {e}")
        raise HTTPException(status_code=400, detail=str(e))

async def update_entity_states():
    """Updates all entity states and sends updates to backend"""
    while True:
        try:
            for entity_id, entity in game_state.entities.items():
                # Update movement
                if entity.update_position():
                    await send_to_backend("command", {
                        "command": "move_to",
                        "entity_id": entity_id,
                        "destination": entity.current_location
                    })
                
                # Update sleep state
                if entity.update_sleep_state():
                    await send_to_backend("event", {
                        "event": "woke_up",
                        "entity_id": entity_id,
                        "target": {},
                        "timestamp": datetime.now().isoformat()
                    })
            
            await asyncio.sleep(MOVEMENT_UPDATE_INTERVAL)
        except Exception as e:
            logger.error(f"Error in entity state updates: {e}")
            display.set_error(f"Error updating entities: {e}")
            await asyncio.sleep(1)

async def update_display():
    """Updates the terminal display"""
    while True:
        try:
            display.update(game_state)
            await asyncio.sleep(DISPLAY_UPDATE_INTERVAL)
        except Exception as e:
            logger.error(f"Error updating display: {e}")
            await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    await initialize_world()
    asyncio.create_task(update_entity_states())
    asyncio.create_task(update_display())

def run_server(app, host: str, port: int):
    config = uvicorn.Config(app, host=host, port=port, log_config=None)
    server = uvicorn.Server(config)
    server.install_signal_handlers = lambda: None
    
    return server.serve()

async def shutdown_server():
    """Wait for shutdown signal and stop the server"""
    await shutdown_event.wait()
    logger.info("Shutting down game engine...")
    global running
    running = False

if __name__ == "__main__":
    print("Starting Game Engine Simulator...")
    print(f"All logs will be written to: {log_dir / 'simulation.log'}")
    
    while running:
        try:
            if is_port_in_use(GAME_ENGINE_PORT):
                print(f"\nError: Port {GAME_ENGINE_PORT} is already in use!")
                print("Please ensure no other game engine instances are running.")
                print("\nRetrying in 5 seconds...")
                time.sleep(5)
                continue
            
            print(f"Game Engine running on port {GAME_ENGINE_PORT}")
            
            # Run uvicorn with modified config
            config = uvicorn.Config(
                app, 
                host="127.0.0.1", 
                port=GAME_ENGINE_PORT,
                log_config=None,
                loop="asyncio"
            )
            server = uvicorn.Server(config)
            server.install_signal_handlers = lambda: None
            
            # Run server in a separate task so we can monitor shutdown_event
            async def serve():
                await server.serve()
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run both the server and shutdown monitor
            loop.run_until_complete(asyncio.gather(
                serve(),
                shutdown_server()
            ))
            
            break
            
        except Exception as e:
            logger.error(f"Server crashed: {e}")
            display.set_error(f"Server crashed: {e}")
            print(f"\nError: Server crashed: {e}")
            if running:
                print("Restarting in 5 seconds...")
                time.sleep(5)
                continue
            else:
                break

    print("Game Engine shutdown complete.")