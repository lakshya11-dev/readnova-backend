from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.connection import get_db, settings
from app.core.dependencies import require_role
from app.models.user import User
from app.schemas.plan import (
    PlanListResponse,
    PlanSubscribeRequest,
    PlanSubscribeResponse,
    PlanRazorpayOrderResponse,
)
from app.services import plan_service
from app.services.razorpay_service import create_razorpay_order
from decimal import Decimal

router = APIRouter(
    prefix="/plans",
    tags=["Pricing & Subscriptions"]
)


@router.post("/create-razorpay-order/{plan_id}", response_model=PlanRazorpayOrderResponse)
def initialize_plan_razorpay_order(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("customer", "admin"))
):
    """
    Initialize a Razorpay checkout session for activating a paid tier (Silver, Gold).
    """
    if plan_id not in plan_service.AVAILABLE_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan '{plan_id}'."
        )

    plan = plan_service.AVAILABLE_PLANS[plan_id]
    amount = Decimal(str(plan.price))

    rp_order = create_razorpay_order(
        amount=amount,
        currency="INR",
        receipt=f"plan_{plan_id[:10]}_{current_user.id}"
    )

    return PlanRazorpayOrderResponse(
        razorpay_order_id=rp_order["id"],
        amount=rp_order["amount"],
        currency=rp_order.get("currency", "INR"),
        key_id=settings.RAZORPAY_KEY_ID,
        plan_id=plan.id,
        plan_name=plan.name,
        price=plan.price
    )


@router.get("", response_model=PlanListResponse)
def list_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("customer", "admin"))
):
    """
    Get available time-limited plans (Free, Silver 1h/6h, Gold 12h)
    and user's active plan countdown.
    """
    return plan_service.get_available_plans(current_user)


@router.post("/subscribe", response_model=PlanSubscribeResponse)
def subscribe_plan(
    payload: PlanSubscribeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("customer", "admin"))
):
    """
    Pay and activate a time-limited pricing plan.
    Immediately updates user's profile and sets expiration timestamp.
    """
    return plan_service.subscribe_user_to_plan(db, current_user, payload)


@router.post("/cron/expire")
def trigger_plan_expiration_cron(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Manual trigger for plan expiration cron job (also runs automatically in background).
    """
    expired_count = plan_service.check_and_expire_plans(db)
    return {
        "status": "success",
        "expired_plans_deactivated": expired_count,
        "message": f"Evaluated all subscriptions and deactivated {expired_count} expired plan(s)."
    }

