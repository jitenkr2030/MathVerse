"""
MathVerse Backend API - Payments Module
========================================
Payment processing and subscription management endpoints.
"""

from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
import stripe
import uuid
import os

from app.database import get_db
from app.models import Payment, Course, User, Enrollment, UserRole, Subscription
from app.schemas import (
    PaymentCreate, PaymentResponse, PaymentIntentResponse,
    SubscriptionCreate, SubscriptionResponse, CreatorEarningsResponse,
    MessageResponse, ErrorResponse
)
from app.dependencies import get_current_user, get_or_404


router = APIRouter()


# Initialize Stripe from environment
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


@router.get("/", response_model=List[PaymentResponse])
async def get_user_payments(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's payment history.
    """
    query = select(Payment).where(Payment.user_id == current_user.id)
    
    if status_filter:
        query = query.where(Payment.status == status_filter)
    
    payments = db.execute(
        query.order_by(Payment.created_at.desc())
    ).scalars().all()
    
    return payments


@router.post("/", response_model=PaymentIntentResponse)
async def create_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a payment intent for course purchase.
    """
    # Verify course exists and get price
    course = await get_or_404(Course, payment_data.course_id, db, "Course not found")
    
    if course.is_free:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This course is free, no payment required"
        )
    
    # Check if already enrolled
    existing_enrollment = db.execute(
        select(Enrollment).where(
            and_(
                Enrollment.user_id == current_user.id,
                Enrollment.course_id == payment_data.course_id
            )
        )
    ).scalar_one_or_none()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this course"
        )
    
    # In production, create Stripe PaymentIntent
    # For now, return mock response
    payment_intent_id = f"pi_{uuid.uuid4().hex[:24]}"
    
    # Create pending payment record
    payment = Payment(
        user_id=current_user.id,
        course_id=payment_data.course_id,
        amount=course.price,
        currency=payment_data.currency.upper(),
        status="pending",
        payment_method="stripe",
        stripe_payment_intent_id=payment_intent_id
    )
    
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    # Return client secret for Stripe Elements
    return PaymentIntentResponse(
        client_secret=f"{payment_intent_id}_secret_mock",
        payment_intent_id=payment_intent_id,
        amount=int(course.price * 100),  # Stripe uses cents
        currency=payment_data.currency.upper()
    )


