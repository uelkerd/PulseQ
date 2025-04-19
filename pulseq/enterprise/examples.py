"""
Example usage patterns for PulseQ monetization scenarios.
"""
from datetime import datetime, timedelta
from typing import Dict, Any
import asyncio
from .billing import BillingManager, ContractType, BillingModel
from .compliance import ComplianceTracker, ComplianceFramework
from .grants import GrantManager, GrantType
from .specialized_models import SpecializedContractManager, IntelligenceLevel
from .compliance_packages import (
    SpaceCompliancePackage,
    QuantumComputingPackage,
    DefenseIndustryPackage,
    ResearchEthicsPackage,
    InternationalTradePackage,
    CriticalInfrastructurePackage
)
from .reporting import ComplianceReporter
from .integrations import ComplianceIntegrator

class PulseQExamples:
    """Example usage patterns for different monetization scenarios."""
    
    @staticmethod
    async def military_contract_example() -> Dict[str, Any]:
        """Example of a military contract setup."""
        billing = BillingManager()
        compliance = ComplianceTracker()
        specialized = SpecializedContractManager()
        
        # Create military contract
        contract = await specialized.create_intelligence_contract(
            agency="US Department of Defense",
            classification=IntelligenceLevel.SECRET,
            compartments=["SCI", "SAP"],
            security_requirements={
                "encryption": "AES-256",
                "access_control": "RBAC",
                "audit_logging": "required"
            },
            access_controls={
                "multi_factor_auth": True,
                "biometric_verification": True
            },
            audit_requirements={
                "retention_period": "90 days",
                "real_time_monitoring": True
            },
            duration_months=12
        )
        
        # Set up compliance monitoring
        await compliance.add_requirement(
            framework=ComplianceFramework.STIG,
            name="Security Technical Implementation Guide",
            description="DoD security requirements",
            severity="high",
            controls=["AC-1", "AC-2", "AC-3"]
        )
        
        # Create billing setup
        subscription = await billing.create_subscription(
            customer_id="DOD-001",
            price_id="military_enterprise",
            billing_model=BillingModel.MILITARY_CONTRACT,
            contract_type=ContractType.MILITARY
        )
        
        return {
            "contract": contract,
            "compliance": await compliance.get_compliance_dashboard(ContractType.MILITARY),
            "subscription": subscription
        }
        
    @staticmethod
    async def research_grant_example() -> Dict[str, Any]:
        """Example of a research grant setup."""
        grants = GrantManager()
        billing = BillingManager()
        
        # Create grant proposal
        grant = await grants.create_grant_proposal(
            grant_type=GrantType.RESEARCH,
            title="Quantum Computing Research",
            description="Advanced quantum computing research project",
            principal_investigator="Dr. Jane Smith",
            institution="MIT",
            budget=1000000,
            duration_months=24,
            requirements={
                "publications": 5,
                "milestones": [
                    "Initial research phase",
                    "Prototype development",
                    "Testing and validation"
                ]
            }
        )
        
        # Set up billing
        subscription = await billing.create_subscription(
            customer_id="MIT-001",
            price_id="research_enterprise",
            billing_model=BillingModel.RESEARCH_GRANT,
            contract_type=ContractType.RESEARCH
        )
        
        return {
            "grant": grant,
            "subscription": subscription
        }
        
    @staticmethod
    async def international_collaboration_example() -> Dict[str, Any]:
        """Example of an international collaboration setup."""
        specialized = SpecializedContractManager()
        compliance = ComplianceTracker()
        
        # Create international agreement
        agreement = await specialized.create_international_agreement(
            agreement_type="RESEARCH_COLLABORATION",
            partner_countries=["US", "UK", "Germany", "Japan"],
            governing_law="International Research Agreement",
            dispute_resolution="Arbitration",
            export_controls=["EAR", "ITAR"],
            intellectual_property={
                "ownership": "joint",
                "publication_rights": "shared",
                "patent_rights": "negotiated"
            },
            data_sharing={
                "protocol": "secure_transfer",
                "encryption": "AES-256",
                "access_control": "role_based"
            },
            duration_months=36
        )
        
        # Set up compliance monitoring
        await compliance.add_requirement(
            framework=ComplianceFramework.GDPR,
            name="Data Protection",
            description="EU data protection requirements",
            severity="high",
            controls=["DP-1", "DP-2", "DP-3"]
        )
        
        return {
            "agreement": agreement,
            "compliance": await compliance.get_compliance_dashboard(ContractType.INTERNATIONAL)
        }
        
    @staticmethod
    async def government_contract_example() -> Dict[str, Any]:
        """Example of a government contract setup."""
        billing = BillingManager()
        compliance = ComplianceTracker()
        
        # Create government contract
        subscription = await billing.create_subscription(
            customer_id="GOV-001",
            price_id="government_enterprise",
            billing_model=BillingModel.GOVERNMENT_GRANT,
            contract_type=ContractType.GOVERNMENT
        )
        
        # Set up compliance monitoring
        await compliance.add_requirement(
            framework=ComplianceFramework.FEDRAMP,
            name="Cloud Security",
            description="Federal cloud security requirements",
            severity="high",
            controls=["CS-1", "CS-2", "CS-3"]
        )
        
        return {
            "subscription": subscription,
            "compliance": await compliance.get_compliance_dashboard(ContractType.GOVERNMENT)
        }
        
    @staticmethod
    async def space_research_example() -> Dict[str, Any]:
        """Example of a space research project setup."""
        grants = GrantManager()
        specialized = SpecializedContractManager()
        
        # Create space research grant
        grant = await grants.create_grant_proposal(
            grant_type=GrantType.SPACE,
            title="Mars Exploration Research",
            description="Advanced research for Mars exploration",
            principal_investigator="Dr. John Doe",
            institution="NASA",
            budget=5000000,
            duration_months=48,
            requirements={
                "publications": 10,
                "milestones": [
                    "Research phase",
                    "Prototype development",
                    "Testing phase",
                    "Deployment"
                ]
            }
        )
        
        # Create international space agreement
        agreement = await specialized.create_international_agreement(
            agreement_type="SPACE_COOPERATION",
            partner_countries=["US", "EU", "Japan"],
            governing_law="International Space Treaty",
            dispute_resolution="Diplomatic channels",
            export_controls=["ITAR", "EAR"],
            intellectual_property={
                "ownership": "shared",
                "publication_rights": "negotiated",
                "patent_rights": "shared"
            },
            data_sharing={
                "protocol": "secure_space_network",
                "encryption": "quantum_resistant",
                "access_control": "multi_level"
            },
            duration_months=60
        )
        
        return {
            "grant": grant,
            "agreement": agreement
        }

