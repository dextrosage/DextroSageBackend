import asyncio
import json
import logging
import os

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError

load_dotenv()

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

sheet: gspread.Worksheet | None = None


class GoogleSheetError(Exception):
    """Raised when Google Sheet operations fail."""


async def initialize_google_sheet() -> None:
    """
    Initialize Google Sheet.

    Should be called once when the server starts.
    """

    global sheet

    try:

        info = json.loads(
            os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
        )

        creds = Credentials.from_service_account_info(
            info,
            scopes=SCOPES,
        )

        client = gspread.authorize(creds)

        sheet = client.open_by_key(
            os.environ["GOOGLE_SERVICE_ACCOUNT_API"]
        ).sheet1

        logger.info("Google Sheet initialized successfully.")

    except Exception:

        logger.exception(
            "Failed to initialize Google Sheet."
        )

        sheet = None
        
async def add_user_to_sheet(
    user_id: str,
    username: str,
    password: str,
    email: str,
) -> None:

    if sheet is None:
        return

    def work():

        sheet.append_row(
            [
                user_id,
                username,
                password,
                email,
            ],
            value_input_option="RAW",
        )

    try:

        await asyncio.to_thread(work)

    except APIError as exc:

        raise GoogleSheetError(
            "Failed to add user to Google Sheet."
        ) from exc
        
async def update_password_in_sheet(
    user_id: str,
    password: str,
) -> None:
    """
    Update the password for the given user_id.

    Args:
        user_id: The user's unique ID.
        password: The new raw password to store.

    Raises:
        GoogleSheetError: If the Google Sheets API request fails.
    """

    if sheet is None:
        return

    def work() -> None:
        
        user_id_cell = sheet.find(
            user_id,
            in_column=1,
        )

        if user_id_cell is None:
            return

        # Column C = Password
        sheet.update_cell(
            row=user_id_cell.row,
            col=3,
            value=password,
        )

    try:
        await asyncio.to_thread(work)

    except APIError as exc:
        raise GoogleSheetError(
            "Failed to update password in Google Sheet."
        ) from exc
        
        
async def delete_user_from_sheet(
    user_id: str,
) -> None:
    """
    Delete the row corresponding to the given user_id.

    Args:
        user_id: The user's unique ID.

    Raises:
        GoogleSheetError: If the Google Sheets API request fails.
    """

    if sheet is None:
        return

    def work() -> None:
        user_id_cell = sheet.find(
            user_id,
            in_column=1,
        )

        if user_id_cell is None:
            return

        sheet.delete_rows(user_id_cell.row)

    try:
        await asyncio.to_thread(work)

    except APIError as exc:
        raise GoogleSheetError(
            "Failed to delete user from Google Sheet."
        ) from exc