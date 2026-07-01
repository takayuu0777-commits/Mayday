import requests

LAT = 34.661
LON = 135.451


def weather_text(code):
    table = {
        0: "快晴",
        1: "晴れ",
        2: "晴れ時々曇り",
        3: "曇り",
        45: "霧",
        51: "小雨",
        61: "雨",
        71: "雪",
        80: "にわか雨",
        95: "雷雨"
    }

    return table.get(code, "不明")


def fetch_weather():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}"
        f"&longitude={LON}"
        "&current=temperature_2m,weather_code"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
        "&timezone=Asia%2FTokyo"
    )

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        current = data["current"]
        daily = data["daily"]

        return {
            "city": "大阪市港区",
            "temperature": f"{current['temperature_2m']}℃",
            "description": weather_text(current["weather_code"]),
            "rain": f"{daily['precipitation_probability_max'][0]}%",
            "high": f"{daily['temperature_2m_max'][0]}℃",
            "low": f"{daily['temperature_2m_min'][0]}℃",
            "icon": "🌤"
        }

    except Exception:
        return {
            "city": "大阪市港区",
            "temperature": "--℃",
            "description": "取得失敗",
            "rain": "--%",
            "high": "--℃",
            "low": "--℃",
            "icon": "❓"
        }


def weather_summary():
    return fetch_weather()


def hourly_forecast():
    return []


def weekly_forecast():
    return []