
import httpx

from fastapi import HTTPException

from app.database.connection import settings


GEOAPIFY_AUTOCOMPLETE_URL = (
    "https://api.geoapify.com/v1/geocode/autocomplete"
)


async def autocomplete_address(search_text: str):

    params = {
        "text": search_text,
        "apiKey": settings.GEOAPIFY_API_KEY,
        "filter": "countrycode:in",
        "limit": 5
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:

            response = await client.get(
                GEOAPIFY_AUTOCOMPLETE_URL,
                params=params
            )

            response.raise_for_status()

            return response.json()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Address service timed out"
        )

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail="Address service returned an error"
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Unable to connect to address service"
        )






GEOAPIFY_REVERSE_URL = (
    "https://api.geoapify.com/v1/geocode/reverse"
)


async def reverse_geocode(latitude: float, longitude: float):

    params = {
        "lat": latitude,
        "lon": longitude,
        "apiKey": settings.GEOAPIFY_API_KEY
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:

            response = await client.get(
                GEOAPIFY_REVERSE_URL,
                params=params
            )

            response.raise_for_status()

            return response.json()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Address service timed out"
        )

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail="Address service returned an error"
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Unable to connect to address service"
        )
