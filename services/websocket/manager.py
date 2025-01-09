from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Dict

# Quản lý trạng thái phòng nghe nhạc
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    async def disconnect(self, room_id: str, websocket: WebSocket):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)


    async def broadcast(self, data: dict, room_id: str):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id][:]:
                try:
                    await connection.send_json(data)
                except Exception as e:
                    # Log and remove problematic connection
                    self.active_connections[room_id].remove(connection)
                    print(f"Error broadcasting to connection: {e}")

manager = ConnectionManager()
