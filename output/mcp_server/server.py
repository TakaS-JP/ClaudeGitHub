"""Auto-generated MCP server (converted from ChatGPT GPT Actions)."""
from __future__ import annotations

import json
import httpx
from mcp.server.fastmcp import FastMCP

BASE_URL = "https://api.example.com/v1"

mcp = FastMCP("gpt-actions")

@mcp.tool()
def listTasks(status: str = "") -> str:
    """List all tasks"""
    params = {k: v for k, v in {"status": status}.items() if v}
    resp = httpx.get(f"{BASE_URL}/tasks", params=params)
    resp.raise_for_status()
    return resp.text

@mcp.tool()
def createTask(title: str = "", due_date: str = "") -> str:
    """Create a new task"""
    params = {}
    body = {k: v for k, v in {"title": title, "due_date": due_date}.items() if v}
    resp = httpx.post(f"{BASE_URL}/tasks", params=params, json=body)
    resp.raise_for_status()
    return resp.text

@mcp.tool()
def updateTask(task_id: str = "", status: str = "") -> str:
    """Update an existing task"""
    params = {}
    body = {k: v for k, v in {"status": status}.items() if v}
    resp = httpx.patch(f"{BASE_URL}/tasks/{task_id}", params=params, json=body)
    resp.raise_for_status()
    return resp.text

@mcp.tool()
def deleteTask(task_id: str = "") -> str:
    """Delete a task"""
    params = {}
    resp = httpx.delete(f"{BASE_URL}/tasks/{task_id}", params=params)
    resp.raise_for_status()
    return resp.text


if __name__ == "__main__":
    mcp.run()