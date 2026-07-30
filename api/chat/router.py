from fastapi import APIRouter, Depends, Query, Path, WebSocket, WebSocketDisconnect
from Request_and_Response.Requests import ChatSendRequest
from Request_and_Response.Responses import ChatMessagesResponse
from dependency.token_dependency import verify_user_access_token
from security.google_sheet_chat import send_message_to_sheet, get_messages_from_sheet
from typing import Dict
import json
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

manager = ConnectionManager()

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str = Path(description="User ID connecting")):
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)

@router.post("/{target_user_id}/send", response_model=dict)
async def send_chat_message(
    target_user_id: str = Path(description="Target User ID"),
    req: ChatSendRequest = None,
    payload: dict = Depends(verify_user_access_token)
):
    await send_message_to_sheet(payload['sub'], target_user_id, req.text)
    
    ws_message = {
        "sender_id": payload['sub'],
        "text": req.text,
        "timestamp": str(datetime.now())
    }
    await manager.send_personal_message(json.dumps(ws_message), target_user_id)
    
    return {"status": "Message sent successfully"}

@router.get("/{target_user_id}", response_model=ChatMessagesResponse)
async def get_chat_messages(
    target_user_id: str = Path(description="Target User ID"),
    page: int = Query(1, ge=1, description="Page number"),
    payload: dict = Depends(verify_user_access_token)
):
    messages = await get_messages_from_sheet(payload['sub'], target_user_id, page=page)
    return {"messages": messages, "page": page}
