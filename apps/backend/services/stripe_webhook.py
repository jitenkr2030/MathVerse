"""
Stripe Webhook Handler for MathVerse Platform

This module provides secure webhook processing for Stripe payment events.
It handles subscription creation, renewals, failures, and cancellations.
"""

import logging
import hmac
import hashlib
import json
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from fastapi import Request, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

import stripe
import os

from app.database import get_db
from app.models import User, Payment, Subscription, Enrollment, Course

logger = logging.getLogger(__name__)


class WebhookEventType(Enum):
    """Stripe webhook event types we handle."""
    CHECKOUT_SESSION_COMPLETED = "checkout.session.completed"
    INVOICE_PAYMENT_SUCCEEDED = "invoice.payment_succeeded"
    INVOICE_PAYMENT_FAILED = "invoice.payment_failed"
    CUSTOMER_SUBSCRIPTION_CREATED = "customer.subscription.created"
    CUSTOMER_SUBSCRIPTION_UPDATED = "customer.subscription.updated"
    CUSTOMER_SUBSCRIPTION_DELETED = "customer.subscription.deleted"
    PAYMENT_INTENT_SUCCEEDED = "payment_intent.succeeded"
    PAYMENT_INTENT_PAYMENT_FAILED = "payment_intent.payment_failed"


@dataclass
class StripeWebhookEvent:
    """Parsed Stripe webhook event."""
    id: str
    type: WebhookEventType
    data: Dict[str, Any]
    created_at: datetime


