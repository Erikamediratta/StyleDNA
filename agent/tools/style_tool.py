import requests
import os
from groq import Groq
from dotenv import load_dotenv
from langchain.tools import tool
import ast

load_dotenv()

client=Groq(api_key=os.getenv("GROQ_API_KEY"))

@tool
def get_style_advice(context:str)->str:
    """Get expert fashion styling tips and advices.
    Use this when you have weather and wardrobe information to get professional styling recommendation"
    on how to combine items, color matching, and styling tips."""

    try:
           # if agent passed a dict-like string, extract just the text
        if context.strip().startswith("{"):
            try:
                parsed = ast.literal_eval(context)
                if isinstance(parsed, dict):
                    context = str(parsed.get("context", context))
            except:
                pass
        prompt=f"""
        You are an expert fashion stylist with professional experience in styling.property

        Context:{context}
        Give specific styling advice in this format:
        Recommended Outfit:[combination of items]
        Why this outfit works: Give concide answer in 2-3 lines
        Styling tips: Give 2-3 practical styling tips
        """

        response=client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":prompt}]
        )
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error getting style advice: {str(e)}"
    

# LangChain agents communicate using STRINGS only

# Agent tools:
# INPUT  → always strings (or simple types)
# OUTPUT → always strings

# Why? Because the agent's "brain" (Gemini)
# reads TEXT, not Python objects

# Gemini can't understand:
# [{"name": "shirt", "color": "white"}]

# Gemini CAN understand:
# "White shirt, white color, work occasion"