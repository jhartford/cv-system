"""Data models for CV management using Pydantic."""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field
from datetime import datetime


class PersonalInfo(BaseModel):
    """Personal information and contact details."""
    name: str
    current_position: str
    department: str
    institution: str
    email: str
    website: Optional[str] = None
    phone: Optional[str] = None
    orcid: Optional[str] = None
    address: Optional[str] = None


class Education(BaseModel):
    """Education entry."""
    year: int
    degree: str
    institution: str
    thesis: Optional[str] = None
    supervisor: Optional[str] = None


class Publication(BaseModel):
    """Publication entry."""
    title: str
    authors: List[str]
    year: int
    venue: Optional[str] = None
    journal: Optional[str] = None
    conference: Optional[str] = None
    volume: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    arxiv: Optional[str] = None
    type: Optional[str] = None  # "oral", "poster", etc.
    acceptance_rate: Optional[str] = None
    award: Optional[str] = None


class Grant(BaseModel):
    """Grant or award entry."""
    title: str
    year: Union[int, str]  # Can be "2024-2029" for multi-year
    amount: Optional[str] = None
    organization: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None  # "declined", "active", etc.
    description: Optional[str] = None


class Teaching(BaseModel):
    """Teaching or mentoring entry."""
    year: Union[int, str]
    role: str
    course: Optional[str] = None
    institution: str
    instructor: Optional[str] = None
    students: Optional[str] = None
    description: Optional[str] = None


class Supervision(BaseModel):
    """Student supervision entry."""
    year: Union[int, str]
    student: str
    institution: str
    level: str  # "PhD", "MSc", "Undergraduate", "Intern"
    collaborator: Optional[str] = None
    status: Optional[str] = None  # "incoming", "ongoing", "completed"


class ServiceActivity(BaseModel):
    """Service or review activity."""
    year: Union[int, List[int], str]
    venue: str
    role: str
    description: Optional[str] = None


class Talk(BaseModel):
    """Talk or presentation."""
    year: int
    title: str
    venue: str
    location: Optional[str] = None
    type: str  # "keynote", "invited", "conference", etc.
    collaborator: Optional[str] = None


class CVData(BaseModel):
    """Complete CV data structure."""
    personal: PersonalInfo
    education: List[Education] = Field(default_factory=list)

    # Publications organized by type
    publications: Dict[str, Union[List[Publication], Dict[str, List[Publication]]]] = Field(
        default_factory=lambda: {
            "preprints": [],
            "conference_papers": {},
            "journal_papers": [],
            "under_review": [],
            "workshop_papers": []
        }
    )

    # Grants and awards by category
    grants: Dict[str, List[Grant]] = Field(
        default_factory=lambda: {
            "fellowships": [],
            "grants": [],
            "conference_awards": [],
            "university_awards": [],
            "research_awards": []
        }
    )

    # Teaching activities
    teaching: List[Teaching] = Field(default_factory=list)
    supervision: List[Supervision] = Field(default_factory=list)

    # Service activities
    service: Dict[str, List[ServiceActivity]] = Field(
        default_factory=lambda: {
            "conference_reviews": [],
            "journal_reviews": [],
            "workshops": [],
            "volunteer": []
        }
    )

    # Talks and presentations
    talks: Dict[str, List[Talk]] = Field(
        default_factory=lambda: {
            "keynotes": [],
            "conference": [],
            "invited": [],
            "industry": [],
            "seminars": []
        }
    )

    # Configuration for CV variants
    config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "templates": {
                "promotion": {"include_all": True},
                "academic_us": {"exclude_sections": []},
                "academic_uk": {"exclude_sections": []}
            }
        }
    )