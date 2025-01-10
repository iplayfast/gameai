# code/backend/backend.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Union, Any
import uvicorn
import asyncio
import threading
from datetime import datetime
import sys
import time
import logging
import os
from pathlib import Path
import httpx

GAME_ENGINE_URL = "http://127.0.0.1:8001"  

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent.parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'simulation.log'),
    ]
)
logger = logging.getLogger('Backend')

# Configure uvicorn logging
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.handlers = [logging.FileHandler(log_dir / 'simulation.log')]

# Configure uvicorn access logging
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.handlers = [logging.FileHandler(log_dir / 'simulation.log')]

# Configure uvicorn error logging
uvicorn_error_logger = logging.getLogger("uvicorn.error")
uvicorn_error_logger.handlers = [logging.FileHandler(log_dir / 'simulation.log')]

class Location(BaseModel):
    x: float
    y: float
    z: float

class House(BaseModel):
    id: str
    name: str
    location: Location
    properties: Dict[str, Any]

class Store(BaseModel):
    id: str
    name: str
    type: str
    location: Location
    properties: Dict[str, Any]

class Person(BaseModel):
    id: str
    name: str
    sex: str
    location: Location
    properties: Dict[str, Any]

class AreaConfig(BaseModel):
    timestamp: str
    area_id: str
    houses: List[House]
    stores: List[Store]
    people: Optional[List[Person]]
    metadata: Dict[str, Any]

class Command(BaseModel):
    command: str
    entity_id: str
    target: Optional[Location] = None
    destination: Optional[Location] = None
    direction: Optional[Location] = None
    target_name: Optional[str] = None
    speed: Optional[float] = None
    duration: Optional[float] = None

class Event(BaseModel):
    event: str
    entity_id: str
    target: Dict[str, Any]
    timestamp: str

