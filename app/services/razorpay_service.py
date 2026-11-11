import hmac
import hashlib
from decimal import Decimal
from fastapi import HTTPException
import razorpay
from app.database.connection import settings


def get_razorpay_client():
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Razorpay credentials are not configured on server."
        )
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def create_razorpay_order(amount: Decimal, currency: str = "INR", receipt: str = None) -> dict:
    """
    Amount is in Decimal currency (e.g. 19.99 or 500.00).
    Razorpay expects amount in smallest currency unit (paise: multiply by 100).
    """
    client = get_razorpay_client()
    amount_in_paise = int((amount * 100).to_integral_value())

    payload = {
        "amount": amount_in_paise,
        "currency": currency,
        "payment_capture": 1
    }
    if receipt:
        payload["receipt"] = receipt[:40]

    try:
        razorpay_order = client.order.create(data=payload)
        return razorpay_order
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create Razorpay payment order: {str(e)}"
        )


def verify_razorpay_signature(razorpay_order_id: str, razorpay_payment_id: str, signature: str) -> bool:
    """
    Verifies that the payment signature matches Razorpay's HMAC SHA256 signature.
    """
    if not settings.RAZORPAY_KEY_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Razorpay secret is not configured on server."
        )

    message = f"{razorpay_order_id}|{razorpay_payment_id}".encode("utf-8")
    generated_signature = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode("utf-8"),
        message,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(generated_signature, signature)

