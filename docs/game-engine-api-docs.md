# Game Engine - Python Backend API Interface Documentation

## Overview
This document details the API interface between a game engine and its Python backend. The backend provides real-time responses to game engine requests and handles various game commands and events.

## Server Details
- Backend server runs first and listens for incoming connections
- Default port: [PORT_NUMBER]
- Protocol: HTTP/REST
- Data format: JSON

## Initial Area Configuration
When the game engine starts, it sends an area configuration to the backend.

### Area Configuration Format
```json
{
  "timestamp": "2024-01-09T12:00:00Z",
  "area_id": "string",
  "houses": [
    {
      "id": "string",
      "name": "string",
      "location": {
        "x": float,
        "y": float,
        "z": float
      },
      "properties": {
        // Extensible properties object
      }
    }
  ],
  "stores": [
    {
      "id": "string",
      "name": "string",
      "type": "string",
      "location": {
        "x": float,
        "y": float,
        "z": float
      },
      "properties": {
        // Extensible properties object
      }
    }
  ],
  "people": [
    {
      "id": "string",
      "name": "string",
      "sex": "male|female|other",
      "location": {
        "x": float,
        "y": float,
        "z": float
      },
      "properties": {
        // Extensible properties object
      }
    }
  ],
  "metadata": {
    // Extensible metadata object for future additions
  }
}
```

## Commands (Game Engine to Backend)

### Movement Commands
```json
{
  "command": "teleport",
  "entity_id": "string",
  "target": {
    "x": float,
    "y": float,
    "z": float
  }
}
```

```json
{
  "command": "walk|run",
  "entity_id": "string",
  "destination": {
    "x": float,
    "y": float,
    "z": float
  },
  "speed": float  // Optional, default values per command type
}
```

### Interaction Commands
```json
{
  "command": "look",
  "entity_id": "string",
  "direction": {
    "x": float,
    "y": float,
    "z": float
  }
}
```

```json
{
  "command": "sleep|wake",
  "entity_id": "string",
  "duration": float  // Optional, for sleep command
}
```

### Query Commands
```json
{
  "command": "distance_to",
  "entity_id": "string",
  "target_name": "string"
}
```

## Events (Game Engine to Backend)

### Perception Events
```json
{
  "event": "saw",
  "entity_id": "string",
  "target": {
    "id": "string",
    "type": "person|house|store",
    "distance": float,
    "location": {
      "x": float,
      "y": float,
      "z": float
    }
  },
  "timestamp": "ISO-8601 timestamp"
}
```

## Response Format (Backend to Game Engine)
All responses follow this structure:
```json
{
  "status": "success|error",
  "command_id": "string",  // Echo of the original command
  "data": {
    // Command-specific response data
  },
  "error": {
    "code": "string",
    "message": "string"
  }
}
```

### Example Response for distance_to
```json
{
  "status": "success",
  "command_id": "distance_to",
  "data": {
    "distance": float,
    "target_name": "string",
    "target_location": {
      "x": float,
      "y": float,
      "z": float
    }
  }
}
```

## Error Codes
- `400`: Invalid request format
- `404`: Entity/target not found
- `422`: Invalid command parameters
- `500`: Internal server error

## Best Practices
1. All coordinates use the same coordinate system throughout
2. All IDs should be unique within their respective types
3. Timestamps should be in ISO-8601 format
4. Include optional properties in the properties object rather than at root level
5. All floating-point values should use consistent precision

## Extensibility
The API supports extensibility through:
1. The properties object in each entity type
2. The metadata object in the area configuration
3. Additional command types
4. Additional event types

To add new features:
1. Add new properties to existing objects using the properties field
2. Document new commands or events following the existing format
3. Maintain backward compatibility when adding new fields
