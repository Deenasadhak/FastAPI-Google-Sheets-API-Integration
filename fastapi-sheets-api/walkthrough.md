# Code Walkthrough

This guide explains how each piece of the `fastapi-sheets-api` application works, the logical request flow, and how the Google Sheets API connects it all together.

## 1. How Each File Works

### `app/config.py`
We define environment variables via Pydantic `BaseSettings`. This file attempts to validate the `.env` file upon app startup. If `GOOGLE_CREDENTIALS_FILE` or `SPREADSHEET_ID` is missing, it crashes predictably rather than hiding the error until runtime.

### `app/schemas.py`
Pydantic is used to strictly define what data comes in (`SheetData`). For example, we mandate `age > 0` and minimal string boundaries. FastAPI parses JSON request bodies against this schema. If invalid, the framework rejects the request before it even reaches the logic.

### `app/core/logging_config.py`
Instead of calling `print()`, we use standard asynchronous logging that pushes formats with a standard timestamp/level/message line structure to `sys.stdout`. 

### `app/services/sheets_service.py`
This is where the heavy lifting happens. 
- **`get_sheets_service()`**: Uses `@Depends` to connect. It creates a Service Account context block avoiding the OAuth screen. 
- **`get_all_rows()`**: Asks Google for all cell contents in `Sheet1`.
- **`append_row()`**: Appends an array of values `[[name, email, age]]` directly into the next empty array layout. 
- **`update_row(row_number)`**: Targets a specific physical coordinate like `Sheet1!A5:C5` and overwrites it. 
- **`delete_row(row_number)`**: Clears the content of a specific cell boundary. Google doesn't have a specific `id` for rows unless you generate them yourself, so row indices are the baseline coordinate reference.

### `app/routers/sheets_router.py`
Translates plain HTTP requests into Python function calls. E.g., `POST /api/v1/data` routes directly to `create_data()` and invokes `append_row()`. All of these utilize the `format_success_response()` wrapper for standard output formatting.

### `app/main.py`
The nucleus. It binds `sheets_router` to the overall application. It adds CORS Middleware enabling frontend clients to talk to this API, and binds Global Exception Middleware, guaranteeing if an unknown `Exception` occurs, a neat `{"status": "error", "message": "..."}` displays rather than Python Server tracebacks hitting the web.

## 2. The Request Flow (e.g., POST Payload)

1. Client hits `POST /api/v1/data` giving a JSON payload `{"name": "X", "email": "Y", "age": 20}`.
2. FastAPI intercepts. Checks `Age` > 0 against `schemas.py`. 
3. Request passes validation -> enters `sheets_router.py`.
4. Router triggers `get_sheets_service()` dependency to spin up Google Credentials.
5. Router hands the sheet context off to `sheets_service.append_row()`, catching all Google exceptions smoothly mapping to `HTTPException`.
6. Helper wraps the response in a `{"status": "success", "data": ...}`.
7. End trip back to the client. 

## 3. How to Extend the Project

- **Database Synchronization:** You can add `sqlalchemy` schemas to echo Google Sheet adds into an external PostgreSQL cluster for high-availability reads.
- **Multiple Sheets:** Under `config.py` accept an array of SPREADSHEETS. Add an `id` to the `SheetData` allowing `/api/v1/data/{spreadsheet_id}/{row}` mapping.
- **Columns Expansion:** Update `schemas.py:SheetData` with more fields, and expand `sheets_service.update_row()` targeting `A:H` respectively.
