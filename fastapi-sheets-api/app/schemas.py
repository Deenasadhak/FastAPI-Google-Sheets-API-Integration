# File: app/schemas.py
from pydantic import BaseModel, EmailStr, Field

class SheetData(BaseModel):
    name: str = Field(..., min_length=2, description="The name of the user")
    email: EmailStr = Field(..., description="The email address of the user")
    age: int = Field(..., gt=0, description="The age of the user, must be greater than 0")

class SheetDataResponse(SheetData):
    row_number: int
