# API Documentation

## Overview

This document describes the API for complex-skill.

## Endpoints

### GET /status
Returns the current status of the system.

### POST /execute
Executes a command with given parameters.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action | string | Yes | The action to execute |
| options | object | No | Additional options |

## Example

```json
{
  "action": "process",
  "options": {
    "mode": "fast"
  }
}
```