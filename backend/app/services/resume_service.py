"""Resume upload, storage, and text extraction service."""

from pathlib import Path
import re
from uuid import uuid4

import fitz
from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.settings import Settings, settings
from app.models.candidate import Candidate
from app.repositories.candidate_repository import create_candidate, get_candidate_by_id
from app.schemas.candidate import CandidateCreate

PDF_CONTENT_TYPES = {"application/pdf", "application/x-pdf"}
READ_CHUNK_SIZE_BYTES = 1024 * 1024


class ResumeValidationError(ValueError):
    """Raised when an uploaded resume fails validation."""


class ResumeProcessingError(RuntimeError):
    """Raised when a resume cannot be processed or saved."""


class CandidateNotFoundError(LookupError):
    """Raised when a candidate record cannot be found."""


class ResumeService:
    """Coordinate resume validation, local storage, text extraction, and persistence."""

    def __init__(self, db: Session, app_settings: Settings | None = None) -> None:
        """Initialize the service with a database session and runtime settings."""
        self.db = db
        self.settings = app_settings or settings

    async def upload_resume(
        self,
        *,
        file: UploadFile,
        candidate_data: CandidateCreate,
    ) -> Candidate:
        """Validate, store, extract, and persist an uploaded PDF resume."""
        resume_bytes = await self._read_upload(file)
        self._validate_pdf_upload(file=file, resume_bytes=resume_bytes)
        resume_text = self._extract_text(resume_bytes)
        resume_filename = self._safe_resume_filename(file.filename or "resume.pdf")
        resume_path = self._store_resume(resume_filename, resume_bytes)

        try:
            return create_candidate(
                self.db,
                candidate_data=candidate_data,
                resume_filename=resume_filename,
                resume_path=resume_path,
                resume_text=resume_text,
            )
        except SQLAlchemyError as exc:
            self.db.rollback()
            self._remove_stored_resume(resume_path)
            raise ResumeProcessingError(
                "Unable to save candidate resume details."
            ) from exc

    def get_candidate(self, candidate_id: int) -> Candidate:
        """Return a candidate record or raise when it does not exist."""
        candidate = get_candidate_by_id(self.db, candidate_id)
        if candidate is None:
            raise CandidateNotFoundError("Candidate resume record was not found.")
        return candidate

    async def _read_upload(self, file: UploadFile) -> bytes:
        """Read an upload in chunks while enforcing the configured size limit."""
        chunks: list[bytes] = []
        total_size = 0

        while chunk := await file.read(READ_CHUNK_SIZE_BYTES):
            total_size += len(chunk)
            if total_size > self.settings.resume_max_file_size_bytes:
                raise ResumeValidationError("PDF resume exceeds the maximum upload size.")
            chunks.append(chunk)

        if total_size == 0:
            raise ResumeValidationError("Uploaded resume file is empty.")

        return b"".join(chunks)

    def _validate_pdf_upload(self, *, file: UploadFile, resume_bytes: bytes) -> None:
        """Validate file metadata and PDF magic bytes."""
        filename = file.filename or ""
        if Path(filename).suffix.lower() != ".pdf":
            raise ResumeValidationError("Only PDF resume files are accepted.")

        if file.content_type not in PDF_CONTENT_TYPES:
            raise ResumeValidationError("Resume upload must use the application/pdf content type.")

        if not resume_bytes.startswith(b"%PDF-"):
            raise ResumeValidationError("Uploaded file is not a valid PDF document.")

    def _extract_text(self, resume_bytes: bytes) -> str:
        """Extract text from a PDF resume using PyMuPDF."""
        try:
            with fitz.open(stream=resume_bytes, filetype="pdf") as document:
                text_parts = [page.get_text("text").strip() for page in document]
        except Exception as exc:
            raise ResumeProcessingError("Unable to extract text from the PDF resume.") from exc

        resume_text = "\n\n".join(part for part in text_parts if part)
        if not resume_text.strip():
            raise ResumeValidationError("PDF resume does not contain extractable text.")

        return resume_text

    def _store_resume(self, resume_filename: str, resume_bytes: bytes) -> str:
        """Store a PDF resume locally and return the saved path."""
        upload_dir = self.settings.resume_upload_dir
        upload_dir.mkdir(parents=True, exist_ok=True)

        stored_filename = f"{uuid4().hex}_{resume_filename}"
        stored_path = upload_dir / stored_filename
        stored_path.write_bytes(resume_bytes)
        return stored_path.as_posix()

    def _remove_stored_resume(self, resume_path: str) -> None:
        """Best-effort cleanup for a resume file when persistence fails."""
        try:
            Path(resume_path).unlink(missing_ok=True)
        except OSError:
            return

    def _safe_resume_filename(self, filename: str) -> str:
        """Return a filesystem-safe PDF filename."""
        original_name = Path(filename).name
        sanitized_name = re.sub(r"[^A-Za-z0-9._-]+", "_", original_name).strip("._")
        if not sanitized_name:
            return "resume.pdf"
        return sanitized_name
