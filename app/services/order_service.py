
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from decimal import Decimal

from app.models.order import Order, OrderItem
from app.repositories import order_repository



def calculate_cart_total(db: Session, current_user):
    cart = order_repository.get_cart_for_update(db, current_user.id)
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Your cart is empty.")

    from app.services.plan_service import get_user_plan_discount_percent
    discount_pct = get_user_plan_discount_percent(current_user.id)
    discount_multiplier = Decimal(str((100 - discount_pct) / 100)) if discount_pct > 0 else Decimal("1.0")

    total_amount = Decimal("0.00")
    for cart_item in cart.items:
        book = db.query(order_repository.Book).filter(order_repository.Book.id == cart_item.book_id).first()
        if not book or not book.is_active:
            raise HTTPException(status_code=400, detail=f"Book ID {cart_item.book_id} is unavailable.")
        effective_price = (book.price * discount_multiplier).quantize(Decimal("0.01"))
        total_amount += effective_price * cart_item.quantity

    return total_amount


def create_customer_order(db: Session, current_user, payload=None):

    try:
        # 1. Get and lock customer's cart
        cart = order_repository.get_cart_for_update(
            db, current_user.id
        )

        if not cart or not cart.items:
            raise HTTPException(
                status_code=400,
                detail="Your cart is empty."
            )

        # 2. Prepare delivery address
        delivery_address = None
        if payload and payload.delivery_address and payload.delivery_address.strip():
            delivery_address = payload.delivery_address.strip()
        else:
            address_parts = [
                current_user.address,
                current_user.city,
                current_user.state,
                current_user.postal_code,
                current_user.country
            ]

            delivery_address = ", ".join(
                part.strip()
                for part in address_parts
                if part and part.strip()
            )

        if not delivery_address:
            raise HTTPException(
                status_code=400,
                detail="Please provide a shipping address before placing an order."
            )

        # Update customer address and coordinates in database if provided
        current_user.address = delivery_address
        if payload and payload.delivery_phone:
            current_user.phone_number = payload.delivery_phone
        if payload and payload.latitude is not None:
            current_user.latitude = payload.latitude
        if payload and payload.longitude is not None:
            current_user.longitude = payload.longitude
        db.add(current_user)

        delivery_phone = (payload.delivery_phone if payload and payload.delivery_phone else None) or current_user.phone_number

        # 3. Prepare order items
        order_items = []
        total_amount = Decimal("0.00")

        for cart_item in cart.items:

            # Lock the book row while checking stock
            book = order_repository.get_book_for_update(
                db, cart_item.book_id
            )

            if not book or not book.is_active:
                raise HTTPException(
                    status_code=400,
                    detail=f"Book ID {cart_item.book_id} is unavailable."
                )

            # Check available stock
            if book.stock < cart_item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for {book.title}."
                )

            # Apply Member Discount (Gold: 20%, Silver: 10%, Free: 0%)
            from app.services.plan_service import get_user_plan_discount_percent
            discount_pct = get_user_plan_discount_percent(current_user.id)
            if discount_pct > 0:
                discount_multiplier = Decimal(str((100 - discount_pct) / 100))
                effective_price = (book.price * discount_multiplier).quantize(Decimal("0.01"))
            else:
                effective_price = book.price

            # Calculate item total
            item_total = effective_price * cart_item.quantity
            total_amount += item_total

            # Create order item snapshot
            order_item = OrderItem(
                book_id=book.id,
                book_title=book.title,
                book_author=book.author,
                quantity=cart_item.quantity,
                price_at_purchase=effective_price
            )

            order_items.append(order_item)

            # Reserve stock for this pending order
            book.stock -= cart_item.quantity

        # 4. Handle Payment Verification
        payment_method = getattr(payload, "payment_method", "razorpay") if payload else "razorpay"
        payment_status = "pending"

        if payment_method == "razorpay":
            if not payload or not payload.razorpay_payment_id or not payload.razorpay_order_id or not payload.razorpay_signature:
                raise HTTPException(
                    status_code=400,
                    detail="Payment verification failed: Razorpay payment details are missing. Please complete online payment."
                )
            
            from app.services.razorpay_service import verify_razorpay_signature
            is_valid = verify_razorpay_signature(
                razorpay_order_id=payload.razorpay_order_id,
                razorpay_payment_id=payload.razorpay_payment_id,
                signature=payload.razorpay_signature
            )
            if not is_valid:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid Razorpay payment signature. Payment could not be verified."
                )
            payment_status = "paid"
        elif payment_method == "cod":
            payment_status = "pending"
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported payment method."
            )

        # 5. Create order
        new_order = Order(
            user_id=current_user.id,
            total_amount=total_amount,
            delivery_address=delivery_address,
            delivery_phone=delivery_phone,
            order_status="processing" if payment_status == "paid" else "pending",
            payment_status=payment_status,
            items=order_items
        )

        order_repository.create_order(db, new_order)

        # 5. Clear cart items after creating the order
        order_repository.clear_cart_items(db, cart)

        # 6. Commit order, stock reservation, and cart clearing together
        db.commit()

        db.refresh(new_order)

        return new_order

    except Exception:
        db.rollback()
        raise


