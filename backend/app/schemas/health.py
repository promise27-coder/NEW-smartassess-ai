"""Pydantic schemas for health check responses."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response payload returned by the health check endpoint."""

    status: Literal["healthy"]
    service: Literal["SmartAssess AI Backend"]
