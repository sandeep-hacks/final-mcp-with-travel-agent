# pip install mcp requests

from mcp.server.fastmcp import FastMCP
import requests
import os

from dotenv import load_dotenv
load_dotenv()

mcp = FastMCP("Weather Server")


OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

@mcp.tool()
def get_current_weather(city: str):

    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
    )

    data = response.json()

    if response.status_code != 200 or "main" not in data:
        return {
            "status": "not_found",
            "city": city,
            "message": data.get("message", "Weather data unavailable")
        }

    return {
        "city": data.get("name", city),
        "temperature_c": data["main"]["temp"],
        "feels_like_c": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"] if "weather" in data and len(data["weather"]) > 0 else "clear",
        "wind_speed": data["wind"]["speed"] if "wind" in data else 0
    }



@mcp.tool()
def get_forecast(city: str):

    url = (
        "https://api.openweathermap.org/data/2.5/forecast"
    )

    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )
        data = response.json()

        if response.status_code != 200 or "list" not in data:
            return {
                "status": "not_found",
                "city": city,
                "forecast": []
            }

        forecast = []
        for item in data.get("list", [])[:5]:
            forecast.append(
                {
                    "datetime": item.get("dt_txt", ""),
                    "temperature": item.get("main", {}).get("temp", "N/A"),
                    "weather": item.get("weather", [{}])[0].get("description", "clear")
                }
            )

        return {
            "city": city,
            "forecast": forecast
        }
    except Exception as e:
        return {
            "status": "error",
            "city": city,
            "forecast": []
        }




if __name__ == "__main__":
    mcp.run()