class InteractiveBackend:
    def __init__(self):
        self.app = FastAPI()
        self.area_config = None
        self.entities = {}
        
        # Register routes
        self.app.post("/area-config")(self.receive_area_config)
        self.app.post("/command")(self.receive_command)
        self.app.post("/event")(self.receive_event)

    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    async def receive_area_config(self, config: AreaConfig):
        """Receive and store area configuration from game engine"""
        self.area_config = config
        # Initialize entities dictionary
        for house in config.houses:
            self.entities[house.id] = {"type": "house", "data": house}
        for store in config.stores:
            self.entities[store.id] = {"type": "store", "data": store}
        if config.people:
            for person in config.people:
                self.entities[person.id] = {"type": "person", "data": person}
        
        logger.info(f"Received area config for: {config.area_id}")
        return {"status": "success", "message": "Area configuration received"}

    async def receive_command(self, command: Command):
        """Receive command updates from game engine"""
        logger.info(f"Received command: {command.command} for entity: {command.entity_id}")
        if command.entity_id in self.entities:
            if command.destination:
                self.entities[command.entity_id]["data"].location = command.destination
                logger.info(f"Updated {command.entity_id} location to {command.destination}")
        return {"status": "success", "command": command.command}

    async def receive_event(self, event: Event):
        """Receive events from game engine"""
        logger.info(f"Received event: {event.event} from entity: {event.entity_id}")
        return {"status": "success", "message": "Event received"}

    async def send_to_game_engine(self, command_data: Dict) -> Dict:
        """Send command to game engine with retry logic"""
        MAX_RETRIES = 3
        RETRY_DELAY = 1.0

        for attempt in range(MAX_RETRIES):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{GAME_ENGINE_URL}/command",
                        json=command_data,
                        timeout=5.0
                    )
                    logger.info(f"Sent command to game engine: {command_data}")
                    return response.json()
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Failed to send command to game engine: {e}")
                    raise

    async def send_shutdown_to_game_engine(self):
        """Send shutdown command to game engine"""
        try:
            async with httpx.AsyncClient() as client:
                print("Sending shutdown command to game engine...")
                logger.info(f"Sending shutdown command to game engine at {GAME_ENGINE_URL}")
                response = await client.post(
                    f"{GAME_ENGINE_URL}/shutdown",
                    timeout=5.0
                )
                print(f"Game engine response: {response.json()}")
                logger.info("Sent shutdown command to game engine")
                await asyncio.sleep(2)  # Give the game engine time to shut down
                return response.json()
        except Exception as e:
            logger.error(f"Failed to send shutdown to game engine: {e}")
            print(f"\nWarning: Could not send shutdown to game engine: {e}")
            return None

    def run_interface(self):
        """Run the interactive command interface"""
        while True:
            try:
                print("\n=== Backend Control Interface ===")
                print("Actions:")
                print("1. Wake")
                print("2. Sleep")
                print("3. Move to")
                print("4. Teleport")
                print("5. Walk")
                print("6. Run")
                print("7. Display current state")
                print("8. View log file")
                print("9. Exit")
                
                choice = input("\nSelect action (1-9): ").strip()
                
                if choice == "9":
                    print("Shutting down game engine...")
                    asyncio.run(self.send_shutdown_to_game_engine())
                    print("Exiting interface...")
                    break
                    
                if choice == "8":
                    log_path = log_dir / 'simulation.log'
                    if sys.platform == 'win32':
                        os.system(f'type "{log_path}"')
                    else:
                        os.system(f'cat "{log_path}"')
                    input("\nPress Enter to continue...")
                    continue

                if choice == "7":
                    print("\nCurrent State:")
                    for entity_id, data in self.entities.items():
                        entity = data["data"]
                        if hasattr(entity, 'location'):
                            print(f"{entity_id} ({data['type']}): "
                                  f"location=({entity.location.x}, {entity.location.y}, {entity.location.z})")
                    continue

                if not self.entities:
                    print("\nNo entities available. Wait for game engine to send area configuration.")
                    continue

                print("\nAvailable entities:")
                entities = [f"{entity_id} ({data['type']})" 
                          for entity_id, data in self.entities.items()]
                for idx, entity in enumerate(entities, 1):
                    print(f"{idx}. {entity}")
                
                try:
                    entity_idx = int(input("\nSelect entity number: ")) - 1
                    if entity_idx < 0 or entity_idx >= len(entities):
                        print("Invalid entity selection")
                        continue
                    
                    entity_id = list(self.entities.keys())[entity_idx]
        
                    # Replace the command construction section in run_interface:
                    if choice in ["3", "4", "5", "6"]:
                        try:
                            x = float(input("Enter x coordinate: "))
                            y = float(input("Enter y coordinate: "))
                            z = float(input("Enter z coordinate: "))
                            
                            command_types = {
                                "3": "walk",
                                "4": "teleport",
                                "5": "walk",
                                "6": "run"
                            }
                            
                            location_data = {"x": x, "y": y, "z": z}
                            command_data = {
                                "command": command_types[choice],
                                "entity_id": entity_id
                            }
                            
                            # Use "target" for teleport, "destination" for walk/run
                            if choice == "4":  # teleport
                                command_data["target"] = location_data
                            else:  # walk/run
                                command_data["destination"] = location_data
                            
                            asyncio.run(self.send_to_game_engine(command_data))
                            print(f"\nSent {command_types[choice]} command for {entity_id} to ({x}, {y}, {z})")
                            
                        except ValueError:
                            print("Invalid coordinate values")
                            continue

                    elif choice in ["1", "2"]:
                        command_data = {
                            "command": "wake" if choice == "1" else "sleep",
                            "entity_id": entity_id
                        }
                        asyncio.run(self.send_to_game_engine(command_data))
                        print(f"\nSent {'wake' if choice == '1' else 'sleep'} command for {entity_id}")

                except ValueError:
                    print("Invalid input")
                    continue

            except Exception as e:
                logger.error(f"Error in interface: {e}")
                print(f"Error: {e}")
                continue

    def run_server(self):
        """Run the FastAPI server"""
        try:
            config = uvicorn.Config(
                app=self.app,
                host="127.0.0.1",
                port=8000,
                log_config={
                    "version": 1,
                    "disable_existing_loggers": False,
                    "formatters": {
                        "default": {
                            "()": "uvicorn.logging.DefaultFormatter",
                            "fmt": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                            "use_colors": False,
                        },
                    },
                    "handlers": {
                        "default": {
                            "formatter": "default",
                            "class": "logging.FileHandler",
                            "filename": str(log_dir / "simulation.log"),
                        },
                    },
                    "loggers": {
                        "uvicorn": {"handlers": ["default"], "level": "INFO"},
                        "uvicorn.error": {"handlers": ["default"], "level": "INFO"},
                        "uvicorn.access": {"handlers": ["default"], "level": "INFO"},
                    },
                },
            )
            server = uvicorn.Server(config)
            server.run()
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise

if __name__ == "__main__":
    try:
        # Clear the screen at startup
        os.system('cls' if os.name == 'nt' else 'clear')
        
        backend = InteractiveBackend()
        
        # Run FastAPI server in a separate thread
        server_thread = threading.Thread(target=backend.run_server, daemon=True)
        server_thread.start()
        
        # Give the server a moment to start
        time.sleep(1)
        
        # Clear screen again before showing interface
        backend.clear_screen()
        
        # Run interactive interface in main thread
        backend.run_interface()
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Startup error: {e}")
        sys.exit(1)