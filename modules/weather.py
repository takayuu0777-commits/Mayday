from datetime import datetime, timedelta
import threading

import requests


LAT = 34.661
LON = 135.451
CITY_NAME = "大阪市港区"

CACHE_MINUTES = 10

_weather_cache = {
    "data": None,
    "expires_at": None
}

_cache_lock = threading.Lock()


def weather_info(code):
    table = {
        0: {"text": "快晴", "icon": "☀️"},
        1: {"text": "晴れ", "icon": "🌤️"},
        2: {"text": "晴れ時々曇り", "icon": "⛅"},
        3: {"text": "曇り", "icon": "☁️"},

        45: {"text": "霧", "icon": "🌫️"},
        48: {"text": "霧氷", "icon": "🌫️"},

        51: {"text": "弱い霧雨", "icon": "🌦️"},
        53: {"text": "霧雨", "icon": "🌦️"},
        55: {"text": "強い霧雨", "icon": "🌧️"},

        56: {"text": "凍る霧雨", "icon": "🌧️"},
        57: {"text": "強い凍る霧雨", "icon": "🌧️"},

        61: {"text": "小雨", "icon": "🌦️"},
        63: {"text": "雨", "icon": "🌧️"},
        65: {"text": "強い雨", "icon": "🌧️"},

        66: {"text": "凍る雨", "icon": "🌧️"},
        67: {"text": "強い凍る雨", "icon": "🌧️"},

        71: {"text": "小雪", "icon": "🌨️"},
        73: {"text": "雪", "icon": "❄️"},
        75: {"text": "大雪", "icon": "❄️"},
        77: {"text": "細かい雪", "icon": "🌨️"},

        80: {"text": "弱いにわか雨", "icon": "🌦️"},
        81: {"text": "にわか雨", "icon": "🌧️"},
        82: {"text": "激しいにわか雨", "icon": "⛈️"},

        85: {"text": "弱いにわか雪", "icon": "🌨️"},
        86: {"text": "強いにわか雪", "icon": "❄️"},

        95: {"text": "雷雨", "icon": "⛈️"},
        96: {"text": "ひょうを伴う雷雨", "icon": "⛈️"},
        99: {"text": "強いひょうを伴う雷雨", "icon": "⛈️"}
    }

    return table.get(
        code,
        {
            "text": "不明",
            "icon": "❓"
        }
    )


def format_temperature(value):
    if value is None:
        return "--℃"

    try:
        return f"{round(float(value), 1)}℃"
    except (TypeError, ValueError):
        return "--℃"


def format_percent(value):
    if value is None:
        return "--%"

    try:
        return f"{round(float(value))}%"
    except (TypeError, ValueError):
        return "--%"


def format_hour_label(time_text):
    try:
        parsed = datetime.fromisoformat(time_text)
        return parsed.strftime("%H:%M")
    except (TypeError, ValueError):
        return "--:--"


def format_day_label(date_text, index):
    if index == 0:
        return "今日"

    if index == 1:
        return "明日"

    try:
        parsed = datetime.strptime(date_text, "%Y-%m-%d")

        weekdays = [
            "月",
            "火",
            "水",
            "木",
            "金",
            "土",
            "日"
        ]

        return (
            f"{parsed.month}/{parsed.day}"
            f"（{weekdays[parsed.weekday()]}）"
        )

    except (TypeError, ValueError):
        return date_text or "不明"


def build_fallback_weather(message="天気を取得できませんでした"):
    return {
        "summary": {
            "city": CITY_NAME,
            "location": CITY_NAME,

            "temperature": "--℃",

            "description": message,
            "condition": message,

            "rain": "--%",
            "high": "--℃",
            "low": "--℃",

            "humidity": "--%",
            "wind": "-- km/h",

            "icon": "❓",
            "updated_at": "--:--",
            "is_error": True
        },

        "hourly": [],

        "weekly": [],

        "error": message
    }