@router.post("/{payment_id}/confirm", response_model=PaymentResponse)
async def confirm_payment(
    payment_id: int,
    payment_intent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Confirm payment and enroll user.
    """
    payment = await get_or_404(Payment, payment_id, db, "Payment not found")
    
    if payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to confirm this payment"
        )
    
    # In production, verify Stripe payment
    # For now, just mark as completed
    
    payment.status = "completed"
    
    # Create enrollment
    enrollment = Enrollment(
        user_id=current_user.id,
        course_id=payment.course_id
    )
    db.add(enrollment)
    
    db.commit()
    db.refresh(payment)
    
    return payment


@router.post("/webhook")
async def stripe_webhook(
    payload: dict,
    background_tasks: BackgroundTasks
):
    """
    Handle Stripe webhook events.
    """
    # In production, verify webhook signature
    event_type = payload.get("type")
    data = payload.get("data", {}).get("object", {})
    
    if event_type == "payment_intent.succeeded":
        payment_intent_id = data.get("id")
        
        # Find and update payment
        # payment = db.query(Payment).filter_by(stripe_payment_intent_id=payment_intent_id).first()
        # if payment:
        #     payment.status = "completed"
        #     # Create enrollment...
    
    elif event_type == "payment_intent.payment_failed":
        payment_intent_id = data.get("id")
        
        # Find and update payment
        # payment = db.query(Payment).filter_by(stripe_payment_intent_id=payment_intent_id).first()
        # if payment:
        #     payment.status = "failed"
    
    return {"status": "received"}


# ==================== SUBSCRIPTIONS ====================

@router.post("/subscription", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a premium subscription.
    """
    # In production, create Stripe subscription
    # For now, create mock subscription
    
    subscription = Subscription(
        user_id=current_user.id,
        tier=subscription_data.tier.value if hasattr(subscription_data.tier, 'value') else subscription_data.tier,
        starts_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=30),
        is_active=True
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    return subscription


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's current subscription.
    """
    subscription = db.execute(
        select(Subscription).where(
            and_(
                Subscription.user_id == current_user.id,
                Subscription.is_active == True
            )
        )
        .order_by(Subscription.expires_at.desc())
    ).scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    return subscription


@router.delete("/subscription", response_model=MessageResponse)
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel user's subscription.
    """
    subscription = db.execute(
        select(Subscription).where(
            and_(
                Subscription.user_id == current_user.id,
                Subscription.is_active == True
            )
        )
    ).scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    subscription.is_active = False
    db.commit()
    
    return MessageResponse(
        message="Subscription cancelled",
        detail="Your subscription has been cancelled. You will retain access until the end of your billing period."
    )


# ==================== CREATOR EARNINGS ====================

@router.get("/earnings", response_model=CreatorEarningsResponse)
async def get_creator_earnings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get creator earnings and transaction history.
    """
    if current_user.role not in [UserRole.CREATOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only creators can access earnings"
        )
    
    # Get all payments for creator's courses
    creator_courses = db.execute(
        select(Course.id).where(Course.creator_id == current_user.id)
    ).scalars().all()
    
    if not creator_courses:
        return CreatorEarningsResponse(
            total_earnings=0,
            pending_earnings=0,
            paid_earnings=0,
            this_month_earnings=0,
            transactions=[]
        )
    
    # Calculate total earnings
    total_earnings = db.execute(
        select(func.sum(Payment.amount)).where(
            and_(
                Payment.course_id.in_(creator_courses),
                Payment.status == "completed"
            )
        )
    ).scalar() or 0
    
    # Calculate pending earnings
    pending_earnings = db.execute(
        select(func.sum(Payment.amount)).where(
            and_(
                Payment.course_id.in_(creator_courses),
                Payment.status == "pending"
            )
        )
    ).scalar() or 0
    
    # Calculate this month earnings
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    this_month_earnings = db.execute(
        select(func.sum(Payment.amount)).where(
            and_(
                Payment.course_id.in_(creator_courses),
                Payment.status == "completed",
                Payment.created_at >= start_of_month
            )
        )
    ).scalar() or 0
    
    # Get recent transactions
    transactions = db.execute(
        select(Payment)
        .where(
            and_(
                Payment.course_id.in_(creator_courses),
                Payment.status == "completed"
            )
        )
        .order_by(Payment.created_at.desc())
        .limit(50)
    ).scalars().all()
    
    transaction_list = []
    for tx in transactions:
        course = db.execute(
            select(Course).where(Course.id == tx.course_id)
        ).scalar_one_or_none()
        
        transaction_list.append({
            "id": tx.id,
            "course_id": tx.course_id,
            "course_title": course.title if course else None,
            "amount": tx.amount,
            "currency": tx.currency,
            "date": tx.created_at
        })
    
    return CreatorEarningsResponse(
        total_earnings=total_earnings * 0.70,  # 70% revenue share for creators
        pending_earnings=pending_earnings * 0.70,
        paid_earnings=0,  # Would track paid amounts
        this_month_earnings=this_month_earnings * 0.70,
        transactions=transaction_list
    )


@router.get("/earnings/payout", response_model=MessageResponse)
async def request_payout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request payout for creator earnings.
    """
    if current_user.role not in [UserRole.CREATOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only creators can request payouts"
        )
    
    # In production, this would initiate a Stripe payout
    return MessageResponse(
        message="Payout request submitted",
        detail="Your payout request has been submitted and will be processed within 5-7 business days."
    )


@router.get("/sales/{course_id}")
async def get_course_sales(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get sales data for a specific course.
    """
    course = await get_or_404(Course, course_id, db, "Course not found")
    
    if course.creator_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this course's sales"
        )
    
    # Get sales count
    sales_count = db.execute(
        select(func.count(Payment.id)).where(
            and_(
                Payment.course_id == course_id,
                Payment.status == "completed"
            )
        )
    ).scalar() or 0
    
    # Get total revenue
    total_revenue = db.execute(
        select(func.sum(Payment.amount)).where(
            and_(
                Payment.course_id == course_id,
                Payment.status == "completed"
            )
        )
    ).scalar() or 0
    
    # Get unique buyers
    unique_buyers = db.execute(
        select(func.count(func.distinct(Payment.user_id))).where(
            and_(
                Payment.course_id == course_id,
                Payment.status == "completed"
            )
        )
    ).scalar() or 0
    
    return {
        "course_id": course_id,
        "course_title": course.title,
        "sales_count": sales_count,
        "total_revenue": total_revenue * 0.70,  # After platform fee
        "unique_buyers": unique_buyers,
        "revenue_share": "70%"
    }
