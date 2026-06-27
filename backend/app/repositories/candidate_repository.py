"""Repository helpers for candidate persistence."""

from sqlalchemy.orm import Session

from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate


def create_candidate(
    db: Session,
    *,
    candidate_data: CandidateCreate,
    resume_filename: str,
    resume_path: str,
    resume_text: str,
) -> Candidate:
    """Persist a candidate resume record and return the saved model."""
    candidate = Candidate(
        full_name=candidate_data.full_name,
        email=str(candidate_data.email) if candidate_data.email else None,
        phone_number=candidate_data.phone_number,
        resume_filename=resume_filename,
        resume_path=resume_path,
        resume_text=resume_text,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


def get_candidate_by_id(db: Session, candidate_id: int) -> Candidate | None:
    """Fetch a candidate by primary key."""
    return db.get(Candidate, candidate_id)
