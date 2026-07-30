import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from hashlib import sha256

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError, WorksheetNotFound

load_dotenv()
logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

gc: gspread.Client | None = None
spreadsheet: gspread.Spreadsheet | None = None

async def initialize_google_sheet_chat() -> None:
    global gc
    global spreadsheet
    try:
        info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
        gc = gspread.authorize(creds)
        spreadsheet = gc.open_by_key(os.environ["GOOGLE_SERVICE_ACCOUNT_API"])
        logger.info("Google Sheet Chat initialized successfully.")
    except Exception:
        logger.exception("Failed to initialize Google Sheet Chat.")
        gc = None
        spreadsheet = None

def get_worksheet_name(user1_id: str, user2_id: str) -> str:
    sorted_ids = sorted([user1_id, user2_id])
    return sha256(f"{sorted_ids[0]}_{sorted_ids[1]}".encode()).hexdigest()[:30]

async def send_message_to_sheet(sender_id: str, receiver_id: str, text: str) -> None:
    if spreadsheet is None:
        return
    def work():
        ws_name = get_worksheet_name(sender_id, receiver_id)
        try:
            ws = spreadsheet.worksheet(ws_name)
        except WorksheetNotFound:
            ws = spreadsheet.add_worksheet(title=ws_name, rows=100, cols=3)
            ws.append_row(["Sender ID", "Text", "Timestamp"])
        timestamp = datetime.now(timezone.utc).isoformat()
        ws.append_row([sender_id, text, timestamp], value_input_option="RAW")
    try:
        await asyncio.to_thread(work)
    except APIError as exc:
        raise Exception("Failed to send message.") from exc

async def get_messages_from_sheet(user1_id: str, user2_id: str, page: int = 1, page_size: int = 30) -> list[dict]:
    if spreadsheet is None:
        return []
    def work():
        ws_name = get_worksheet_name(user1_id, user2_id)
        try:
            ws = spreadsheet.worksheet(ws_name)
        except WorksheetNotFound:
            return []
        
        all_values = ws.get_all_values()
        if len(all_values) <= 1:
            return []
            
        data = all_values[1:] # Skip header
        data.reverse()
        start = (page - 1) * page_size
        end = start + page_size
        page_data = data[start:end]
        page_data.reverse()
        
        return [{"sender_id": row[0], "text": row[1], "timestamp": row[2]} for row in page_data]
    try:
        return await asyncio.to_thread(work)
    except APIError as exc:
        raise Exception("Failed to fetch messages.") from exc
