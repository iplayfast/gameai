# test_simulation.py
import asyncio
import httpx
import time
from typing import Dict

async def test_backend_communication():
    async with httpx.AsyncClient() as client:
        base_url = "http://127.0.0.1:8001"
        
        print("Testing simulation...")
        
        # Initialize world
        print("\n1. Initializing world...")
        response = await client.post(f"{base_url}/initialize-world")
        print(f"Response: {response.json()}")
        
        # Test movement
        print("\n2. Testing movement simulation...")
        response = await client.post(
            f"{base_url}/simulate-movement",
            params={
                "entity_id": "person_001",
                "command_type": "walk",
                "x": 125.0,
                "y": 0.0,
                "z": 125.0,
                "speed": 1.0
            }
        )
        print(f"Response: {response.json()}")
        
        # Test looking
        print("\n3. Testing look simulation...")
        response = await client.post(
            f"{base_url}/simulate-look",
            params={
                "entity_id": "person_001",
                "x": 1.0,
                "y": 0.0,
                "z": 0.0
            }
        )
        print(f"Response: {response.json()}")
        
        # Test distance check
        print("\n4. Testing distance check...")
        response = await client.get(
            f"{base_url}/check-distance",
            params={
                "entity_id": "person_001",
                "target_name": "house_001"
            }
        )
        print(f"Response: {response.json()}")
        
        # Test event simulation
        print("\n5. Testing event simulation...")
        response = await client.post(
            f"{base_url}/simulate-event",
            json={
                "event_type": "saw",
                "entity_id": "person_001",
                "target_data": {
                    "id": "house_001",
                    "type": "house",
                    "distance": 10.0
                }
            }
        )
        print(f"Response: {response.json()}")

if __name__ == "__main__":
    asyncio.run(test_backend_communication())
