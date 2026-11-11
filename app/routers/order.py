
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.connection import get_db, settings
from app.core.dependencies import require_role
from app.services import order_service
from app.services.razorpay_service import create_razorpay_order
from app.schemas.order import OrderResponse, OrderCreate, RazorpayOrderCreate, RazorpayOrderResponse


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


# Create Razorpay order session before frontend opens checkout modal
@router.post(
    "/create-razorpay-order",
    response_model=RazorpayOrderResponse,
    status_code=status.HTTP_200_OK
)
def initialize_razorpay_order(
    payload: RazorpayOrderCreate | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("customer", "admin"))
):
    if payload and payload.amount and payload.amount > 0:
        amount = payload.amount
    else:
        amount = order_service.calculate_cart_total(db, current_user)

    rp_order = create_razorpay_order(
        amount=amount,
        currency="INR",
        receipt=f"usr_{current_user.id}"
    )

    return RazorpayOrderResponse(
        razorpay_order_id=rp_order["id"],
        amount=rp_order["amount"],
        currency=rp_order.get("currency", "INR"),
        key_id=settings.RAZORPAY_KEY_ID
    )


# Place a new order
@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
def place_order(
    payload: OrderCreate | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("customer", "admin"))
):
    return order_service.create_customer_order(
        db=db,
        current_user=current_user,
        payload=payload
    )


# Get customer's order history
@router.get(
    "/",
    response_model=list[OrderResponse],
    status_code=status.HTTP_200_OK
)
def get_my_orders(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("customer", "admin"))
):
    return order_service.get_customer_orders(
        db, current_user.id
    )


# Cancel an order (placed before /{order_id} or explicitly distinct)
@router.patch(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK
)
@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK
)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("customer", "admin"))
):
    return order_service.cancel_customer_order(
        db, order_id, current_user.id
    )


# Get details of a particular order
@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK
)
def get_order_details(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("customer", "admin"))
):
    return order_service.get_customer_order_details(
        db, order_id, current_user.id
    )
