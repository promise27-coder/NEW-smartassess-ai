"""Pydantic schemas for candidate resume records."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CandidateCreate(BaseModel):
    """Validated candidate details accepted with a resume upload."""

    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr | None = Field(default=None)
    phone_number: str | None = Field(
        default=None,
        min_length=7,
        max_length=32,
        pattern=r"^[0-9+()\-\s]+$",
    )


class CandidateResponse(BaseModel):
    """Public candidate response returned after resume upload."""

    id: int
    full_name: str
    email: EmailStr | None
    phone_number: str | None
    resume_filename: str
    resume_path: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CandidateDetailResponse(CandidateResponse):
    """Detailed candidate response including extracted resume text."""

    resume_text: str