def get_customer_orders(db: Session, user_id: int):

    return order_repository.get_orders_by_user(
        db, user_id
    )


def get_customer_order_details(
    db: Session,
    order_id: int,
    user_id: int
):

    order = order_repository.get_order_by_user(
        db, order_id, user_id
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found."
        )

    return order


def get_all_customer_orders(db: Session):

    return order_repository.get_all_orders(db)



def update_customer_order_status(
    db: Session,
    order_id: int,
    new_status: str
):

    # Flexible Admin status transitions
    allowed_transitions = {
        "pending": ["pending", "processing", "shipped", "delivered", "cancelled"],
        "processing": ["pending", "processing", "shipped", "delivered", "cancelled"],
        "shipped": ["pending", "processing", "shipped", "delivered", "cancelled"],
        "delivered": ["pending", "processing", "shipped", "delivered", "cancelled"],
        "cancelled": ["pending", "processing", "shipped", "delivered", "cancelled"]
    }

    if new_status not in [
        "pending", "processing", "shipped", "delivered", "cancelled"
    ]:
        raise HTTPException(
            status_code=400,
            detail="Invalid order status."
        )

    try:
        # 1. Lock the order row
        order = order_repository.get_order_for_update(
            db, order_id
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found."
            )

        # 2. Validate status transition
        if new_status not in allowed_transitions.get(
            order.order_status, []
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Cannot change order status from "
                    f"{order.order_status} to {new_status}."
                )
            )

        # 3. Restore stock only when cancelling
        if new_status == "cancelled":

            for item in order.items:

                book = order_repository.get_book_for_update(
                    db, item.book_id
                )

                if book:
                    book.stock += item.quantity

        # 4. Update order status
        order.order_status = new_status

        # 5. Commit changes
        db.commit()
        db.refresh(order)

        return order

    except Exception:
        db.rollback()
        raise



def cancel_customer_order(db: Session, order_id: int, user_id: int):
    try:
        order = order_repository.get_order_for_update(db, order_id)

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found."
            )

        # Allow user who owns the order (or admin)
        if order.user_id != user_id:
            from app.models.user import User
            requesting_user = db.query(User).filter(User.id == user_id).first()
            if not requesting_user or requesting_user.role != "admin":
                raise HTTPException(
                    status_code=403,
                    detail="You can only cancel your own orders."
                )

        status_lower = (order.order_status or "").lower()
        if status_lower in ["cancelled", "canceled"]:
            raise HTTPException(
                status_code=400,
                detail="Order is already cancelled."
            )

        if status_lower not in ["pending", "processing"]:
            raise HTTPException(
                status_code=400,
                detail=f"Order cannot be cancelled because it is already {order.order_status}."
            )

        # Restore stock for each item in the cancelled order
        for item in order.items:
            book = order_repository.get_book_for_update(db, item.book_id)
            if book:
                book.stock += item.quantity

        order.order_status = "cancelled"
        db.commit()
        db.refresh(order)
        return order

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error cancelling order: {str(e)}"
        )
