from pydantic import BaseModel, Field
from typing import Dict, Any


class RecordData(BaseModel):
    """Model for creating new database records."""
    data: Dict[str, Any] = Field(
        ...,
        description="Column names mapped to values for the new record"
    )


class RecordUpdate(BaseModel):
    """Model for updating existing database records."""
    updates: Dict[str, Any] = Field(
        ...,
        description="Column names mapped to new values (only changed fields)"
    )
