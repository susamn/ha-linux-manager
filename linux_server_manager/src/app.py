import json
import os
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .ssh_manager import ServerManager
import logging

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")

# Load configuration
CONFIG_PATH = "/data/options.json"
if not os.path.exists(CONFIG_PATH):
    # Fallback for local testing
    CONFIG_PATH = os.path.join(os.getcwd(), "options.json")
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump({"servers": []}, f)

with open(CONFIG_PATH) as f:
    config = json.load(f)

servers = [
    ServerManager(**s) for s in config.get("servers", [])
]

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Detect the ingress path from the request headers if available
    ingress_path = request.headers.get("X-Ingress-Path", "")
    
    server_data = []
    for s in servers:
        status = await s.get_status()
        server_data.append({
            "name": s.name,
            "host": s.host,
            "status": status,
            "is_busy": s.is_busy,
            "plug": s.plug_entity
        })
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "servers": server_data,
        "ingress_path": ingress_path
    })

@app.post("/turn_on/{server_name}")
async def turn_on(server_name: str):
    server = next((s for s in servers if s.name == server_name), None)
    if server:
        success = await server.turn_on()
        return {"success": success}
    return {"success": False, "error": "Server not found"}

@app.post("/turn_off/{server_name}")
async def turn_off(server_name: str, background_tasks: BackgroundTasks):
    server = next((s for s in servers if s.name == server_name), None)
    if server:
        if server.is_busy:
            return {"success": False, "error": "Already processing"}
        # Run shutdown in background since it takes time
        background_tasks.add_task(server.turn_off)
        return {"success": True, "message": "Shutdown sequence initiated"}
    return {"success": False, "error": "Server not found"}

@app.get("/api/status")
async def get_status():
    server_data = []
    for s in servers:
        status = await s.get_status()
        server_data.append({
            "name": s.name,
            "status": status,
            "is_busy": s.is_busy
        })
    return server_data
