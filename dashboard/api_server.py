# Copyright (c) 2026 AI Center Plus. All Rights Reserved.
# This software is proprietary and confidential. See LICENSE file.
# Unauthorized copying, distribution, or modification is strictly prohibited.

"""
APEX Dashboard - FastAPI Web Server
Real-time web dashboard for monitoring and controlling APEX.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


def create_app(apex_organism) -> FastAPI:
    """Create the FastAPI application with APEX integration."""

    app = FastAPI(
        title="APEX Organism Dashboard",
        description="Real-time monitoring and control of the APEX digital organism.",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ─── REST API Endpoints ────────────────────────────────────────

    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Serve the main dashboard HTML."""
        return get_dashboard_html()

    @app.get("/api/status")
    async def get_status():
        """Get APEX organism status."""
        return JSONResponse(apex_organism.get_status())

    @app.get("/api/capabilities")
    async def get_capabilities():
        """List all learned capabilities."""
        caps = apex_organism.capabilities
        return JSONResponse({
            "count": len(caps),
            "capabilities": list(caps.keys()),
        })

    @app.get("/api/knowledge")
    async def get_knowledge(topic: str = ""):
        """Search the knowledge base."""
        results = await apex_organism.oracle.get_knowledge(topic)
        return JSONResponse({"results": results})

    @app.get("/api/spending")
    async def get_spending():
        """Get spending report."""
        return JSONResponse(apex_organism.money_gate.get_spending_report())

    @app.post("/api/command")
    async def execute_command(body: Dict[str, Any]):
        """Execute a natural language command."""
        command = body.get("command", "")
        if not command:
            return JSONResponse({"error": "No command provided"}, status_code=400)

        # Route through MCP client
        result = await apex_organism.mcp_client.query(command)
        return JSONResponse({"command": command, "result": result})

    @app.post("/api/search")
    async def search(body: Dict[str, Any]):
        """Research a topic."""
        query = body.get("query", "")
        result = await apex_organism.search(query)
        return JSONResponse({"query": query, "result": result})

    @app.post("/api/learn")
    async def learn(body: Dict[str, Any]):
        """Learn a new capability."""
        topic = body.get("topic", "")
        await apex_organism.learn(topic)
        return JSONResponse({"topic": topic, "status": "learned"})

    @app.post("/api/swarm")
    async def deploy_swarm(body: Dict[str, Any]):
        """Deploy a swarm of agents."""
        num_agents = body.get("agents", 5)
        task = body.get("task", "")
        results = await apex_organism.deploy_swarm(num_agents, task)
        return JSONResponse({
            "agents": num_agents,
            "task": task,
            "results_count": len(results),
        })

    # ─── WebSocket for Real-time Updates ────────────────────────────

    connected_clients = set()

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        connected_clients.add(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                # Process real-time commands
                try:
                    msg = json.loads(data)
                    if msg.get("type") == "command":
                        result = await apex_organism.mcp_client.query(
                            msg.get("content", "")
                        )
                        await websocket.send_json({
                            "type": "response",
                            "content": result,
                            "timestamp": datetime.now().isoformat(),
                        })
                    elif msg.get("type") == "status":
                        await websocket.send_json({
                            "type": "status",
                            "content": apex_organism.get_status(),
                        })
                except json.JSONDecodeError:
                    await websocket.send_json({
                        "type": "error",
                        "content": "Invalid JSON",
                    })
        except WebSocketDisconnect:
            connected_clients.discard(websocket)

    return app


def get_dashboard_html() -> str:
    """Return the full dashboard HTML."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APEX Organism Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: #0a0a0a;
            color: #00ff88;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #0a1a0a, #001a00);
            border-bottom: 2px solid #00ff88;
            padding: 20px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            font-size: 28px;
            text-shadow: 0 0 20px #00ff88;
        }
        .header .version {
            color: #00aa55;
            font-size: 14px;
        }
        .pulse {
            width: 12px; height: 12px;
            background: #00ff88;
            border-radius: 50%;
            animation: pulse 1.4s infinite;
            display: inline-block;
            margin-right: 8px;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; box-shadow: 0 0 10px #00ff88; }
            50% { opacity: 0.3; box-shadow: 0 0 2px #00ff88; }
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            padding: 20px;
        }
        .card {
            background: #111;
            border: 1px solid #00ff8844;
            border-radius: 8px;
            padding: 20px;
        }
        .card h2 {
            font-size: 16px;
            color: #00ff88;
            margin-bottom: 15px;
            border-bottom: 1px solid #00ff8833;
            padding-bottom: 8px;
        }
        .stat {
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            border-bottom: 1px solid #0a0a0a;
        }
        .stat-label { color: #888; }
        .stat-value { color: #00ff88; font-weight: bold; }
        .terminal {
            grid-column: 1 / -1;
            background: #0a0a0a;
            border: 1px solid #00ff8844;
            border-radius: 8px;
            padding: 20px;
        }
        .terminal h2 {
            font-size: 16px;
            color: #00ff88;
            margin-bottom: 15px;
        }
        #output {
            background: #000;
            border: 1px solid #333;
            border-radius: 4px;
            padding: 15px;
            height: 300px;
            overflow-y: auto;
            margin-bottom: 15px;
            font-size: 14px;
            line-height: 1.6;
        }
        .output-line { margin: 2px 0; }
        .output-user { color: #00aaff; }
        .output-apex { color: #00ff88; }
        .output-error { color: #ff4444; }
        .output-info { color: #888; }
        .input-row {
            display: flex;
            gap: 10px;
        }
        #commandInput {
            flex: 1;
            background: #111;
            border: 1px solid #00ff8844;
            color: #00ff88;
            padding: 12px 15px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        #commandInput:focus { outline: none; border-color: #00ff88; }
        .btn {
            background: #00ff88;
            color: #000;
            border: none;
            padding: 12px 25px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            font-family: 'Courier New', monospace;
        }
        .btn:hover { background: #00cc66; }
        .organ {
            display: flex;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #1a1a1a;
        }
        .organ-dot {
            width: 8px; height: 8px;
            border-radius: 50%;
            margin-right: 10px;
        }
        .organ-dot.active { background: #00ff88; }
        .organ-dot.inactive { background: #444; }
        .organ-name { flex: 1; }
        .organ-role { color: #666; font-size: 12px; }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #222;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 8px;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff88, #00aaff);
            border-radius: 4px;
            transition: width 0.5s;
        }
        @media (max-width: 768px) {
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1><span class="pulse"></span> APEX ORGANISM</h1>
            <span class="version" id="versionLabel">v0.1.0 | Loading...</span>
        </div>
        <div>
            <button class="btn" onclick="refreshStatus()">REFRESH</button>
        </div>
    </div>

    <div class="grid">
        <!-- Status Card -->
        <div class="card">
            <h2>ORGANISM STATUS</h2>
            <div class="stat">
                <span class="stat-label">Health</span>
                <span class="stat-value" id="healthVal">--</span>
            </div>
            <div class="stat">
                <span class="stat-label">Intelligence</span>
                <span class="stat-value" id="intelligenceVal">--</span>
            </div>
            <div class="progress-bar"><div class="progress-fill" id="intelligenceBar" style="width:10%"></div></div>
            <div class="stat" style="margin-top:10px">
                <span class="stat-label">Capabilities</span>
                <span class="stat-value" id="capsVal">--</span>
            </div>
            <div class="stat">
                <span class="stat-label">Uptime</span>
                <span class="stat-value" id="uptimeVal">--</span>
            </div>
            <div class="stat">
                <span class="stat-label">Oracle DB</span>
                <span class="stat-value" id="oracleVal">--</span>
            </div>
        </div>

        <!-- AI Organs Card -->
        <div class="card">
            <h2>AI ORGANS</h2>
            <div id="organsContainer">Loading...</div>
        </div>

        <!-- Capabilities Card -->
        <div class="card">
            <h2>LEARNED CAPABILITIES</h2>
            <div id="capsContainer">Loading...</div>
        </div>

        <!-- Terminal -->
        <div class="terminal">
            <h2>COMMAND TERMINAL</h2>
            <div id="output">
                <div class="output-line output-apex">APEX Organism v0.1 Dashboard</div>
                <div class="output-line output-info">Type a command below. Examples:</div>
                <div class="output-line output-info">  "Search for AI breakthroughs 2026"</div>
                <div class="output-line output-info">  "Learn how to process images"</div>
                <div class="output-line output-info">  "Analyze cryptocurrency market trends"</div>
            </div>
            <div class="input-row">
                <input type="text" id="commandInput" placeholder="Type a command..." onkeypress="if(event.key==='Enter')sendCommand()">
                <button class="btn" onclick="sendCommand()">EXECUTE</button>
            </div>
        </div>
    </div>

    <script>
        const API = window.location.origin;
        let ws = null;

        function connectWS() {
            const wsUrl = API.replace('http', 'ws') + '/ws';
            ws = new WebSocket(wsUrl);
            ws.onmessage = (e) => {
                const msg = JSON.parse(e.data);
                if (msg.type === 'response') {
                    appendOutput(msg.content, 'apex');
                } else if (msg.type === 'status') {
                    updateStatus(msg.content);
                }
            };
            ws.onclose = () => setTimeout(connectWS, 3000);
        }

        async function refreshStatus() {
            try {
                const res = await fetch(API + '/api/status');
                const data = await res.json();
                updateStatus(data);
            } catch (e) {
                document.getElementById('versionLabel').textContent = 'Connection error';
            }
        }

        function updateStatus(data) {
            document.getElementById('healthVal').textContent = data.health + '%';
            document.getElementById('intelligenceVal').textContent = data.intelligence + '%';
            document.getElementById('intelligenceBar').style.width = data.intelligence + '%';
            document.getElementById('capsVal').textContent = data.capabilities_count;
            document.getElementById('oracleVal').textContent = data.oracle_connected ? 'CONNECTED' : 'FALLBACK';

            const uptime = Math.floor(data.uptime_seconds);
            const h = Math.floor(uptime / 3600);
            const m = Math.floor((uptime % 3600) / 60);
            document.getElementById('uptimeVal').textContent = h + 'h ' + m + 'm';
            document.getElementById('versionLabel').textContent = 'v' + data.version + ' | ' + data.ai_organs_active + ' organs active';

            // Capabilities
            const capsEl = document.getElementById('capsContainer');
            if (data.capabilities && data.capabilities.length > 0) {
                capsEl.innerHTML = data.capabilities.map(c =>
                    '<div style="padding:4px 0;border-bottom:1px solid #1a1a1a;font-size:13px">' + c + '</div>'
                ).join('');
            } else {
                capsEl.innerHTML = '<div style="color:#666">No capabilities yet. Try: "Learn how to process images"</div>';
            }
        }

        async function sendCommand() {
            const input = document.getElementById('commandInput');
            const cmd = input.value.trim();
            if (!cmd) return;
            input.value = '';

            appendOutput('> ' + cmd, 'user');
            appendOutput('Processing...', 'info');

            try {
                const res = await fetch(API + '/api/command', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({command: cmd})
                });
                const data = await res.json();
                appendOutput(data.result || data.error || 'Done.', 'apex');
                refreshStatus();
            } catch (e) {
                appendOutput('Error: ' + e.message, 'error');
            }
        }

        function appendOutput(text, type) {
            const output = document.getElementById('output');
            const line = document.createElement('div');
            line.className = 'output-line output-' + type;
            line.textContent = text;
            output.appendChild(line);
            output.scrollTop = output.scrollHeight;
        }

        // Initialize
        refreshStatus();
        connectWS();
        setInterval(refreshStatus, 30000);
    </script>
</body>
</html>"""