def fetch_weather_from_api():
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": LAT,
        "longitude": LON,

        "current": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "weather_code",
            "wind_speed_10m"
        ]),

        "hourly": ",".join([
            "temperature_2m",
            "precipitation_probability",
            "weather_code"
        ]),

        "daily": ",".join([
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_max"
        ]),

        "forecast_days": 7,
        "timezone": "Asia/Tokyo"
    }

    response = requests.get(
        url,
        params=params,
        timeout=8
    )

    response.raise_for_status()

    data = response.json()

    current = data.get("current", {})
    hourly = data.get("hourly", {})
    daily = data.get("daily", {})

    current_code = current.get("weather_code")
    current_weather = weather_info(current_code)

    current_time_text = current.get("time")

    try:
        current_time = datetime.fromisoformat(current_time_text)
    except (TypeError, ValueError):
        current_time = datetime.now()

    daily_highs = daily.get("temperature_2m_max", [])
    daily_lows = daily.get("temperature_2m_min", [])
    daily_rains = daily.get("precipitation_probability_max", [])

    today_high = daily_highs[0] if daily_highs else None
    today_low = daily_lows[0] if daily_lows else None
    today_rain = daily_rains[0] if daily_rains else None

    summary = {
        "city": CITY_NAME,
        "location": CITY_NAME,

        "temperature": format_temperature(
            current.get("temperature_2m")
        ),

        "feels_like": format_temperature(
            current.get("apparent_temperature")
        ),

        "description": current_weather["text"],
        "condition": current_weather["text"],

        "icon": current_weather["icon"],

        "rain": format_percent(today_rain),

        "high": format_temperature(today_high),
        "low": format_temperature(today_low),

        "humidity": format_percent(
            current.get("relative_humidity_2m")
        ),

        "wind": (
            f"{round(float(current.get('wind_speed_10m')), 1)} km/h"
            if current.get("wind_speed_10m") is not None
            else "-- km/h"
        ),

        "updated_at": current_time.strftime("%H:%M"),
        "is_error": False
    }

    hourly_times = hourly.get("time", [])
    hourly_temperatures = hourly.get("temperature_2m", [])
    hourly_rains = hourly.get("precipitation_probability", [])
    hourly_codes = hourly.get("weather_code", [])

    hourly_result = []

    for index, time_text in enumerate(hourly_times):
        try:
            forecast_time = datetime.fromisoformat(time_text)
        except (TypeError, ValueError):
            continue

        if forecast_time < current_time.replace(
            minute=0,
            second=0,
            microsecond=0
        ):
            continue

        code = (
            hourly_codes[index]
            if index < len(hourly_codes)
            else None
        )

        info = weather_info(code)

        temperature = (
            hourly_temperatures[index]
            if index < len(hourly_temperatures)
            else None
        )

        rain = (
            hourly_rains[index]
            if index < len(hourly_rains)
            else None
        )

        hourly_result.append({
            "time": format_hour_label(time_text),
            "icon": info["icon"],
            "condition": info["text"],
            "temperature": format_temperature(temperature),
            "temp": format_temperature(temperature),
            "rain": format_percent(rain)
        })

        if len(hourly_result) >= 24:
            break

    daily_dates = daily.get("time", [])
    daily_codes = daily.get("weather_code", [])

    weekly_result = []

    for index, date_text in enumerate(daily_dates):
        code = (
            daily_codes[index]
            if index < len(daily_codes)
            else None
        )

        info = weather_info(code)

        high = (
            daily_highs[index]
            if index < len(daily_highs)
            else None
        )

        low = (
            daily_lows[index]
            if index < len(daily_lows)
            else None
        )

        rain = (
            daily_rains[index]
            if index < len(daily_rains)
            else None
        )

        weekly_result.append({
            "date": date_text,
            "day": format_day_label(date_text, index),
            "icon": info["icon"],
            "condition": info["text"],
            "high": format_temperature(high),
            "low": format_temperature(low),
            "rain": format_percent(rain)
        })

    return {
        "summary": summary,
        "hourly": hourly_result,
        "weekly": weekly_result,
        "error": None
    }


def fetch_weather(force_refresh=False):
    now = datetime.now()

    with _cache_lock:
        cached_data = _weather_cache["data"]
        expires_at = _weather_cache["expires_at"]

        if (
            not force_refresh
            and cached_data is not None
            and expires_at is not None
            and now < expires_at
        ):
            return cached_data

    try:
        weather_data = fetch_weather_from_api()

    except requests.RequestException:
        with _cache_lock:
            if _weather_cache["data"] is not None:
                return _weather_cache["data"]

        weather_data = build_fallback_weather(
            "天気サービスに接続できませんでした"
        )

    except (KeyError, TypeError, ValueError):
        with _cache_lock:
            if _weather_cache["data"] is not None:
                return _weather_cache["data"]

        weather_data = build_fallback_weather(
            "天気データを読み取れませんでした"
        )

    with _cache_lock:
        _weather_cache["data"] = weather_data
        _weather_cache["expires_at"] = (
            now + timedelta(minutes=CACHE_MINUTES)
        )

    return weather_data


def weather_summary():
    return fetch_weather()["summary"]


def hourly_forecast():
    return fetch_weather()["hourly"]


def weekly_forecast():
    return fetch_weather()["weekly"]