"""Geocodificación vía Nominatim (OpenStreetMap)."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

GEOCODER_USER_AGENT = "RumboPerfecto-Lite/1 (+https://localhost)"


class GeocodeLookupError(Exception):
    """Error de red o respuesta inválida del proveedor."""


class GeocodeNotFoundError(Exception):
    """Sin resultados para la consulta."""


def nominatim_geocode_first(
    query: str,
    *,
    timeout: float = 12.0,
    accept_language: str = "es",
) -> tuple[float, float, str]:
    q = query.strip()
    if len(q) > 280:
        q = q[:280]

    qs = urllib.parse.urlencode({"format": "json", "limit": "1", "q": q})
    url = f"https://nominatim.openstreetmap.org/search?{qs}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": GEOCODER_USER_AGENT,
            "Accept": "application/json",
            "Accept-Language": accept_language,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as exc:
        raise GeocodeLookupError("HTTP error from nominatim") from exc
    except Exception as exc:
        raise GeocodeLookupError("geocode request failed") from exc

    if not isinstance(data, list) or len(data) == 0:
        raise GeocodeNotFoundError()

    first = data[0]
    try:
        lat = float(first["lat"])
        lon = float(first["lon"])
    except (KeyError, TypeError, ValueError) as exc:
        raise GeocodeLookupError("incomplete nominatim payload") from exc

    display_name = str(first.get("display_name") or q)
    return lat, lon, display_name
