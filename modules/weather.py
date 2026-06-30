def weather_summary():
    return {
        "location": "大阪市港区",
        "icon": "🌤",
        "temperature": "未設定",
        "condition": "天気API準備中",
        "rain": "未設定",
        "high": "未設定",
        "low": "未設定"
    }


def hourly_forecast():
    return [
        {"time": "朝", "icon": "🌤", "temp": "未設定"},
        {"time": "昼", "icon": "☀️", "temp": "未設定"},
        {"time": "夕方", "icon": "🌥", "temp": "未設定"},
        {"time": "夜", "icon": "🌙", "temp": "未設定"}
    ]


def weekly_forecast():
    return [
        {"day": "今日", "icon": "🌤", "high": "未設定", "low": "未設定"},
        {"day": "明日", "icon": "🌥", "high": "未設定", "low": "未設定"},
        {"day": "明後日", "icon": "☁️", "high": "未設定", "low": "未設定"}
    ]