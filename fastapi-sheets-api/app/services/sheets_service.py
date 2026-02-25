# File: app/services/sheets_service.py
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fastapi import HTTPException
from typing import List, Dict, Any

from app.config import settings
from app.core.logging_config import get_logger
from app.schemas import SheetData

logger = get_logger(__name__)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_sheets_service():
    """
    Authenticate using a service account and return the Google Sheets API 'Resource' object.
    Raises an HTTPException if authentication fails.
    """
    try:
        logger.info(f"Loaded credentials file path: {settings.GOOGLE_CREDENTIALS_FILE}")
        logger.info(f"Loaded Spreadsheet ID: {settings.SPREADSHEET_ID}")
        
        credentials = Credentials.from_service_account_file(
            settings.GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
        )
        service = build('sheets', 'v4', credentials=credentials)
        
        logger.info("Successfully initialized Google Sheets service")
        return service
    except Exception as e:
        logger.error(f"Failed to authenticate Google Sheets Service: {e}")
        raise HTTPException(status_code=500, detail="Internal server error: Google authentication failed")

# We will work with a specific range (e.g. Sheet1)
DEFAULT_RANGE = "Sheet1"

def get_all_rows(service) -> List[Dict[str, Any]]:
    """
    Fetch all rows from the spreadsheet.
    """
    try:
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=settings.SPREADSHEET_ID,
            range=DEFAULT_RANGE
        ).execute()

        values = result.get('values', [])
        
        if not values:
            return []
            
        # Assuming row 1 is headers: [Name, Email, Age]
        headers = values[0]
        data_rows = values[1:]
        
        parsed_data = []
        for i, row in enumerate(data_rows):
            # i+2 gives us the actual integer row number on the google sheet (1-based index, +1 for header)
            
            # handle cases where rows might be missing some columns at the end
            name = row[0] if len(row) > 0 else ""
            email = row[1] if len(row) > 1 else ""
            age = row[2] if len(row) > 2 else 0

            try:
                age_int = int(age)
            except ValueError:
                age_int = 0

            parsed_data.append({
                "row_number": i + 2,
                "name": name,
                "email": email,
                "age": age_int
            })

        logger.info(f"Successfully retrieved {len(parsed_data)} rows.")
        return parsed_data

    except HttpError as err:
        logger.error(f"Google API HTTP Error fetching rows: {err}")
        raise HTTPException(status_code=err.resp.status, detail=f"Google API Error: {err._get_reason()}")
    except Exception as e:
        logger.error(f"Unexpected error fetching rows: {e}")
        raise HTTPException(status_code=500, detail="Error fetching data from spreadsheet.")

def append_row(service, data: SheetData) -> Dict[str, Any]:
    """
    Append a new row to the end of the sheet.
    """
    try:
        sheet = service.spreadsheets()
        values = [[data.name, data.email, data.age]]
        body = {'values': values}

        result = sheet.values().append(
            spreadsheetId=settings.SPREADSHEET_ID,
            range=DEFAULT_RANGE,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()

        updated_range = result.get('updates', {}).get('updatedRange', '')
        logger.info(f"Successfully appended row: {updated_range}")
        
        return {"appended_range": updated_range}

    except HttpError as err:
        logger.error(f"Google API HTTP Error appending row: {err}")
        raise HTTPException(status_code=err.resp.status, detail=f"Google API Error: {err._get_reason()}")
    except Exception as e:
        logger.error(f"Unexpected error appending row: {e}")
        raise HTTPException(status_code=500, detail="Error saving data to spreadsheet.")

def update_row(service, row_number: int, data: SheetData) -> Dict[str, Any]:
    """
    Update a specific row number with new data. 
    Notes: row_number 1 typically headers, 2 is first data row.
    """
    if row_number < 2:
        raise HTTPException(status_code=400, detail="Cannot update header row (row 1). Please specify row_number >= 2.")

    try:
        sheet = service.spreadsheets()
        
        # A, B, C map to Name, Email, Age (assume A-C columns)
        update_range = f"Sheet1!A{row_number}:C{row_number}"
        values = [[data.name, data.email, data.age]]
        body = {'values': values}

        result = sheet.values().update(
            spreadsheetId=settings.SPREADSHEET_ID,
            range=update_range,
            valueInputOption='RAW',
            body=body
        ).execute()

        logger.info(f"Successfully updated row {row_number}")
        return {"updated_range": update_range, "updated_cells": result.get('updatedCells')}

    except HttpError as err:
        logger.error(f"Google API HTTP Error updating row {row_number}: {err}")
        raise HTTPException(status_code=err.resp.status, detail=f"Google API Error: {err._get_reason()}")
    except Exception as e:
        logger.error(f"Unexpected error updating row {row_number}: {e}")
        raise HTTPException(status_code=500, detail="Error updating data in spreadsheet.")

def delete_row(service, row_number: int) -> Dict[str, Any]:
    """
    Clear a specific row number in the spreadsheet.
    Note: 'Clear' removes values but leaves the empty row cells. Deleting actual row dimension requires batchUpdate.
    For simplicity, 'Clear' is often standard.
    """
    if row_number < 2:
        raise HTTPException(status_code=400, detail="Cannot clear header row (row 1). Please specify row_number >= 2.")

    try:
        sheet = service.spreadsheets()
        
        clear_range = f"Sheet1!A{row_number}:C{row_number}"
        
        result = sheet.values().clear(
            spreadsheetId=settings.SPREADSHEET_ID,
            range=clear_range
        ).execute()

        logger.info(f"Successfully cleared row {row_number}")
        return {"cleared_range": clear_range}

    except HttpError as err:
        logger.error(f"Google API HTTP Error clearing row {row_number}: {err}")
        raise HTTPException(status_code=err.resp.status, detail=f"Google API Error: {err._get_reason()}")
    except Exception as e:
        logger.error(f"Unexpected error clearing row {row_number}: {e}")
        raise HTTPException(status_code=500, detail="Error clearing data in spreadsheet.")
