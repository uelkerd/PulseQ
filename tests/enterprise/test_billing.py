"""
Unit tests for the BillingManager class.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
import stripe
from fastapi import HTTPException

from pulseq.enterprise.billing import BillingManager


@pytest.fixture
def billing_manager():
    return BillingManager()


@pytest.fixture
def mock_stripe():
    with patch("stripe.Subscription.create") as mock_sub_create, patch(
        "stripe.Subscription.modify"
    ) as mock_sub_modify, patch("stripe.Subscription.delete") as mock_sub_delete, patch(
        "stripe.Invoice.list"
    ) as mock_invoice_list, patch(
        "stripe.Invoice.upcoming"
    ) as mock_invoice_upcoming, patch(
        "stripe.PaymentMethod.create"
    ) as mock_pm_create, patch("stripe.PaymentMethod.modify") as mock_pm_modify, patch(
        "stripe.PaymentMethod.detach"
    ) as mock_pm_detach, patch(
        "stripe.SubscriptionItem.create_usage_record"
    ) as mock_usage_record, patch(
        "stripe.SubscriptionItem.retrieve_usage_record_summary"
    ) as mock_usage_summary, patch(
        "stripe.Webhook.construct_event"
    ) as mock_webhook, patch("stripe.PaymentIntent.create") as mock_pi_create, patch(
        "stripe.PaymentIntent.confirm"
    ) as mock_pi_confirm, patch(
        "stripe.Customer.create"
    ) as mock_customer_create, patch(
        "stripe.Customer.retrieve"
    ) as mock_customer_retrieve, patch(
        "stripe.Customer.modify"
    ) as mock_customer_modify:
        yield {
            "subscription_create": mock_sub_create,
            "subscription_modify": mock_sub_modify,
            "subscription_delete": mock_sub_delete,
            "invoice_list": mock_invoice_list,
            "invoice_upcoming": mock_invoice_upcoming,
            "payment_method_create": mock_pm_create,
            "payment_method_modify": mock_pm_modify,
            "payment_method_detach": mock_pm_detach,
            "usage_record": mock_usage_record,
            "usage_summary": mock_usage_summary,
            "webhook": mock_webhook,
            "payment_intent_create": mock_pi_create,
            "payment_intent_confirm": mock_pi_confirm,
            "customer_create": mock_customer_create,
            "customer_retrieve": mock_customer_retrieve,
            "customer_modify": mock_customer_modify,
        }


@pytest.mark.asyncio
async def test_create_subscription(billing_manager, mock_stripe):
    # Setup mock
    mock_sub = MagicMock()
    mock_sub.id = "sub_test_123"
    mock_sub.status = "active"
    mock_sub.current_period_end = 1234567890
    mock_stripe["subscription_create"].return_value = mock_sub

    # Test
    result = await billing_manager.create_subscription(
        "cus_test_123", "price_test_123", "pm_test_123"
    )

    # Assert
    assert result["subscription_id"] == "sub_test_123"
    assert result["status"] == "active"
    assert result["current_period_end"] == 1234567890
    mock_stripe["subscription_create"].assert_called_once()


@pytest.mark.asyncio
async def test_report_usage(billing_manager, mock_stripe):
    # Setup mock
    mock_usage = MagicMock()
    mock_usage.id = "usage_test_123"
    mock_usage.quantity = 100
    mock_usage.timestamp = 1234567890
    mock_stripe["usage_record"].return_value = mock_usage

    # Test
    result = await billing_manager.report_usage("si_test_123", 100)

    # Assert
    assert result["usage_record_id"] == "usage_test_123"
    assert result["quantity"] == 100
    assert result["timestamp"] == 1234567890
    mock_stripe["usage_record"].assert_called_once()


@pytest.mark.asyncio
async def test_handle_webhook_success(billing_manager, mock_stripe):
    # Setup mock
    mock_event = MagicMock()
    mock_event.type = "invoice.payment_succeeded"
    mock_event.data.object = MagicMock()
    mock_event.data.object.id = "inv_test_123"
    mock_event.data.object.amount_paid = 1000
    mock_event.data.object.customer = "cus_test_123"
    mock_stripe["webhook"].return_value = mock_event

    # Test
    result = await billing_manager.handle_webhook(
        {"type": "invoice.payment_succeeded"}, "sig_test_123"
    )

    # Assert
    assert result["status"] == "success"
    assert result["event_type"] == "payment_succeeded"
    assert result["invoice_id"] == "inv_test_123"
    assert result["amount_paid"] == 1000
    assert result["customer_id"] == "cus_test_123"
    mock_stripe["webhook"].assert_called_once()


@pytest.mark.asyncio
async def test_handle_webhook_invalid_signature(billing_manager, mock_stripe):
    # Setup mock
    mock_stripe["webhook"].side_effect = stripe.error.SignatureVerificationError(
        "Invalid signature", "sig_test_123"
    )

    # Test and assert
    with pytest.raises(HTTPException) as exc_info:
        await billing_manager.handle_webhook(
            {"type": "invoice.payment_succeeded"}, "sig_test_123"
        )
    assert exc_info.value.status_code == 400
    assert "Invalid webhook signature" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_create_payment_intent(billing_manager, mock_stripe):
    # Setup mock
    mock_pi = MagicMock()
    mock_pi.id = "pi_test_123"
    mock_pi.client_secret = "pi_test_secret_123"
    mock_pi.status = "requires_payment_method"
    mock_stripe["payment_intent_create"].return_value = mock_pi

    # Test
    result = await billing_manager.create_payment_intent(
        amount=1000,
        currency="usd",
        payment_method_types=["card"],
        customer_id="cus_test_123",
    )

    # Assert
    assert result["payment_intent_id"] == "pi_test_123"
    assert result["client_secret"] == "pi_test_secret_123"
    assert result["status"] == "requires_payment_method"
    mock_stripe["payment_intent_create"].assert_called_once()


@pytest.mark.asyncio
async def test_get_usage_summary(billing_manager, mock_stripe):
    # Setup mock
    mock_summary = MagicMock()
    mock_summary.total_usage = 1000
    mock_summary.period = MagicMock()
    mock_summary.period.start = 1234567890
    mock_summary.period.end = 1234567899
    mock_stripe["usage_summary"].return_value = mock_summary

    # Test
    result = await billing_manager.get_usage_summary(
        "si_test_123", 1234567890, 1234567899
    )

    # Assert
    assert result["total_usage"] == 1000
    assert result["period_start"] == 1234567890
    assert result["period_end"] == 1234567899
    mock_stripe["usage_summary"].assert_called_once()


@pytest.mark.asyncio
async def test_prorated_subscription_upgrade(billing_manager, mock_stripe):
    # Setup mock
    mock_sub = MagicMock()
    mock_sub.id = "sub_test_123"
    mock_sub.status = "active"
    mock_sub.current_period_end = 1234567890
    mock_sub.proration_date = 1234567890
    mock_sub.proration_items = [{"amount": 500}]
    mock_stripe["subscription_modify"].return_value = mock_sub

    # Test
    result = await billing_manager.update_subscription(
        "sub_test_123", "price_test_456", prorate=True
    )

    # Assert
    assert result["subscription_id"] == "sub_test_123"
    assert result["status"] == "active"
    assert result["proration_amount"] == 500
    mock_stripe["subscription_modify"].assert_called_once()


@pytest.mark.asyncio
async def test_ach_payment_method(billing_manager, mock_stripe):
    # Setup mock
    mock_pm = MagicMock()
    mock_pm.id = "pm_test_123"
    mock_pm.type = "us_bank_account"
    mock_pm.us_bank_account = MagicMock()
    mock_pm.us_bank_account.last4 = "1234"
    mock_pm.us_bank_account.bank_name = "Test Bank"
    mock_stripe["payment_method_create"].return_value = mock_pm

    # Test
    result = await billing_manager.create_payment_method(
        type="us_bank_account",
        bank_name="Test Bank",
        account_number="00001234",
        routing_number="110000000",
    )

    # Assert
    assert result["payment_method_id"] == "pm_test_123"
    assert result["type"] == "us_bank_account"
    assert result["last4"] == "1234"
    assert result["bank_name"] == "Test Bank"
    mock_stripe["payment_method_create"].assert_called_once()


@pytest.mark.asyncio
async def test_sepa_payment_method(billing_manager, mock_stripe):
    # Setup mock
    mock_pm = MagicMock()
    mock_pm.id = "pm_test_123"
    mock_pm.type = "sepa_debit"
    mock_pm.sepa_debit = MagicMock()
    mock_pm.sepa_debit.last4 = "1234"
    mock_pm.sepa_debit.bank_code = "TESTBANK"
    mock_stripe["payment_method_create"].return_value = mock_pm

    # Test
    result = await billing_manager.create_payment_method(
        type="sepa_debit", iban="DE89370400440532013000", name="Test Account"
    )

    # Assert
    assert result["payment_method_id"] == "pm_test_123"
    assert result["type"] == "sepa_debit"
    assert result["last4"] == "1234"
    assert result["bank_code"] == "TESTBANK"
    mock_stripe["payment_method_create"].assert_called_once()


@pytest.mark.asyncio
async def test_handle_subscription_schedule_created(billing_manager, mock_stripe):
    # Setup mock
    mock_event = MagicMock()
    mock_event.type = "subscription_schedule.created"
    mock_event.data.object = MagicMock()
    mock_event.data.object.id = "sub_sched_test_123"
    mock_event.data.object.customer = "cus_test_123"
    mock_event.data.object.phases = [{"start_date": 1234567890}]
    mock_stripe["webhook"].return_value = mock_event

    # Test
    result = await billing_manager.handle_webhook(
        {"type": "subscription_schedule.created"}, "sig_test_123"
    )

    # Assert
    assert result["status"] == "success"
    assert result["event_type"] == "subscription_schedule_created"
    assert result["schedule_id"] == "sub_sched_test_123"
    assert result["customer_id"] == "cus_test_123"
    mock_stripe["webhook"].assert_called_once()


@pytest.mark.asyncio
async def test_handle_invoice_finalized(billing_manager, mock_stripe):
    # Setup mock
    mock_event = MagicMock()
    mock_event.type = "invoice.finalized"
    mock_event.data.object = MagicMock()
    mock_event.data.object.id = "inv_test_123"
    mock_event.data.object.customer = "cus_test_123"
    mock_event.data.object.amount_due = 1000
    mock_stripe["webhook"].return_value = mock_event

    # Test
    result = await billing_manager.handle_webhook(
        {"type": "invoice.finalized"}, "sig_test_123"
    )

    # Assert
    assert result["status"] == "success"
    assert result["event_type"] == "invoice_finalized"
    assert result["invoice_id"] == "inv_test_123"
    assert result["amount_due"] == 1000
    mock_stripe["webhook"].assert_called_once()
