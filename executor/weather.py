"""
Weather module - lay du lieu thoi tiet MIEN PHI, KHONG CAN API KEY.

Dung Open-Meteo (https://open-meteo.com) cho ca geocoding (ten thanh pho ->
toa do) va du bao thoi tiet. Open-Meteo la dich vu mo, khong yeu cau dang ky
hay API key cho muc dich phi thuong mai.
"""
import requests

_GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Ma weathercode cua Open-Meteo -> mo ta ngan gon bang tieng Anh
_WEATHER_CODES = {
    0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "depositing rime fog",
    51: "light drizzle", 53: "moderate drizzle", 55: "dense drizzle",
    61: "slight rain", 63: "moderate rain", 65: "heavy rain",
    71: "slight snow", 73: "moderate snow", 75: "heavy snow",
    80: "slight rain showers", 81: "moderate rain showers", 82: "violent rain showers",
    95: "thunderstorm", 96: "thunderstorm with slight hail", 99: "thunderstorm with heavy hail",
}


def get_weather(city: str) -> str:
    """Tra ve mot cau mo ta thoi tiet hien tai cho `city`, khong can API key."""
    if not city:
        return "Please tell me which city you want the weather for, sir."

    try:
        # Buoc 1: Geocoding - chuyen ten thanh pho thanh toa do lat/lon
        geo_resp = requests.get(
            _GEOCODE_URL, params={"name": city, "count": 1}, timeout=6
        )
        geo_data = geo_resp.json()
        results = geo_data.get("results")
        if not results:
            return f"Sorry sir, I could not find a location named '{city}'."

        place = results[0]
        lat, lon = place["latitude"], place["longitude"]
        place_name = place.get("name", city)
        country = place.get("country", "")

        # Buoc 2: Lay du bao thoi tiet hien tai cho toa do do
        forecast_resp = requests.get(
            _FORECAST_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                "timezone": "auto",
            },
            timeout=6,
        )
        forecast_data = forecast_resp.json()
        current = forecast_data.get("current", {})

        temp = current.get("temperature_2m")
        humidity = current.get("relative_humidity_2m")
        wind = current.get("wind_speed_10m")
        code = current.get("weather_code")
        description = _WEATHER_CODES.get(code, "unknown conditions")

        location_label = f"{place_name}, {country}" if country else place_name
        return (
            f"The weather in {location_label} is currently {description}, "
            f"{temp}\u00b0C, with {humidity}% humidity and wind speed of {wind} km/h, sir."
        )
    except requests.exceptions.RequestException:
        return "Sorry sir, I could not reach the weather service. Please check your internet connection."
    except Exception as e:
        print(f"[Weather Error]: {e}")
        return "Sorry sir, something went wrong while fetching the weather."
