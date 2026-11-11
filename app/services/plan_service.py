import json
import os
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.plan import PlanItem, PlanListResponse, PlanSubscribeResponse

PLAN_STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "user_plans.json")

def _load_plans_store() -> dict:
    if os.path.exists(PLAN_STATE_FILE):
        try:
            with open(PLAN_STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_plans_store(store: dict):
    try:
        with open(PLAN_STATE_FILE, "w") as f:
            json.dump(store, f, indent=2)
    except Exception as e:
        print(f"Warning: could not save plan state: {e}")


# Canonical definitions according to FRD: Free, Silver, Gold with 1h, 6h, 12h limits
AVAILABLE_PLANS = {
    "free": PlanItem(
        id="free",
        name="Free",
        tier="free",
        price=0.0,
        duration_hours=None,
        duration_label="Forever Free",
        description="Standard access to bookstore catalog and regular checkout.",
        features=[
            "Access to all catalog books",
            "Standard shipping rates",
            "Order history and invoice tracking",
            "Basic customer support",
        ],
        popular=False,
    ),
    "silver_1h": PlanItem(
        id="silver_1h",
        name="Silver (1 Hour Trial)",
        tier="silver",
        price=4.99,
        duration_hours=1,
        duration_label="1 Hour Access",
        description="Flash reader plan: 1 hour of express shipping & 10% book discount.",
        features=[
            "10% discount on all books",
            "Free express delivery",
            "Active for 1 hour from payment",
            "Auto-expires back to Free tier",
        ],
        popular=False,
    ),
    "silver_6h": PlanItem(
        id="silver_6h",
        name="Silver (6 Hours)",
        tier="silver",
        price=14.99,
        duration_hours=6,
        duration_label="6 Hours Access",
        description="Ideal for focused reading sessions with priority benefits.",
        features=[
            "10% discount on all books",
            "Free priority delivery",
            "Active for 6 hours from payment",
            "Auto-expires back to Free tier",
        ],
        popular=True,
    ),
    "gold_12h": PlanItem(
        id="gold_12h",
        name="Gold (12 Hours)",
        tier="gold",
        price=29.99,
        duration_hours=12,
        duration_label="12 Hours Access",
        description="Full VIP day pass with maximum 20% discount and concierge support.",
        features=[
            "20% discount on all books",
            "Guaranteed same-day/next-day dispatch",
            "Active for 12 hours from payment",
            "Concierge librarian support",
        ],
        popular=False,
    ),
}


def get_user_plan_data(user_id: int) -> dict:
    store = _load_plans_store()
    data = store.get(str(user_id))
    now = datetime.now(timezone.utc)
    if data and data.get("expires_at"):
        exp_dt = datetime.fromisoformat(data["expires_at"])
        if exp_dt <= now:
            # Plan has expired
            data["plan_id"] = "free"
            data["plan_name"] = "Free"
            data["plan_status"] = "expired"
            data["duration_hours"] = None
            data["expires_at"] = None
            _save_plans_store(store)
    return data or {
        "plan_id": "free",
        "plan_name": "Free",
        "plan_status": "active",
        "duration_hours": None,
        "activated_at": None,
        "expires_at": None,
    }


def get_user_plan_discount_percent(user_id: int) -> int:
    """
    Returns discount percent:
    - Gold member (gold_12h): 20% discount
    - Silver member (silver_1h, silver_6h): 10% discount
    - Free: 0% discount
    """
    plan_data = get_user_plan_data(user_id)
    if plan_data.get("plan_status") != "active":
        return 0
    plan_name = plan_data.get("plan_name", "").lower()
    plan_id = plan_data.get("plan_id", "").lower()

    if "gold" in plan_name or "gold" in plan_id:
        return 20
    if "silver" in plan_name or "silver" in plan_id:
        return 10
    return 0



def get_available_plans(user: User) -> PlanListResponse:
    plan_info = get_user_plan_data(user.id)
    now = datetime.now(timezone.utc)
    remaining_seconds = None

    expires_at = None
    if plan_info.get("expires_at"):
        try:
            expires_at = datetime.fromisoformat(plan_info["expires_at"])
            diff = (expires_at - now).total_seconds()
            remaining_seconds = max(0, int(diff))
        except Exception:
            pass

    return PlanListResponse(
        plans=list(AVAILABLE_PLANS.values()),
        current_plan=plan_info.get("plan_name", "Free"),
        current_plan_id=plan_info.get("plan_id", "free"),
        current_plan_status=plan_info.get("plan_status", "active"),
        expires_at=expires_at,
        remaining_seconds=remaining_seconds,
    )


def subscribe_user_to_plan(db: Session, user: User, payload) -> PlanSubscribeResponse:
    plan_id = payload.plan_id if hasattr(payload, "plan_id") else str(payload)
    if plan_id not in AVAILABLE_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan '{plan_id}'. Choose from: {list(AVAILABLE_PLANS.keys())}",
        )

    selected = AVAILABLE_PLANS[plan_id]

    # Verify Razorpay payment if plan is paid
    if selected.price > 0:
        payment_method = getattr(payload, "payment_method", "razorpay")
        if payment_method == "razorpay":
            rp_payment_id = getattr(payload, "razorpay_payment_id", None)
            rp_order_id = getattr(payload, "razorpay_order_id", None)
            rp_signature = getattr(payload, "razorpay_signature", None)

            if not rp_payment_id or not rp_order_id or not rp_signature:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payment verification failed: Razorpay payment details are missing."
                )

            from app.services.razorpay_service import verify_razorpay_signature
            if not verify_razorpay_signature(rp_order_id, rp_payment_id, rp_signature):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid Razorpay signature. Plan payment could not be verified."
                )

    now = datetime.now(timezone.utc)

    if selected.duration_hours is not None:
        expires_at = now + timedelta(hours=selected.duration_hours)
        plan_status = "active"
    else:
        expires_at = None
        plan_status = "active"

    store = _load_plans_store()
    store[str(user.id)] = {
        "plan_id": selected.id,
        "plan_name": selected.name,
        "plan_status": plan_status,
        "duration_hours": selected.duration_hours,
        "activated_at": now.isoformat(),
        "expires_at": expires_at.isoformat() if expires_at else None,
    }
    _save_plans_store(store)

    return PlanSubscribeResponse(
        success=True,
        message=f"Successfully activated '{selected.name}' plan!",
        plan_id=selected.id,
        plan_name=selected.name,
        plan_status=plan_status,
        duration_hours=selected.duration_hours,
        activated_at=now,
        expires_at=expires_at,
        user_id=user.id,
    )


def check_and_expire_plans(db: Session = None) -> int:
    """
    Called periodically or manually to expire time-limited plans (1h, 6h, 12h)
    """
    store = _load_plans_store()
    now = datetime.now(timezone.utc)
    count = 0

    for uid, data in store.items():
        if data.get("plan_status") == "active" and data.get("expires_at"):
            try:
                exp_dt = datetime.fromisoformat(data["expires_at"])
                if exp_dt <= now:
                    data["plan_status"] = "expired"
                    data["plan_name"] = "Free"
                    data["duration_hours"] = None
                    count += 1
            except Exception:
                pass

    if count > 0:
        _save_plans_store(store)

    return count
