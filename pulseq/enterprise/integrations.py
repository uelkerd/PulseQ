"""
Integration with external compliance systems.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import logging
import aiohttp
from dataclasses import dataclass
from .compliance import ComplianceFramework, ComplianceRequirement
from .compliance_packages import CompliancePackage

@dataclass
class ExternalSystem:
    """External compliance system configuration."""
    name: str
    api_endpoint: str
    api_key: str
    supported_frameworks: List[ComplianceFramework]
    sync_frequency: str
    last_sync: Optional[datetime] = None

class ComplianceIntegrator:
    """Manages integration with external compliance systems."""
    
    def __init__(self):
        """Initialize compliance integrator."""
        self.logger = logging.getLogger('compliance_integrator')
        self.systems: Dict[str, ExternalSystem] = {}
        self.sync_tasks: Dict[str, asyncio.Task] = {}
        
    async def register_system(self, system: ExternalSystem) -> None:
        """Register a new external compliance system."""
        self.systems[system.name] = system
        await self._start_sync_task(system)
        
    async def _start_sync_task(self, system: ExternalSystem) -> None:
        """Start synchronization task for a system."""
        if system.name in self.sync_tasks:
            self.sync_tasks[system.name].cancel()
            
        self.sync_tasks[system.name] = asyncio.create_task(
            self._sync_system(system)
        )
        
    async def _sync_system(self, system: ExternalSystem) -> None:
        """Synchronize with external system."""
        while True:
            try:
                await self._perform_sync(system)
                system.last_sync = datetime.utcnow()
                
                # Wait before next sync based on frequency
                wait_time = self._get_sync_wait_time(system.sync_frequency)
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                self.logger.error(f"Sync error for {system.name}: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
                
    def _get_sync_wait_time(self, frequency: str) -> int:
        """Get wait time in seconds based on sync frequency."""
        frequencies = {
            "hourly": 3600,
            "daily": 86400,
            "weekly": 604800,
            "monthly": 2592000
        }
        return frequencies.get(frequency.lower(), 3600)  # Default to hourly
                
    async def _perform_sync(self, system: ExternalSystem) -> None:
        """Perform synchronization with external system."""
        async with aiohttp.ClientSession() as session:
            # Get current compliance status
            async with session.get(
                f"{system.api_endpoint}/compliance/status",
                headers={"Authorization": f"Bearer {system.api_key}"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    await self._process_sync_data(system, data)
                else:
                    raise Exception(f"Failed to sync with {system.name}: {response.status}")
                    
    async def _process_sync_data(self, system: ExternalSystem,
                               data: Dict[str, Any]) -> None:
        """Process synchronization data."""
        # Implementation would process and store sync data
        self.logger.info(f"Processed sync data from {system.name}")
        
    async def sync_package(self, package: CompliancePackage) -> None:
        """Synchronize a compliance package with external systems."""
        relevant_systems = [
            system for system in self.systems.values()
            if any(framework in system.supported_frameworks
                  for framework in package.frameworks)
        ]
        
        for system in relevant_systems:
            try:
                await self._sync_package_with_system(package, system)
            except Exception as e:
                self.logger.error(
                    f"Failed to sync package with {system.name}: {str(e)}"
                )
                
    async def _sync_package_with_system(self, package: CompliancePackage,
                                      system: ExternalSystem) -> None:
        """Synchronize package with specific system."""
        async with aiohttp.ClientSession() as session:
            # Prepare package data
            package_data = {
                "name": package.name,
                "frameworks": [f.value for f in package.frameworks],
                "requirements": [
                    {
                        "id": req.id,
                        "framework": req.framework.value,
                        "name": req.name,
                        "status": req.status.value,
                        "severity": req.severity,
                        "controls": req.controls,
                        "validation_method": req.validation_method,
                        "validation_frequency": req.validation_frequency
                    }
                    for req in package.requirements
                ]
            }
            
            # Send package data
            async with session.post(
                f"{system.api_endpoint}/compliance/packages",
                headers={"Authorization": f"Bearer {system.api_key}"},
                json=package_data
            ) as response:
                if response.status != 200:
                    raise Exception(f"Failed to sync package: {response.status}")
                    
    async def get_system_status(self, system_name: str) -> Dict[str, Any]:
        """Get status of an external system."""
        if system_name not in self.systems:
            raise ValueError(f"System {system_name} not found")
            
        system = self.systems[system_name]
        
        return {
            "name": system.name,
            "last_sync": system.last_sync.isoformat() if system.last_sync else None,
            "sync_frequency": system.sync_frequency,
            "supported_frameworks": [
                f.value for f in system.supported_frameworks
            ],
            "sync_task_running": system.name in self.sync_tasks
        }
        
    async def validate_requirement(self, requirement: ComplianceRequirement,
                                 system_name: str) -> Dict[str, Any]:
        """Validate a requirement against external system."""
        if system_name not in self.systems:
            raise ValueError(f"System {system_name} not found")
            
        system = self.systems[system_name]
        
        if requirement.framework not in system.supported_frameworks:
            raise ValueError(
                f"Framework {requirement.framework.value} not supported by {system_name}"
            )
            
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{system.api_endpoint}/compliance/validate",
                headers={"Authorization": f"Bearer {system.api_key}"},
                json={
                    "requirement_id": requirement.id,
                    "framework": requirement.framework.value,
                    "controls": requirement.controls,
                    "validation_method": requirement.validation_method
                }
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Validation failed: {response.status}")
                    
    async def get_system_recommendations(self, package: CompliancePackage,
                                       system_name: str) -> List[Dict[str, Any]]:
        """Get recommendations from external system."""
        if system_name not in self.systems:
            raise ValueError(f"System {system_name} not found")
            
        system = self.systems[system_name]
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{system.api_endpoint}/compliance/recommendations",
                headers={"Authorization": f"Bearer {system.api_key}"},
                json={
                    "package_name": package.name,
                    "frameworks": [f.value for f in package.frameworks],
                    "requirements": [
                        {
                            "id": req.id,
                            "framework": req.framework.value,
                            "status": req.status.value,
                            "severity": req.severity
                        }
                        for req in package.requirements
                    ]
                }
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to get recommendations: {response.status}")
                    
    async def export_compliance_data(self, package: CompliancePackage,
                                   format: str = "json") -> Dict[str, Any]:
        """Export compliance data in specified format."""
        export_data = {
            "package": package.get_package_details(),
            "requirements": [
                {
                    "id": req.id,
                    "framework": req.framework.value,
                    "name": req.name,
                    "description": req.description,
                    "status": req.status.value,
                    "severity": req.severity,
                    "controls": req.controls,
                    "validation_method": req.validation_method,
                    "validation_frequency": req.validation_frequency,
                    "evidence_requirements": req.evidence_requirements,
                    "emergency_procedures": req.emergency_procedures
                }
                for req in package.requirements
            ],
            "exported_at": datetime.utcnow().isoformat(),
            "format": format
        }
        
        return export_data 