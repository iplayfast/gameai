# backend_server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Union, Any
import uvicorn
from datetime import datetime

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

app = FastAPI()
area_config = None

@app.post("/area-config")
async def receive_area_config(config: AreaConfig):
    global area_config
    area_config = config
    print(f"Received area config for: {config.area_id}")
    return {"status": "success", "message": "Area configuration received"}

@app.post("/command")
async def receive_command(command: Command):
    if area_config is None:
        raise HTTPException(status_code=400, detail="No area configuration loaded")
    
    print(f"Processing command: {command.command} for entity: {command.entity_id}")
    
    response = {
        "status": "success",
        "command_id": command.command,
        "data": {}
    }

    if command.command == "distance_to":
        # Simulate distance calculation
        response["data"] = {
            "distance": 42.0,
            "target_name": command.target_name,
            "target_location": {"x": 100.0, "y": 0.0, "z": 100.0}
        }
    elif command.command in ["teleport", "walk", "run"]:
        response["data"] = {
            "status": "moving",
            "destination": command.destination or command.target
        }
    elif command.command in ["sleep", "wake"]:
        response["data"] = {
            "status": command.command + "ing"
        }
    elif command.command == "look":
        response["data"] = {
            "visible_objects": [
                {"type": "house", "id": "house_001", "distance": 10.0},
                {"type": "store", "id": "store_001", "distance": 15.0}
            ]
        }
    
    return response

@app.post("/event")
async def receive_event(event: Event):
    print(f"Received event: {event.event} from entity: {event.entity_id}")
    return {"status": "success", "message": "Event received"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
