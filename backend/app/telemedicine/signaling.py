from collections import defaultdict
from fastapi import WebSocket, WebSocketDisconnect


class SignalingRoom:
    def __init__(self) -> None:
        self.peers: dict[str, WebSocket] = {}

    async def connect(self, peer_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.peers[peer_id] = websocket

    def disconnect(self, peer_id: str) -> None:
        self.peers.pop(peer_id, None)

    async def broadcast(self, sender_id: str, message: dict) -> None:
        stale: list[str] = []
        for peer_id, websocket in self.peers.items():
            if peer_id == sender_id:
                continue
            try:
                await websocket.send_json({"from": sender_id, **message})
            except Exception:
                stale.append(peer_id)
        for peer_id in stale:
            self.disconnect(peer_id)


rooms: dict[str, SignalingRoom] = defaultdict(SignalingRoom)


async def signaling_session(room_id: str, peer_id: str, websocket: WebSocket) -> None:
    room = rooms[room_id]
    await room.connect(peer_id, websocket)
    await websocket.send_json({"type": "joined", "room_id": room_id, "peer_id": peer_id, "demo_mode": True})
    try:
        while True:
            message = await websocket.receive_json()
            await room.broadcast(peer_id, message)
    except WebSocketDisconnect:
        room.disconnect(peer_id)
        await room.broadcast(peer_id, {"type": "peer_left", "peer_id": peer_id})
