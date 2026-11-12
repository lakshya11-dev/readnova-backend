import httpx
from app.database.connection import settings


def verify_facebook_token(access_token: str) -> dict:
    """
    Verifies Facebook User Access Token by calling Facebook Graph API /me.
    Returns a dict with facebook_id, email, and name.
    """
    url = "https://graph.facebook.com/me"
    params = {
        "fields": "id,name,email,picture.type(large)",
        "access_token": access_token
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, params=params)

        if response.status_code != 200:
            error_data = response.json().get("error", {})
            msg = error_data.get("message", "Invalid Facebook access token")
            raise ValueError(f"Facebook authentication failed: {msg}")

        data = response.json()
        facebook_id = data.get("id")
        if not facebook_id:
            raise ValueError("No Facebook ID returned by Graph API")

        # Fallback if Facebook account does not have a verified public email
        email = data.get("email") or f"fb_{facebook_id}@facebook.readingnova.com"
        name = data.get("name") or f"Facebook User"
        picture = data.get("picture", {}).get("data", {}).get("url")

        return {
            "facebook_id": str(facebook_id),
            "email": email,
            "name": name,
            "picture": picture
        }
    except httpx.RequestError as exc:
        raise ValueError(f"Unable to communicate with Facebook Graph API: {str(exc)}")

