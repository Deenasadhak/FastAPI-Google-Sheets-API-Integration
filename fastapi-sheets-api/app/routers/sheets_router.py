# File: app/routers/sheets_router.py
from fastapi import APIRouter, Depends, Path, HTTPException
from typing import Any

from app.schemas import SheetData
from app.services.sheets_service import (
    get_sheets_service, 
    get_all_rows, 
    append_row, 
    update_row, 
    delete_row
)
from app.utils.helpers import format_success_response

router = APIRouter(
    prefix="/api/v1",
    tags=["Google Sheets Data"],
    dependencies=[Depends(get_sheets_service)]
)

@router.get("/health", summary="Health Check")
async def health_check():
    """
    Simple endpoint to check if the API is running and responding.
    """
    return format_success_response({"status": "healthy"}, "API is up and running")

@router.get("/data", summary="Get all rows")
async def read_data(service: Any = Depends(get_sheets_service)):
    """
    Retrieve all rows from the Google Sheet.
    Returns a list of dictionaries where each object contains row_number, name, email, and age.
    """
    data = get_all_rows(service)
    return format_success_response(data, "Successfully retrieved data")

@router.post("/data", summary="Add a new row")
async def create_data(sheet_data: SheetData, service: Any = Depends(get_sheets_service)):
    """
    Append a single user row to the Google Sheet.
    """
    result = append_row(service, sheet_data)
    return format_success_response(result, "Successfully added new row")

@router.put("/data/{row_number}", summary="Update a row")
async def modify_data(
    sheet_data: SheetData, 
    row_number: int = Path(..., title="The integer row number to update (e.g. 2)"),
    service: Any = Depends(get_sheets_service)
):
    """
    Overwrites the specified row in the Google Sheet.
    """
    result = update_row(service, row_number, sheet_data)
    return format_success_response(result, f"Successfully updated row {row_number}")

@router.delete("/data/{row_number}", summary="Clear a row")
async def remove_data(
    row_number: int = Path(..., title="The integer row number to clear (e.g. 2)"),
    service: Any = Depends(get_sheets_service)
):
    """
    Clears the content of a specific row without deleting the cell structure.
    """
    result = delete_row(service, row_number)
    return format_success_response(result, f"Successfully cleared row {row_number}")
