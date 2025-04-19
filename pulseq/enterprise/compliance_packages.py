"""
Specialized compliance packages for different industries.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from .billing import BillingModel, ContractType
from .compliance import ComplianceFramework, ComplianceRequirement, ComplianceStatus


class CompliancePackage:
    """Base class for compliance packages."""

    def __init__(
        self, name: str, description: str, frameworks: List[ComplianceFramework]
    ):
        self.name = name
        self.description = description
        self.frameworks = frameworks
        self.requirements: List[ComplianceRequirement] = []

    def get_package_details(self) -> Dict[str, Any]:
        """Get package details."""
        return {
            "name": self.name,
            "description": self.description,
            "frameworks": [f.value for f in self.frameworks],
            "requirements": len(self.requirements),
        }


class MilitaryCompliancePackage(CompliancePackage):
    """Military-grade compliance package."""

    def __init__(self):
        super().__init__(
            name="Military-Grade Security",
            description="Comprehensive security compliance for military applications",
            frameworks=[
                ComplianceFramework.STIG,
                ComplianceFramework.NIST,
                ComplianceFramework.ITAR,
                ComplianceFramework.DEFENSE_INDUSTRY,
                ComplianceFramework.CYBER_RANGE,
                ComplianceFramework.CRITICAL_INFRA,
                ComplianceFramework.QUANTUM_SAFE,
            ],
        )
        self._initialize_requirements()

    def _initialize_requirements(self):
        """Initialize military-specific requirements."""
        self.requirements = [
            ComplianceRequirement(
                id="MIL-001",
                framework=ComplianceFramework.STIG,
                name="System Security Plan",
                description="Comprehensive security plan for military systems",
                severity="critical",
                controls=["AC-1", "AC-2", "AC-3"],
                documentation_required=True,
                validation_frequency="monthly",
                validation_method="hybrid",
                evidence_requirements=[
                    "security_plan",
                    "risk_assessment",
                    "incident_response_plan",
                ],
                exceptions_allowed=False,
                emergency_procedures={
                    "incident_response": "immediate_notification",
                    "data_breach": "isolate_and_contain",
                },
            ),
            ComplianceRequirement(
                id="MIL-002",
                framework=ComplianceFramework.ITAR,
                name="Export Controls",
                description="ITAR compliance for military technology",
                severity="critical",
                controls=["EC-1", "EC-2", "EC-3"],
                documentation_required=True,
                validation_frequency="quarterly",
                validation_method="manual",
                evidence_requirements=[
                    "export_licenses",
                    "training_records",
                    "access_logs",
                ],
                exceptions_allowed=False,
            ),
            ComplianceRequirement(
                id="MIL-003",
                framework=ComplianceFramework.QUANTUM_SAFE,
                name="Quantum-Resistant Cryptography",
                description="Post-quantum cryptography implementation",
                severity="high",
                controls=["CR-1", "CR-2", "CR-3"],
                documentation_required=True,
                validation_frequency="annually",
                validation_method="automated",
                evidence_requirements=[
                    "crypto_implementation",
                    "key_management",
                    "algorithm_certification",
                ],
            ),
        ]


class SpaceCompliancePackage(CompliancePackage):
    """Space industry compliance package."""

    def __init__(self):
        super().__init__(
            name="Space Industry Security",
            description="Compliance package for space systems and operations",
            frameworks=[
                ComplianceFramework.SPACE_SECURITY,
                ComplianceFramework.SPACE_TRAFFIC,
                ComplianceFramework.QUANTUM_SAFE,
                ComplianceFramework.INTERNATIONAL_TRADE,
                ComplianceFramework.CRITICAL_INFRA,
            ],
        )
        self._initialize_requirements()

    def _initialize_requirements(self):
        """Initialize space-specific requirements."""
        self.requirements = [
            ComplianceRequirement(
                id="SPC-001",
                framework=ComplianceFramework.SPACE_SECURITY,
                name="Space System Security",
                description="Security requirements for space systems",
                severity="critical",
                controls=["SS-1", "SS-2", "SS-3"],
                documentation_required=True,
                validation_frequency="monthly",
                validation_method="hybrid",
                evidence_requirements=[
                    "system_architecture",
                    "security_controls",
                    "testing_results",
                ],
                exceptions_allowed=False,
                emergency_procedures={
                    "system_compromise": "emergency_shutdown",
                    "data_breach": "isolate_and_report",
                },
            ),
            ComplianceRequirement(
                id="SPC-002",
                framework=ComplianceFramework.SPACE_TRAFFIC,
                name="Space Traffic Management",
                description="Compliance with space traffic management regulations",
                severity="high",
                controls=["TM-1", "TM-2", "TM-3"],
                documentation_required=True,
                validation_frequency="daily",
                validation_method="automated",
                evidence_requirements=[
                    "traffic_data",
                    "collision_avoidance",
                    "coordination_records",
                ],
            ),
        ]


class QuantumComputingPackage(CompliancePackage):
    """Quantum computing compliance package."""

    def __init__(self):
        super().__init__(
            name="Quantum Computing Security",
            description="Compliance package for quantum computing systems",
            frameworks=[
                ComplianceFramework.QUANTUM_COMPUTING,
                ComplianceFramework.QUANTUM_SAFE,
                ComplianceFramework.RESEARCH_ETHICS,
                ComplianceFramework.INTERNATIONAL_TRADE,
            ],
        )
        self._initialize_requirements()

    def _initialize_requirements(self):
        """Initialize quantum computing-specific requirements."""
        self.requirements = [
            ComplianceRequirement(
                id="QC-001",
                framework=ComplianceFramework.QUANTUM_COMPUTING,
                name="Quantum System Security",
                description="Security requirements for quantum computing systems",
                severity="critical",
                controls=["QS-1", "QS-2", "QS-3"],
                documentation_required=True,
                validation_frequency="weekly",
                validation_method="hybrid",
                evidence_requirements=[
                    "system_configuration",
                    "security_measures",
                    "testing_protocols",
                ],
                exceptions_allowed=False,
                emergency_procedures={
                    "system_compromise": "immediate_isolation",
                    "data_breach": "quantum_state_preservation",
                },
            ),
            ComplianceRequirement(
                id="QC-002",
                framework=ComplianceFramework.RESEARCH_ETHICS,
                name="Quantum Research Ethics",
                description="Ethical guidelines for quantum computing research",
                severity="high",
                controls=["RE-1", "RE-2", "RE-3"],
                documentation_required=True,
                validation_frequency="quarterly",
                validation_method="manual",
                evidence_requirements=[
                    "ethics_review",
                    "research_protocols",
                    "publication_guidelines",
                ],
            ),
        ]


class AIEthicsPackage(CompliancePackage):
    """AI ethics compliance package."""

    def __init__(self):
        super().__init__(
            name="AI Ethics Compliance",
            description="Compliance package for AI system ethics",
            frameworks=[
                ComplianceFramework.AI_ETHICS,
                ComplianceFramework.RESEARCH_ETHICS,
                ComplianceFramework.GDPR,
                ComplianceFramework.QUANTUM_SAFE,
            ],
        )
        self._initialize_requirements()

    def _initialize_requirements(self):
        """Initialize AI ethics-specific requirements."""
        self.requirements = [
            ComplianceRequirement(
                id="AI-001",
                framework=ComplianceFramework.AI_ETHICS,
                name="AI System Ethics",
                description="Ethical requirements for AI systems",
                severity="high",
                controls=["AE-1", "AE-2", "AE-3"],
                documentation_required=True,
                validation_frequency="monthly",
                validation_method="hybrid",
                evidence_requirements=[
                    "ethics_assessment",
                    "bias_mitigation",
                    "transparency_documentation",
                ],
                exceptions_allowed=False,
                emergency_procedures={
                    "ethical_breach": "system_override",
                    "bias_detection": "immediate_correction",
                },
            ),
            ComplianceRequirement(
                id="AI-002",
                framework=ComplianceFramework.GDPR,
                name="AI Data Privacy",
                description="GDPR compliance for AI systems",
                severity="critical",
                controls=["DP-1", "DP-2", "DP-3"],
                documentation_required=True,
                validation_frequency="quarterly",
                validation_method="automated",
                evidence_requirements=[
                    "privacy_impact_assessment",
                    "data_processing_records",
                    "consent_management",
                ],
            ),
        ]


class DefenseIndustryPackage(CompliancePackage):
    """Defense industry compliance package."""

    def __init__(self):
        super().__init__(
            name="Defense Industry Security",
            description="Compliance package for defense industry applications",
            frameworks=[
                ComplianceFramework.DEFENSE_INDUSTRY,
                ComplianceFramework.ITAR,
                ComplianceFramework.EAR,
                ComplianceFramework.CYBER_RANGE,
                ComplianceFramework.CRITICAL_INFRA,
                ComplianceFramework.QUANTUM_SAFE,
            ],
        )
        self._initialize_requirements()

    def _initialize_requirements(self):
        """Initialize defense industry-specific requirements."""
        self.requirements = [
            ComplianceRequirement(
                id="DEF-001",
                framework=ComplianceFramework.DEFENSE_INDUSTRY,
                name="Defense Industry Security",
                description="Security requirements for defense industry systems",
                severity="critical",
                controls=["DI-1", "DI-2", "DI-3"],
                documentation_required=True,
                validation_frequency="monthly",
                validation_method="hybrid",
                evidence_requirements=[
                    "security_plan",
                    "risk_assessment",
                    "incident_response_plan",
                ],
                exceptions_allowed=False,
                emergency_procedures={
                    "incident_response": "immediate_notification",
                    "data_breach": "isolate_and_contain",
                },
            ),
            ComplianceRequirement(
                id="DEF-002",
                framework=ComplianceFramework.ITAR,
                name="Export Controls",
                description="ITAR compliance for defense technology",
                severity="critical",
                controls=["EC-1", "EC-2", "EC-3"],
                documentation_required=True,
                validation_frequency="quarterly",
                validation_method="manual",
                evidence_requirements=[
                    "export_licenses",
                    "training_records",
                    "access_logs",
                ],
                exceptions_allowed=False,
            ),
        ]


class ResearchEthicsPackage(CompliancePackage):
    """Research ethics compliance package."""

    def __init__(self):
        super().__init__(
            name="Research Ethics Compliance",
            description="Compliance package for research ethics and integrity",
            frameworks=[
                ComplianceFramework.RESEARCH_ETHICS,
                ComplianceFramework.AI_ETHICS,
                ComplianceFramework.GDPR,
                ComplianceFramework.QUANTUM_SAFE,
                ComplianceFramework.QUANTUM_COMPUTING,
            ],
        )
        self._initialize_requirements()

    def _initialize_requirements(self):
        """Initialize research ethics-specific requirements."""
        self.requirements = [
            ComplianceRequirement(
                id="RES-001",
                framework=ComplianceFramework.RESEARCH_ETHICS,
                name="Research Integrity",
                description="Ethical requirements for research activities",
                severity="high",
                controls=["RI-1", "RI-2", "RI-3"],
                documentation_required=True,
                validation_frequency="quarterly",
                validation_method="hybrid",
                evidence_requirements=[
                    "ethics_approval",
                    "research_protocols",
                    "data_management_plan",
                ],
                exceptions_allowed=False,
                emergency_procedures={
                    "ethical_breach": "immediate_reporting",
                    "data_misuse": "investigation_and_containment",
                },
            ),
            ComplianceRequirement(
                id="RES-002",
                framework=ComplianceFramework.AI_ETHICS,
                name="AI Research Ethics",
                description="Ethical guidelines for AI research",
                severity="high",
                controls=["AIE-1", "AIE-2", "AIE-3"],
                documentation_required=True,
                validation_frequency="monthly",
                validation_method="automated",
                evidence_requirements=[
                    "bias_assessment",
                    "transparency_documentation",
                    "impact_analysis",
                ],
            ),
        ]


class InternationalTradePackage(CompliancePackage):
    """International trade compliance package."""

    def __init__(self):
        super().__init__(
            name="International Trade Compliance",
            description="Compliance package for international trade and export",
            frameworks=[
                ComplianceFramework.INTERNATIONAL_TRADE,
                ComplianceFramework.ITAR,
                ComplianceFramework.EAR,
                ComplianceFramework.GDPR,
                ComplianceFramework.QUANTUM_SAFE,
            ],
        )
        self._initialize_requirements()

    def _initialize_requirements(self):
        """Initialize international trade-specific requirements."""
        self.requirements = [
            ComplianceRequirement(
                id="IT-001",
                framework=ComplianceFramework.INTERNATIONAL_TRADE,
                name="Trade Compliance",
                description="Compliance with international trade regulations",
                severity="critical",
                controls=["TC-1", "TC-2", "TC-3"],
                documentation_required=True,
                validation_frequency="monthly",
                validation_method="hybrid",
                evidence_requirements=[
                    "export_licenses",
                    "trade_agreements",
                    "compliance_records",
                ],
                exceptions_allowed=False,
                emergency_procedures={
                    "compliance_breach": "immediate_reporting",
                    "export_violation": "investigation_and_containment",
                },
            ),
            ComplianceRequirement(
                id="IT-002",
                framework=ComplianceFramework.GDPR,
                name="Data Protection",
                description="GDPR compliance for international data transfers",
                severity="high",
                controls=["DP-1", "DP-2", "DP-3"],
                documentation_required=True,
                validation_frequency="quarterly",
                validation_method="automated",
                evidence_requirements=[
                    "data_processing_agreements",
                    "transfer_mechanisms",
                    "privacy_impact_assessments",
                ],
            ),
        ]


class CriticalInfrastructurePackage(CompliancePackage):
    """Critical infrastructure compliance package."""

    def __init__(self):
        super().__init__(
            name="Critical Infrastructure Security",
            description="Compliance package for critical infrastructure protection",
            frameworks=[
                ComplianceFramework.CRITICAL_INFRA,
                ComplianceFramework.CYBER_RANGE,
                ComplianceFramework.QUANTUM_SAFE,
                ComplianceFramework.SPACE_SECURITY,
                ComplianceFramework.SPACE_TRAFFIC,
            ],
        )
        self._initialize_requirements()

    def _initialize_requirements(self):
        """Initialize critical infrastructure-specific requirements."""
        self.requirements = [
            ComplianceRequirement(
                id="CI-001",
                framework=ComplianceFramework.CRITICAL_INFRA,
                name="Infrastructure Protection",
                description="Security requirements for critical infrastructure",
                severity="critical",
                controls=["IP-1", "IP-2", "IP-3"],
                documentation_required=True,
                validation_frequency="daily",
                validation_method="hybrid",
                evidence_requirements=[
                    "security_plan",
                    "risk_assessment",
                    "incident_response_plan",
                ],
                exceptions_allowed=False,
                emergency_procedures={
                    "system_compromise": "immediate_isolation",
                    "service_disruption": "failover_and_recovery",
                },
            ),
            ComplianceRequirement(
                id="CI-002",
                framework=ComplianceFramework.CYBER_RANGE,
                name="Cyber Resilience",
                description="Cyber resilience requirements for critical systems",
                severity="critical",
                controls=["CR-1", "CR-2", "CR-3"],
                documentation_required=True,
                validation_frequency="weekly",
                validation_method="automated",
                evidence_requirements=[
                    "testing_results",
                    "recovery_plans",
                    "resilience_metrics",
                ],
            ),
        ]


def get_compliance_package(contract_type: ContractType) -> CompliancePackage:
    """Get appropriate compliance package based on contract type."""
    packages = {
        ContractType.MILITARY: MilitaryCompliancePackage(),
        ContractType.SPACE: SpaceCompliancePackage(),
        ContractType.QUANTUM: QuantumComputingPackage(),
        ContractType.AI: AIEthicsPackage(),
        ContractType.DEFENSE: DefenseIndustryPackage(),
        ContractType.RESEARCH: ResearchEthicsPackage(),
        ContractType.INTERNATIONAL: InternationalTradePackage(),
        ContractType.CRITICAL_INFRA: CriticalInfrastructurePackage(),
    }
    return packages.get(
        contract_type, CompliancePackage("Basic", "Standard compliance package", [])
    )
