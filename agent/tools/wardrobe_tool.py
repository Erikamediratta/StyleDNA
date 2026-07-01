import requests
import os
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")

@tool
def get_wardrobe(occasion: str = "", season: str = "") -> str:
    """Get the user's wardrobe items from the database.
    Use this when you need to know what clothes the user owns
    to make outfit recommendations.
    """
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/wardrobe",
            cookies={"jwt": os.getenv("USER_JWT", "")}
        )
        
        if response.status_code != 200:
            return "Could not fetch wardrobe. User might not be logged in."
        
        items = response.json()
        
        if not items:
            return "Wardrobe is empty. Skip get_wardrobe. Call get_style_advice next with context noting no wardrobe items exist, to give general starter outfit suggestions."
        filtered = items
        
        if occasion:
            new_filtered = []

            for i in filtered:
                item_occasion = i.get("occasion", "")

                if occasion.lower() in item_occasion.lower():
                    new_filtered.append(i)

            filtered = new_filtered
        
        if season:
            filtered = [i for i in filtered if i.get("season", "all") in [season.lower(), "all"]]
        
        if not filtered:
            filtered = items
        
        result = "User's wardrobe:\n"

        for item in filtered:

            emoji = item.get("emoji", "👕")
            name = item["name"]
            category = item["category"]
            color = item["color"]
            occasion = item.get("occasion", "any")
            season = item.get("season", "all")

            result += (
                f"- {emoji} {name} "
                f"({category}, {color}, "
                f"occasion: {occasion}, "
                f"season: {season})\n"
    )
        return result
    
    except Exception as e:
        return f"Error fetching wardrobe: {str(e)}"

      