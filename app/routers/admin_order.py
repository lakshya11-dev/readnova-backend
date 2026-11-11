
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.dependencies import require_role
from app.services import order_service
from app.schemas.order import OrderResponse, OrderStatusUpdate


router = APIRouter(
    prefix="/admin/orders",
    tags=["Admin Orders"]
)


# Admin: View all customer orders
@router.get(
    "/",
    response_model=list[OrderResponse],
    status_code=status.HTTP_200_OK
)
def get_all_orders(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    return order_service.get_all_customer_orders(db)


# Admin: Update order status
@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK
)
def update_order_status(
    order_id: int,
    request: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    status_value = request.get_status()
    return order_service.update_customer_order_status(
        db,
        order_id,
        status_value
    )
