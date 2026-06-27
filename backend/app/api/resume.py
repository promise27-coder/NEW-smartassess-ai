"""Resume Intelligence API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.candidate import CandidateCreate, CandidateDetailResponse, CandidateResponse
from app.services.resume_service import (
    CandidateNotFoundError,
    ResumeProcessingError,
    ResumeService,
    ResumeValidationError,
)

router = APIRouter(prefix="/api/v1/resume", tags=["Resume Intelligence"])


def _optional_form_value(value: str | None) -> str | None:
    """Normalize optional form values by treating blank strings as missing."""
    if value is None:
        return None
    stripped_value = value.strip()
    return stripped_value or None


@router.post(
    "/upload",
    response_model=CandidateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_resume(
    file: Annotated[UploadFile, File(description="PDF resume file")],
    full_name: Annotated[str, Form(min_length=1, max_length=255)],
    db: Annotated[Session, Depends(get_db)],
    email: Annotated[str | None, Form()] = None,
    phone_number: Annotated[str | None, Form()] = None,
) -> CandidateResponse:
    """Upload a PDF resume, extract text, and create a candidate record."""
    try:
        candidate_data = CandidateCreate(
            full_name=full_name.strip(),
            email=_optional_form_value(email),
            phone_number=_optional_form_value(phone_number),
        )
        candidate = await ResumeService(db).upload_resume(
            file=file,
            candidate_data=candidate_data,
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(include_url=False),
        ) from exc
    except ResumeValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ResumeProcessingError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    return CandidateResponse.model_validate(candidate)


@router.get("/{candidate_id}", response_model=CandidateDetailResponse)
def get_resume(
    candidate_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> CandidateDetailResponse:
    """Return candidate resume details and extracted text by candidate ID."""
    try:
        candidate = ResumeService(db).get_candidate(candidate_id)
    except CandidateNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return CandidateDetailResponse.model_validate(candidate)
