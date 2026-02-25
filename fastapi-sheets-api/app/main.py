# File: app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from googleapiclient.errors import HttpError
import uvicorn

from app.routers import sheets_router
from app.core.logging_config import get_logger
from app.utils.helpers import format_error_response

logger = get_logger(__name__)

# FastAPI app creation
app = FastAPI(
    title="Google Sheets REST API",
    description="A production-ready FastAPI application to interact with Google Sheets",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(sheets_router.router)

# Global Exception Handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception at {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=format_error_response("Internal Server Error", str(exc))
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error at {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content=format_error_response("Unprocessable Entity", exc.errors())
    )

@app.exception_handler(HttpError)
async def google_api_error_handler(request: Request, exc: HttpError):
    logger.error(f"Google API error at {request.url.path}: {exc._get_reason()}")
    return JSONResponse(
        status_code=exc.resp.status,
        content=format_error_response("Google API Error", exc._get_reason())
    )

@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse("app/static/index.html")

# Run command placeholder for python -m app.main
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