class StripeWebhookHandler:
    """
    Handles Stripe webhook events with signature verification and idempotency.
    """
    
    def __init__(self, webhook_secret: str):
        """
        Initialize the webhook handler.
        
        Args:
            webhook_secret: Stripe webhook signing secret
        """
        self.webhook_secret = webhook_secret
        self._processed_events: set = set()  # For idempotency
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify Stripe webhook signature.
        
        Args:
            payload: Raw request body
            signature: Stripe-Signature header value
            
        Returns:
            True if signature is valid
            
        Raises:
            HTTPException: If signature verification fails
        """
        try:
            stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return True
        except stripe.error.SignatureVerificationError:
            logger.warning("Invalid Stripe webhook signature")
            raise HTTPException(
                status_code=400,
                detail="Invalid webhook signature"
            )
    
    def parse_event(self, payload: dict) -> StripeWebhookEvent:
        """
        Parse webhook payload into structured event.
        
        Args:
            payload: Webhook payload from Stripe
            
        Returns:
            Parsed StripeWebhookEvent
            
        Raises:
            HTTPException: If event type is not supported
        """
        event_id = payload.get("id")
        
        # Check idempotency
        if event_id in self._processed_events:
            logger.info(f"Duplicate event detected: {event_id}")
            raise HTTPException(
                status_code=400,
                detail="Duplicate event"
            )
        
        event_type_str = payload.get("type")
        
        # Parse event type
        try:
            event_type = WebhookEventType(event_type_str)
        except ValueError:
            logger.info(f"Unhandled event type: {event_type_str}")
            raise HTTPException(
                status_code=400,
                detail=f"Unhandled event type: {event_type_str}"
            )
        
        return StripeWebhookEvent(
            id=event_id,
            type=event_type,
            data=payload.get("data", {}).get("object", {}),
            created_at=datetime.fromtimestamp(payload.get("created", 0))
        )
    
    async def handle_event(
        self,
        event: StripeWebhookEvent,
        db: Session
    ) -> Dict[str, Any]:
        """
        Handle a processed webhook event.
        
        Args:
            event: Parsed webhook event
            db: Database session
            
        Returns:
            Result of event handling
        """
        handler_map = {
            WebhookEventType.CHECKOUT_SESSION_COMPLETED: self._handle_checkout_completed,
            WebhookEventType.INVOICE_PAYMENT_SUCCEEDED: self._handle_invoice_succeeded,
            WebhookEventType.INVOICE_PAYMENT_FAILED: self._handle_invoice_failed,
            WebhookEventType.CUSTOMER_SUBSCRIPTION_CREATED: self._handle_subscription_created,
            WebhookEventType.CUSTOMER_SUBSCRIPTION_UPDATED: self._handle_subscription_updated,
            WebhookEventType.CUSTOMER_SUBSCRIPTION_DELETED: self._handle_subscription_deleted,
            WebhookEventType.PAYMENT_INTENT_SUCCEEDED: self._handle_payment_intent_succeeded,
            WebhookEventType.PAYMENT_INTENT_PAYMENT_FAILED: self._handle_payment_intent_failed,
        }
        
        handler = handler_map.get(event.type)
        if handler:
            result = await handler(event, db)
            self._processed_events.add(event.id)
            return result
        
        return {"status": "ignored", "reason": "No handler for event type"}
    
    async def _handle_checkout_completed(
        self,
        event: StripeWebhookEvent,
        db: Session
    ) -> Dict[str, Any]:
        """Handle successful checkout session completion."""
        data = event.data
        
        customer_id = data.get("customer")
        customer_email = data.get("customer_email")
        payment_intent = data.get("payment_intent")
        amount_total = data.get("amount_total", 0) / 100  # Convert from cents
        currency = data.get("currency", "usd").upper()
        
        # Find user by Stripe customer ID or email
        user = None
        if customer_id:
            user = db.execute(
                select(User).where(User.stripe_customer_id == customer_id)
            ).scalar_one_or_none()
        
        if not user and customer_email:
            user = db.execute(
                select(User).where(User.email == customer_email)
            ).scalar_one_or_none()
        
        if not user:
            logger.warning(f"User not found for checkout: {customer_email or customer_id}")
            return {"status": "user_not_found"}
        
        # Check if this is a subscription or one-time purchase
        mode = data.get("mode", "payment")
        
        if mode == "subscription":
            # Handle subscription checkout
            subscription_id = data.get("subscription")
            await self._create_or_update_subscription(
                user.id, subscription_id, customer_id, db
            )
        else:
            # Handle one-time payment (course purchase)
            # Extract metadata about what was purchased
            metadata = data.get("metadata", {})
            course_id = metadata.get("course_id")
            
            if course_id:
                # Create payment record
                payment = Payment(
                    user_id=user.id,
                    course_id=int(course_id),
                    amount=amount_total,
                    currency=currency,
                    status="completed",
                    payment_method="stripe",
                    stripe_payment_intent_id=payment_intent
                )
                db.add(payment)
                
                # Create enrollment
                enrollment = Enrollment(
                    user_id=user.id,
                    course_id=int(course_id)
                )
                db.add(enrollment)
                
                db.commit()
        
        logger.info(f"Checkout completed for user {user.id}")
        return {"status": "completed", "user_id": user.id}
    
    async def _handle_invoice_succeeded(
        self,
        event: StripeWebhookEvent,
        db: Session
    ) -> Dict[str, Any]:
        """Handle successful invoice payment."""
        data = event.data
        
        customer_id = data.get("customer")
        subscription_id = data.get("subscription")
        amount_paid = data.get("amount_paid", 0) / 100
        
        user = db.execute(
            select(User).where(User.stripe_customer_id == customer_id)
        ).scalar_one_or_none()
        
        if not user:
            logger.warning(f"User not found for invoice: {customer_id}")
            return {"status": "user_not_found"}
        
        if subscription_id:
            # Update subscription
            subscription = db.execute(
                select(Subscription).where(
                    and_(
                        Subscription.stripe_subscription_id == subscription_id,
                        Subscription.user_id == user.id
                    )
                )
            ).scalar_one_or_none()
            
            if subscription:
                # Extend subscription period
                period_end = data.get("period_end")
                if period_end:
                    from datetime import datetime, timedelta
                    subscription.expires_at = datetime.fromtimestamp(period_end)
                
                subscription.is_active = True
                db.commit()
        
        logger.info(f"Invoice payment succeeded for user {user.id}")
        return {"status": "completed", "user_id": user.id}
    
    async def _handle_invoice_failed(
        self,
        event: StripeWebhookEvent,
        db: Session
    ) -> Dict[str, Any]:
        """Handle failed invoice payment."""
        data = event.data
        
        customer_id = data.get("customer")
        subscription_id = data.get("subscription")
        
        user = db.execute(
            select(User).where(User.stripe_customer_id == customer_id)
        ).scalar_one_or_none()
        
        if not user:
            return {"status": "user_not_found"}
        
        if subscription_id:
            subscription = db.execute(
                select(Subscription).where(
                    and_(
                        Subscription.stripe_subscription_id == subscription_id,
                        Subscription.user_id == user.id
                    )
                )
            ).scalar_one_or_none()
            
            if subscription:
                subscription.is_active = False
                db.commit()
        
        logger.warning(f"Invoice payment failed for user {user.id}")
        return {"status": "payment_failed", "user_id": user.id}
    
    async def _handle_subscription_created(
        self,
        event: StripeWebhookEvent,
        db: Session
    ) -> Dict[str, Any]:
        """Handle new subscription creation."""
        data = event.data
        
        customer_id = data.get("customer")
        subscription_id = data.get("id")
        status = data.get("status")
        current_period_end = data.get("current_period_end")
        
        user = db.execute(
            select(User).where(User.stripe_customer_id == customer_id)
        ).scalar_one_or_none()
        
        if not user:
            return {"status": "user_not_found"}
        
        await self._create_or_update_subscription(
            user.id, subscription_id, customer_id, db,
            expires_at=current_period_end
        )
        
        return {"status": "completed", "user_id": user.id}
    
    async def _handle_subscription_updated(
        self,
        event: StripeWebhookEvent,
        db: Session
    ) -> Dict[str, Any]:
        """Handle subscription updates."""
        data = event.data
        
        customer_id = data.get("customer")
        subscription_id = data.get("id")
        status = data.get("status")
        current_period_end = data.get("current_period_end")
        
        user = db.execute(
            select(User).where(User.stripe_customer_id == customer_id)
        ).scalar_one_or_none()
        
        if not user:
            return {"status": "user_not_found"}
        
        await self._create_or_update_subscription(
            user.id, subscription_id, customer_id, db,
            expires_at=current_period_end
        )
        
        return {"status": "completed", "user_id": user.id}
    
    async def _handle_subscription_deleted(
        self,
        event: StripeWebhookEvent,
        db: Session
    ) -> Dict[str, Any]:
        """Handle subscription cancellation."""
        data = event.data
        
        customer_id = data.get("customer")
        subscription_id = data.get("id")
        
        user = db.execute(
            select(User).where(User.stripe_customer_id == customer_id)
        ).scalar_one_or_none()
        
        if not user:
            return {"status": "user_not_found"}
        
        subscription = db.execute(
            select(Subscription).where(
                and_(
                    Subscription.stripe_subscription_id == subscription_id,
                    Subscription.user_id == user.id
                )
            )
        ).scalar_one_or_none()
        
        if subscription:
            subscription.is_active = False
            db.commit()
        
        logger.info(f"Subscription deleted for user {user.id}")
        return {"status": "completed", "user_id": user.id}
    
    async def _handle_payment_intent_succeeded(
        self,
        event: StripeWebhookEvent,
        db: Session
    ) -> Dict[str, Any]:
        """Handle successful payment intent."""
        data = event.data
        
        payment_intent_id = data.get("id")
        amount = data.get("amount", 0) / 100
        currency = data.get("currency", "usd").upper()
        
        # Find and update payment record
        payment = db.execute(
            select(Payment).where(
                Payment.stripe_payment_intent_id == payment_intent_id
            )
        ).scalar_one_or_none()
        
        if payment:
            payment.status = "completed"
            db.commit()
        
        logger.info(f"Payment intent succeeded: {payment_intent_id}")
        return {"status": "completed"}
    
    async def _handle_payment_intent_failed(
        self,
        event: StripeWebhookEvent,
        db: Session
    ) -> Dict[str, Any]:
        """Handle failed payment intent."""
        data = event.data
        
        payment_intent_id = data.get("id")
        
        # Find and update payment record
        payment = db.execute(
            select(Payment).where(
                Payment.stripe_payment_intent_id == payment_intent_id
            )
        ).scalar_one_or_none()
        
        if payment:
            payment.status = "failed"
            db.commit()
        
        logger.warning(f"Payment intent failed: {payment_intent_id}")
        return {"status": "payment_failed"}
    
    async def _create_or_update_subscription(
        self,
        user_id: int,
        stripe_subscription_id: str,
        stripe_customer_id: str,
        db: Session,
        expires_at: Optional[int] = None
    ) -> Subscription:
        """Create or update user subscription."""
        from datetime import datetime, timedelta
        
        # Check for existing subscription
        subscription = db.execute(
            select(Subscription).where(
                and_(
                    Subscription.stripe_subscription_id == stripe_subscription_id,
                    Subscription.user_id == user_id
                )
            )
        ).scalar_one_or_none()
        
        if not subscription:
            subscription = Subscription(
                user_id=user_id,
                stripe_subscription_id=stripe_subscription_id,
                stripe_customer_id=stripe_customer_id,
                tier="premium",
                starts_at=datetime.utcnow()
            )
            db.add(subscription)
        
        # Update subscription
        if expires_at:
            subscription.expires_at = datetime.fromtimestamp(expires_at)
        else:
            subscription.expires_at = datetime.utcnow() + timedelta(days=30)
        
        subscription.is_active = True
        db.commit()
        db.refresh(subscription)
        
        return subscription


# Global webhook handler instance
_webhook_handler: Optional[StripeWebhookHandler] = None


def get_webhook_handler() -> StripeWebhookHandler:
    """Get or create the webhook handler instance."""
    global _webhook_handler
    
    if _webhook_handler is None:
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        if not webhook_secret:
            logger.warning("STRIPE_WEBHOOK_SECRET not configured")
            webhook_secret = "whsec_test_placeholder"
        
        _webhook_handler = StripeWebhookHandler(webhook_secret)
    
    return _webhook_handler


async def process_stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Process incoming Stripe webhook.
    
    Args:
        request: FastAPI request object
        background_tasks: Background tasks runner
        
    Returns:
        Response dict with status
    """
    # Get raw body for signature verification
    body = await request.body()
    
    # Get signature header
    signature = request.headers.get("Stripe-Signature")
    if not signature:
        raise HTTPException(
            status_code=400,
            detail="Missing Stripe-Signature header"
        )
    
    # Get database session
    db = next(get_db())
    
    try:
        # Parse payload
        payload = await request.json()
        
        # Get handler and verify signature
        handler = get_webhook_handler()
        handler.verify_signature(body, signature)
        
        # Parse event
        event = handler.parse_event(payload)
        
        # Handle event
        result = await handler.handle_event(event, db)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Webhook processing failed"
        )
    finally:
        db.close()
