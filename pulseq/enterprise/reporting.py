"""
Advanced reporting capabilities for compliance and security.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .compliance import ComplianceFramework, ComplianceStatus
from .compliance_packages import CompliancePackage


@dataclass
class ReportMetrics:
    """Metrics for compliance reports."""

    total_requirements: int
    compliant_requirements: int
    partially_compliant: int
    non_compliant: int
    in_progress: int
    waived: int
    conditional: int
    validation_methods: Dict[str, int]
    risk_score: float
    last_updated: datetime


class ComplianceReporter:
    """Advanced compliance reporting system."""

    def __init__(self):
        """Initialize compliance reporter."""
        self.logger = logging.getLogger("compliance_reporter")
        self.report_cache: Dict[str, Dict[str, Any]] = {}
        self.metrics_history: Dict[str, List[ReportMetrics]] = {}

    async def generate_comprehensive_report(
        self, package: CompliancePackage, timeframe: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """Generate a comprehensive compliance report."""
        metrics = await self._calculate_metrics(package)
        trends = await self._analyze_trends(package.name, metrics)
        risks = await self._assess_risks(package)

        report = {
            "package": package.get_package_details(),
            "timeframe": {
                "start": (datetime.utcnow() - timeframe).isoformat(),
                "end": datetime.utcnow().isoformat(),
            },
            "metrics": {
                "total_requirements": metrics.total_requirements,
                "compliant_requirements": metrics.compliant_requirements,
                "partially_compliant": metrics.partially_compliant,
                "non_compliant": metrics.non_compliant,
                "in_progress": metrics.in_progress,
                "waived": metrics.waived,
                "conditional": metrics.conditional,
                "validation_methods": metrics.validation_methods,
                "risk_score": metrics.risk_score,
                "last_updated": metrics.last_updated.isoformat(),
            },
            "trends": trends,
            "risk_assessment": risks,
            "recommendations": await self._generate_recommendations(package, metrics),
            "action_items": await self._generate_action_items(package, metrics),
            "compliance_score": self._calculate_compliance_score(metrics),
            "framework_coverage": await self._analyze_framework_coverage(package),
            "validation_efficiency": await self._analyze_validation_efficiency(package),
            "emergency_preparedness": await self._assess_emergency_preparedness(
                package
            ),
        }

        self.report_cache[package.name] = report
        self._update_metrics_history(package.name, metrics)

        return report

    async def _calculate_metrics(self, package: CompliancePackage) -> ReportMetrics:
        """Calculate metrics for a compliance package."""
        requirements = package.requirements
        validation_methods = {"automated": 0, "manual": 0, "hybrid": 0}

        for req in requirements:
            validation_methods[req.validation_method] += 1

        return ReportMetrics(
            total_requirements=len(requirements),
            compliant_requirements=len(
                [r for r in requirements if r.status == ComplianceStatus.COMPLIANT]
            ),
            partially_compliant=len(
                [
                    r
                    for r in requirements
                    if r.status == ComplianceStatus.PARTIALLY_COMPLIANT
                ]
            ),
            non_compliant=len(
                [r for r in requirements if r.status == ComplianceStatus.NON_COMPLIANT]
            ),
            in_progress=len(
                [r for r in requirements if r.status == ComplianceStatus.IN_PROGRESS]
            ),
            waived=len(
                [r for r in requirements if r.status == ComplianceStatus.WAIVED]
            ),
            conditional=len(
                [r for r in requirements if r.status == ComplianceStatus.CONDITIONAL]
            ),
            validation_methods=validation_methods,
            risk_score=self._calculate_risk_score(requirements),
            last_updated=datetime.utcnow(),
        )

    def _calculate_risk_score(self, requirements: List[Any]) -> float:
        """Calculate overall risk score based on requirements."""
        if not requirements:
            return 0.0

        total_risk = sum(
            (
                1.0
                if req.severity == "critical"
                else (
                    0.7
                    if req.severity == "high"
                    else 0.4
                    if req.severity == "medium"
                    else 0.1
                )
            )
            for req in requirements
        )

        return total_risk / len(requirements)

    async def _analyze_trends(
        self, package_name: str, current_metrics: ReportMetrics
    ) -> Dict[str, Any]:
        """Analyze trends in compliance metrics."""
        if package_name not in self.metrics_history:
            return {"status": "insufficient_data"}

        history = self.metrics_history[package_name]
        if len(history) < 2:
            return {"status": "insufficient_data"}

        previous_metrics = history[-1]

        return {
            "compliance_trend": self._calculate_trend(
                current_metrics.compliant_requirements,
                previous_metrics.compliant_requirements,
            ),
            "risk_trend": self._calculate_trend(
                current_metrics.risk_score, previous_metrics.risk_score
            ),
            "validation_efficiency": self._analyze_validation_trends(
                current_metrics.validation_methods, previous_metrics.validation_methods
            ),
        }

    def _calculate_trend(self, current: float, previous: float) -> str:
        """Calculate trend between two values."""
        if current > previous:
            return "improving"
        elif current < previous:
            return "deteriorating"
        return "stable"

    def _analyze_validation_trends(
        self, current: Dict[str, int], previous: Dict[str, int]
    ) -> Dict[str, str]:
        """Analyze trends in validation methods."""
        return {
            method: self._calculate_trend(current[method], previous[method])
            for method in current
        }

    async def _assess_risks(self, package: CompliancePackage) -> Dict[str, Any]:
        """Assess risks for a compliance package."""
        critical_requirements = [
            req for req in package.requirements if req.severity == "critical"
        ]

        return {
            "critical_requirements": len(critical_requirements),
            "high_risk_areas": [
                {
                    "id": req.id,
                    "name": req.name,
                    "framework": req.framework.value,
                    "controls": req.controls,
                    "validation_frequency": req.validation_frequency,
                    "emergency_procedures": req.emergency_procedures,
                }
                for req in critical_requirements
            ],
            "risk_mitigation": await self._generate_risk_mitigation(
                critical_requirements
            ),
        }

    async def _generate_risk_mitigation(
        self, requirements: List[Any]
    ) -> List[Dict[str, Any]]:
        """Generate risk mitigation strategies."""
        return [
            {
                "requirement_id": req.id,
                "mitigation_strategy": self._get_mitigation_strategy(req),
                "priority": "high" if req.severity == "critical" else "medium",
                "timeline": (
                    "immediate" if req.severity == "critical" else "within_30_days"
                ),
            }
            for req in requirements
        ]

    def _get_mitigation_strategy(self, requirement: Any) -> str:
        """Get appropriate mitigation strategy for a requirement."""
        if requirement.validation_method == "manual":
            return "Implement automated validation"
        elif requirement.validation_frequency == "annually":
            return "Increase validation frequency"
        elif not requirement.emergency_procedures:
            return "Develop emergency procedures"
        return "Enhance existing controls"

    async def _generate_recommendations(
        self, package: CompliancePackage, metrics: ReportMetrics
    ) -> List[Dict[str, Any]]:
        """Generate recommendations for improvement."""
        recommendations = []

        # Analyze validation methods
        if (
            metrics.validation_methods["manual"]
            > metrics.validation_methods["automated"]
        ):
            recommendations.append(
                {
                    "type": "validation_efficiency",
                    "description": "Increase automated validation to improve efficiency",
                    "priority": "high",
                    "impact": "significant",
                }
            )

        # Check compliance status
        if metrics.non_compliant > 0:
            recommendations.append(
                {
                    "type": "compliance_gap",
                    "description": "Address non-compliant requirements",
                    "priority": "critical",
                    "impact": "high",
                }
            )

        return recommendations

    async def _generate_action_items(
        self, package: CompliancePackage, metrics: ReportMetrics
    ) -> List[Dict[str, Any]]:
        """Generate specific action items."""
        action_items = []

        for req in package.requirements:
            if req.status != ComplianceStatus.COMPLIANT:
                action_items.append(
                    {
                        "requirement_id": req.id,
                        "action": f"Address {req.status.value} status",
                        "priority": "high" if req.severity == "critical" else "medium",
                        "due_date": (
                            datetime.utcnow() + timedelta(days=30)
                        ).isoformat(),
                    }
                )

        return action_items

    def _calculate_compliance_score(self, metrics: ReportMetrics) -> float:
        """Calculate overall compliance score."""
        if metrics.total_requirements == 0:
            return 0.0

        compliant_weight = 1.0
        partial_weight = 0.7
        non_compliant_weight = 0.0

        total_score = (
            metrics.compliant_requirements * compliant_weight
            + metrics.partially_compliant * partial_weight
            + metrics.non_compliant * non_compliant_weight
        )

        return total_score / metrics.total_requirements

    async def _analyze_framework_coverage(
        self, package: CompliancePackage
    ) -> Dict[str, Any]:
        """Analyze coverage of compliance frameworks."""
        framework_counts = {}
        for framework in package.frameworks:
            framework_counts[framework.value] = len(
                [req for req in package.requirements if req.framework == framework]
            )

        return {
            "framework_distribution": framework_counts,
            "coverage_gaps": self._identify_coverage_gaps(package),
        }

    def _identify_coverage_gaps(
        self, package: CompliancePackage
    ) -> List[Dict[str, Any]]:
        """Identify gaps in framework coverage."""
        gaps = []
        for framework in package.frameworks:
            requirements = [
                req for req in package.requirements if req.framework == framework
            ]
            if not requirements:
                gaps.append(
                    {
                        "framework": framework.value,
                        "severity": "high",
                        "recommendation": f"Add requirements for {framework.value} framework",
                    }
                )
        return gaps

    async def _analyze_validation_efficiency(
        self, package: CompliancePackage
    ) -> Dict[str, Any]:
        """Analyze efficiency of validation methods."""
        efficiency_metrics = {
            "automated": {"count": 0, "average_frequency": 0},
            "manual": {"count": 0, "average_frequency": 0},
            "hybrid": {"count": 0, "average_frequency": 0},
        }

        frequency_values = {
            "hourly": 1,
            "daily": 24,
            "weekly": 168,
            "monthly": 720,
            "quarterly": 2160,
            "annually": 8760,
        }

        for req in package.requirements:
            method = req.validation_method
            efficiency_metrics[method]["count"] += 1
            efficiency_metrics[method]["average_frequency"] += frequency_values.get(
                req.validation_frequency, 0
            )

        for method in efficiency_metrics:
            if efficiency_metrics[method]["count"] > 0:
                efficiency_metrics[method]["average_frequency"] /= efficiency_metrics[
                    method
                ]["count"]

        return efficiency_metrics

    async def _assess_emergency_preparedness(
        self, package: CompliancePackage
    ) -> Dict[str, Any]:
        """Assess emergency preparedness."""
        requirements_with_emergency = [
            req for req in package.requirements if req.emergency_procedures
        ]

        return {
            "total_requirements": len(package.requirements),
            "requirements_with_emergency_procedures": len(requirements_with_emergency),
            "coverage_percentage": (
                len(requirements_with_emergency) / len(package.requirements) * 100
                if package.requirements
                else 0
            ),
            "critical_requirements_coverage": len(
                [
                    req
                    for req in requirements_with_emergency
                    if req.severity == "critical"
                ]
            ),
        }

    def _update_metrics_history(
        self, package_name: str, metrics: ReportMetrics
    ) -> None:
        """Update metrics history for trend analysis."""
        if package_name not in self.metrics_history:
            self.metrics_history[package_name] = []

        self.metrics_history[package_name].append(metrics)

        # Keep only last 12 months of history
        if len(self.metrics_history[package_name]) > 12:
            self.metrics_history[package_name] = self.metrics_history[package_name][
                -12:
            ]
