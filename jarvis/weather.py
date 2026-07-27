from __future__ import annotations

import json
from urllib.parse import quote_plus
from urllib.request import Request, urlopen


_WEATHER_CODES = {
    0: "clear sky",
    1: "mostly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    61: "light rain",
    63: "moderate rain",
    65: "heavy rain",
    71: "light snow",
    73: "moderate snow",
    75: "heavy snow",
    80: "light rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    95: "a thunderstorm",
    96: "a thunderstorm with hail",
    99: "a severe thunderstorm with hail",
}


def _get_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "JARVIS-Assistant/1.0"})
    with urlopen(request, timeout=8) as response:
        return json.loads(response.read().decode("utf-8"))


def _locate_by_ip() -> tuple[float, float, str] | None:
    try:
        data = _get_json("https://ipapi.co/json/")
        lat = data.get("latitude")
        lon = data.get("longitude")
        city = data.get("city") or "your area"
        if lat is None or lon is None:
            return None
        return float(lat), float(lon), str(city)
    except Exception:
        return None


def _locate_by_city(city: str) -> tuple[float, float, str] | None:
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={quote_plus(city)}&count=1"
        data = _get_json(url)
        results = data.get("results") or []
        if not results:
            return None
        top = results[0]
        label = top.get("name", city)
        country = top.get("country")
        if country:
            label = f"{label}, {country}"
        return float(top["latitude"]), float(top["longitude"]), label
    except Exception:
        return None


def weather_summary(city: str = "") -> str:
    """Return a short spoken-friendly weather report using free, keyless APIs."""
    location = _locate_by_city(city.strip()) if city.strip() else _locate_by_ip()
    if not location:
        target = city.strip() or "your location"
        return f"I could not find weather data for {target}, sir."

    lat, lon, label = location
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m"
            "&temperature_unit=celsius&wind_speed_unit=kmh"
        )
        data = _get_json(url)
        current = data.get("current", {})
        temp = current.get("temperature_2m")
        feels = current.get("apparent_temperature")
        humidity = current.get("relative_humidity_2m")
        wind = current.get("wind_speed_10m")
        code = current.get("weather_code")
        condition = _WEATHER_CODES.get(code, "changing conditions")

        if temp is None:
            return f"I could not read the weather data for {label}, sir."

        return (
            f"It is currently {temp:.0f} degrees Celsius in {label}, with {condition}, "
            f"feeling like {feels:.0f} degrees. Humidity is {humidity:.0f} percent and "
            f"wind speed is {wind:.0f} kilometers per hour, sir."
        )
    except Exception as exc:
        return f"I could not fetch the weather for {label}, sir. Details: {exc}"
