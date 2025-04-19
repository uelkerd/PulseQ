"""
Grant management module.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from .billing import ContractType


class GrantType(Enum):
    """Types of grants supported."""

    RESEARCH = "research"
    DEFENSE = "defense"
    SPACE = "space"
    INTERNATIONAL = "international"
    ACADEMIC = "academic"


class GrantStatus(Enum):
    """Grant status levels."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    COMPLETED = "completed"
    TERMINATED = "terminated"


@dataclass
class Publication:
    """Research publication details."""

    id: str
    title: str
    authors: List[str]
    journal: str
    publication_date: datetime
    doi: Optional[str] = None
    grant_id: Optional[str] = None
    impact_factor: Optional[float] = None


@dataclass
class Milestone:
    """Project milestone."""

    id: str
    name: str
    description: str
    due_date: datetime
    status: str = "pending"
    completion_date: Optional[datetime] = None
    deliverables: List[str] = None


class GrantManager:
    """Manages grants and research projects."""

    def __init__(self):
        """Initialize grant manager."""
        self.logger = logging.getLogger("grant_manager")
        self.grants: Dict[str, Dict[str, Any]] = {}
        self.publications: Dict[str, Publication] = {}
        self.milestones: Dict[str, Milestone] = {}

    async def create_grant_proposal(
        self,
        grant_type: GrantType,
        title: str,
        description: str,
        principal_investigator: str,
        institution: str,
        budget: float,
        duration_months: int,
        requirements: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a new grant proposal."""
        grant_id = f"GR{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        grant = {
            "id": grant_id,
            "type": grant_type.value,
            "title": title,
            "description": description,
            "principal_investigator": principal_investigator,
            "institution": institution,
            "budget": budget,
            "duration_months": duration_months,
            "start_date": None,
            "end_date": None,
            "status": GrantStatus.DRAFT.value,
            "requirements": requirements,
            "milestones": [],
            "publications": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        self.grants[grant_id] = grant
        return grant

    async def submit_grant_proposal(self, grant_id: str) -> Dict[str, Any]:
        """Submit a grant proposal for review."""
        if grant_id not in self.grants:
            raise ValueError(f"Grant {grant_id} not found")

        grant = self.grants[grant_id]
        grant["status"] = GrantStatus.SUBMITTED.value
        grant["updated_at"] = datetime.utcnow().isoformat()

        return grant

    async def track_grant_progress(self, grant_id: str) -> Dict[str, Any]:
        """Track progress of an active grant."""
        if grant_id not in self.grants:
            raise ValueError(f"Grant {grant_id} not found")

        grant = self.grants[grant_id]

        # Calculate progress metrics
        total_milestones = len(grant["milestones"])
        completed_milestones = len(
            [m for m in grant["milestones"] if m["status"] == "completed"]
        )

        progress = {
            "grant_id": grant_id,
            "status": grant["status"],
            "milestone_progress": {
                "total": total_milestones,
                "completed": completed_milestones,
                "percentage": (
                    (completed_milestones / total_milestones * 100)
                    if total_milestones > 0
                    else 0
                ),
            },
            "publications": len(grant["publications"]),
            "budget_utilization": self._calculate_budget_utilization(grant),
            "timeline": self._calculate_timeline_progress(grant),
        }

        return progress

    def _calculate_budget_utilization(self, grant: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate budget utilization metrics."""
        # Implementation would track actual spending
        return {
            "total_budget": grant["budget"],
            "spent": 0,
            "remaining": grant["budget"],
            "utilization_percentage": 0,
        }

    def _calculate_timeline_progress(self, grant: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate timeline progress metrics."""
        if not grant["start_date"]:
            return {
                "start_date": None,
                "end_date": None,
                "elapsed_days": 0,
                "remaining_days": grant["duration_months"] * 30,
                "percentage": 0,
            }

        start_date = datetime.fromisoformat(grant["start_date"])
        end_date = datetime.fromisoformat(grant["end_date"])
        now = datetime.utcnow()

        total_days = (end_date - start_date).days
        elapsed_days = (now - start_date).days
        remaining_days = (end_date - now).days

        return {
            "start_date": grant["start_date"],
            "end_date": grant["end_date"],
            "elapsed_days": elapsed_days,
            "remaining_days": remaining_days,
            "percentage": (elapsed_days / total_days * 100) if total_days > 0 else 0,
        }

    async def add_publication(self, grant_id: str, publication: Publication) -> None:
        """Add a publication to a grant."""
        if grant_id not in self.grants:
            raise ValueError(f"Grant {grant_id} not found")

        self.publications[publication.id] = publication
        self.grants[grant_id]["publications"].append(publication.id)

    async def get_publication_metrics(self, grant_id: str) -> Dict[str, Any]:
        """Get publication metrics for a grant."""
        if grant_id not in self.grants:
            raise ValueError(f"Grant {grant_id} not found")

        publications = [
            self.publications[pub_id]
            for pub_id in self.grants[grant_id]["publications"]
        ]

        return {
            "total_publications": len(publications),
            "average_impact_factor": (
                sum(p.impact_factor for p in publications if p.impact_factor)
                / len(publications)
                if publications
                else 0
            ),
            "publications_by_year": self._group_publications_by_year(publications),
            "citations": sum(
                len(p.authors) for p in publications
            ),  # Simplified citation count
        }

    def _group_publications_by_year(
        self, publications: List[Publication]
    ) -> Dict[int, int]:
        """Group publications by year."""
        years = {}
        for pub in publications:
            year = pub.publication_date.year
            years[year] = years.get(year, 0) + 1
        return years

    async def create_milestone(self, grant_id: str, milestone: Milestone) -> None:
        """Add a milestone to a grant."""
        if grant_id not in self.grants:
            raise ValueError(f"Grant {grant_id} not found")

        self.milestones[milestone.id] = milestone
        self.grants[grant_id]["milestones"].append(milestone.id)

    async def update_milestone_status(
        self, milestone_id: str, status: str, completion_date: Optional[datetime] = None
    ) -> None:
        """Update milestone status."""
        if milestone_id not in self.milestones:
            raise ValueError(f"Milestone {milestone_id} not found")

        milestone = self.milestones[milestone_id]
        milestone.status = status
        if completion_date:
            milestone.completion_date = completion_date
