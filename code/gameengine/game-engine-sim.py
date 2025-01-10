# game_engine_simulator.py
from fastapi import FastAPI, HTTPException
import uvicorn
import httpx
from datetime import datetime
from typing import Dict, Optional

app = FastAPI()
BACKEND_URL = "http://127.0.0.1:8000"

async def send_to_backend(endpoint: str, data: Dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BACKEND_URL}/{endpoint}", json=data)
        return response.json()

@app.post("/initialize-world")
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
            },
            {
                "id": "house_002",
                "name": "Cottage",
                "location": {"x": 150.0, "y": 0.0, "z": 150.0},
                "properties": {"style": "cottage", "rooms": 2}
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
                "name": "John Doe",
                "sex": "male",
                "location": {"x": 110.0, "y": 0.0, "z": 110.0},
                "properties": {"age": 30}
            }
        ],
        "metadata": {
            "time_of_day": "morning",
            "weather": "sunny"
        }
    }
    return await send_to_backend("area-config", config)

@app.post("/simulate-movement")
async def simulate_movement(entity_id: str, command_type: str, 
                          x: float, y: float, z: float,
                          speed: Optional[float] = None):
    """Simulates movement commands (walk, run, teleport)"""
    command = {
        "command": command_type,
        "entity_id": entity_id,
        "destination": {"x": x, "y": y, "z": z}
    }
    if speed is not None:
        command["speed"] = speed
    
    return await send_to_backend("command", command)

@app.post("/simulate-look")
async def simulate_look(entity_id: str, x: float, y: float, z: float):
    """Simulates look command"""
    command = {
        "command": "look",
        "entity_id": entity_id,
        "direction": {"x": x, "y": y, "z": z}
    }
    return await send_to_backend("command", command)

@app.post("/simulate-event")
async def simulate_event(event_type: str, entity_id: str, target_data: Dict):
    """Simulates sending an event to the backend"""
    event = {
        "event": event_type,
        "entity_id": entity_id,
        "target": target_data,
        "timestamp": datetime.now().isoformat()
    }
    return await send_to_backend("event", event)

@app.get("/check-distance")
async def check_distance(entity_id: str, target_name: str):
    """Simulates distance check command"""
    command = {
        "command": "distance_to",
        "entity_id": entity_id,
        "target_name": target_name
    }
    return await send_to_backend("command", command)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
