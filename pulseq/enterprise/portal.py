"""
Customer Portal Interface

Provides a web interface for customers to manage their subscriptions,
licenses, and usage.
"""

from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from .billing import BillingManager
from .license import LicenseManager
from .usage import UsageTracker

app = FastAPI(title="PulseQ Enterprise Portal")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize managers
billing_manager = BillingManager()
license_manager = LicenseManager()
usage_tracker = UsageTracker()
portal_manager = PortalManager(billing_manager, license_manager, usage_tracker)


async def get_current_customer(request: Request) -> str:
    """Get current customer ID from request"""
    # In a real implementation, this would validate the token
    # and return the associated customer ID
    return request.headers.get("X-Customer-ID")


@app.get("/dashboard")
async def get_dashboard(customer_id: str = Depends(get_current_customer)):
    """Get customer dashboard data"""
    return await portal_manager.get_customer_dashboard(customer_id)


@app.post("/subscription/update")
async def update_subscription(
    new_plan: str, customer_id: str = Depends(get_current_customer)
):
    """Update customer subscription plan"""
    return await portal_manager.update_subscription(customer_id, new_plan)


@app.get("/billing/history")
async def get_billing_history(customer_id: str = Depends(get_current_customer)):
    """Get customer billing history"""
    return await portal_manager.get_billing_history(customer_id)


@app.get("/usage/report")
async def get_usage_report(
    start_date: str, end_date: str, customer_id: str = Depends(get_current_customer)
):
    """Generate usage report for customer"""
    return await portal_manager.get_usage_report(customer_id, start_date, end_date)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500, content={"message": "An internal server error occurred"}
    )


class PortalManager:
    def __init__(
        self,
        billing_manager: BillingManager,
        license_manager: LicenseManager,
        usage_tracker: UsageTracker,
    ):
        self.billing = billing_manager
        self.license = license_manager
        self.usage = usage_tracker

    async def get_customer_dashboard(self, customer_id: str) -> Dict[str, Any]:
        """Get customer dashboard data"""
        try:
            # Get subscription status
            subscription = self.billing.stripe.Subscription.list(
                customer=customer_id, limit=1
            ).data[0]

            # Get license info
            license_data = self.license.get_license_data(customer_id)

            # Get usage data
            usage_data = self.usage.get_usage(customer_id)

            return {
                "subscription": {
                    "status": subscription.status,
                    "current_period_end": subscription.current_period_end,
                    "plan": subscription.plan.nickname,
                },
                "license": license_data,
                "usage": usage_data,
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def update_subscription(
        self, customer_id: str, new_plan: str
    ) -> Dict[str, Any]:
        """Update customer subscription plan"""
        try:
            # Get current subscription
            subscription = self.billing.stripe.Subscription.list(
                customer=customer_id, limit=1
            ).data[0]

            # Update subscription
            updated = self.billing.update_subscription(subscription.id, new_plan)

            # Update license features
            self.license.update_license_features(
                customer_id, self._get_features_for_plan(new_plan)
            )

            return {"status": "success", "subscription": updated}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_billing_history(self, customer_id: str) -> Dict[str, Any]:
        """Get customer billing history"""
        try:
            invoices = self.billing.stripe.Invoice.list(customer=customer_id)
            return {"invoices": invoices.data}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_usage_report(
        self, customer_id: str, start_date: str, end_date: str
    ) -> Dict[str, Any]:
        """Generate usage report for customer"""
        try:
            report = self.usage.generate_report(customer_id, start_date, end_date)
            return {"report": report}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def _get_features_for_plan(self, plan: str) -> Dict[str, Any]:
        """Get features available for a specific plan"""
        plans = {
            "starter": {
                "max_users": 5,
                "max_tests": 100,
                "features": ["basic_analytics", "email_support"],
            },
            "professional": {
                "max_users": 20,
                "max_tests": 500,
                "features": ["advanced_analytics", "priority_support", "api_access"],
            },
            "enterprise": {
                "max_users": 100,
                "max_tests": 2000,
                "features": [
                    "all_features",
                    "dedicated_support",
                    "custom_integrations",
                ],
            },
        }
        return plans.get(plan, {})
