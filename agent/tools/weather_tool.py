import os
from langchain.tools import tool
from dotenv import load_dotenv
import requests

load_dotenv()

@tool
def get_weather(city:str="Delhi")->str:
    #Delhi is default
    # -> str means the function will finally return a string 
    """Get current weather for a city.
    Use it when you need to know the weather for making outfit recommendation
    """

    try:
        city = city.replace("city=", "").replace("'", "").replace('"', "").strip()
        api_key=os.getenv("OPENWEATHER_API_KEY")
        url=url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

        response=requests.get(url)
        data=response.json()
        #python converts the json response into dictionary using response.json()

        temp=data["main"]["temp"]
        feels_like=data["main"]["feels_like"]
        description=data["weather"][0]["description"]
        humidity=data["main"]["humidity"]

        return f"""
        City:{city}
        Temperature:{temp} degrees (feels like {feels_like})
        Weather:{description}
        Humidity:{humidity}%
        """
    
    except Exception as e:
        print("Weather Tool Error:", e)
        return f"Could not get weather for {city}"