class ComplianceExamples:
    """Example usage patterns for compliance packages and services."""
    
    @staticmethod
    async def space_security_example() -> Dict[str, Any]:
        """Example of space security compliance implementation."""
        # Initialize space security package
        space_package = SpaceCompliancePackage()
        
        # Set up compliance monitoring
        reporter = ComplianceReporter()
        report = await reporter.generate_comprehensive_report(
            space_package,
            timeframe=timedelta(days=30)
        )
        
        # Set up external system integration
        integrator = ComplianceIntegrator()
        await integrator.register_system({
            "name": "SpaceCompliance",
            "api_endpoint": "https://api.spacecompliance.com",
            "api_key": "space_api_key",
            "supported_frameworks": space_package.frameworks,
            "sync_frequency": "daily"
        })
        
        return {
            "package": space_package.get_package_details(),
            "report": report,
            "integration_status": await integrator.get_system_status("SpaceCompliance")
        }
        
    @staticmethod
    async def quantum_security_example() -> Dict[str, Any]:
        """Example of quantum computing security implementation."""
        # Initialize quantum security package
        quantum_package = QuantumComputingPackage()
        
        # Set up real-time monitoring
        reporter = ComplianceReporter()
        report = await reporter.generate_comprehensive_report(
            quantum_package,
            timeframe=timedelta(days=7)  # More frequent monitoring for quantum systems
        )
        
        # Set up emergency response services
        emergency_procedures = {
            "system_compromise": "immediate_isolation",
            "data_breach": "quantum_state_preservation"
        }
        
        return {
            "package": quantum_package.get_package_details(),
            "report": report,
            "emergency_procedures": emergency_procedures
        }
        
    @staticmethod
    async def defense_industry_example() -> Dict[str, Any]:
        """Example of defense industry compliance implementation."""
        # Initialize defense industry package
        defense_package = DefenseIndustryPackage()
        
        # Set up automated validation
        reporter = ComplianceReporter()
        report = await reporter.generate_comprehensive_report(
            defense_package,
            timeframe=timedelta(days=14)
        )
        
        # Set up exception management
        exception_process = {
            "request_submission": "formal_request",
            "review_process": "security_committee",
            "approval_authority": "chief_security_officer",
            "documentation": "exception_log"
        }
        
        return {
            "package": defense_package.get_package_details(),
            "report": report,
            "exception_process": exception_process
        }
        
    @staticmethod
    async def research_ethics_example() -> Dict[str, Any]:
        """Example of research ethics compliance implementation."""
        # Initialize research ethics package
        research_package = ResearchEthicsPackage()
        
        # Set up compliance monitoring
        reporter = ComplianceReporter()
        report = await reporter.generate_comprehensive_report(
            research_package,
            timeframe=timedelta(days=90)  # Quarterly reporting
        )
        
        # Set up training program
        training_program = {
            "modules": [
                "research_integrity",
                "data_ethics",
                "ai_research_ethics",
                "conflict_of_interest"
            ],
            "certification": {
                "name": "Certified Research Ethics Professional",
                "validity": "2 years",
                "renewal": "continuing_education"
            }
        }
        
        return {
            "package": research_package.get_package_details(),
            "report": report,
            "training_program": training_program
        }
        
    @staticmethod
    async def international_trade_example() -> Dict[str, Any]:
        """Example of international trade compliance implementation."""
        # Initialize international trade package
        trade_package = InternationalTradePackage()
        
        # Set up compliance monitoring
        reporter = ComplianceReporter()
        report = await reporter.generate_comprehensive_report(
            trade_package,
            timeframe=timedelta(days=30)
        )
        
        # Set up consulting services
        consulting_services = {
            "gap_analysis": {
                "scope": "trade_compliance",
                "deliverables": ["gap_report", "remediation_plan"]
            },
            "implementation": {
                "phases": ["assessment", "planning", "implementation", "validation"],
                "timeline": "3-6 months"
            }
        }
        
        return {
            "package": trade_package.get_package_details(),
            "report": report,
            "consulting_services": consulting_services
        }
        
    @staticmethod
    async def critical_infrastructure_example() -> Dict[str, Any]:
        """Example of critical infrastructure compliance implementation."""
        # Initialize critical infrastructure package
        infra_package = CriticalInfrastructurePackage()
        
        # Set up real-time monitoring
        reporter = ComplianceReporter()
        report = await reporter.generate_comprehensive_report(
            infra_package,
            timeframe=timedelta(days=1)  # Daily monitoring for critical systems
        )
        
        # Set up emergency response services
        emergency_services = {
            "incident_response": {
                "team": "24/7_response_team",
                "escalation": "automated_escalation",
                "recovery": "automated_recovery"
            },
            "monitoring": {
                "frequency": "real-time",
                "alerts": "automated_alerts",
                "reporting": "automated_reporting"
            }
        }
        
        return {
            "package": infra_package.get_package_details(),
            "report": report,
            "emergency_services": emergency_services
        } 