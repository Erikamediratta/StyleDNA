from langchain_groq import ChatGroq

# ChatGoogleGenerativeAI → LangChain's wrapper
#                          around Gemini

# WHY do we need this instead of regular genai?
# → LangChain needs a STANDARDISED way
#   to talk to ANY AI model
# → this wrapper makes Gemini "speak"
#   LangChain's language

from langchain.agents import create_react_agent,AgentExecutor
import os
from dotenv import load_dotenv
from langchain import hub

#hub is a langchain's library with proven prompt templates
#we use this so we need not right reAct agent prompt


from tools.style_tool import get_style_advice
from tools.wardrobe_tool import get_wardrobe
from tools.weather_tool import get_weather


load_dotenv()

llm=ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7
)
tools=[get_weather,get_wardrobe,get_style_advice]

prompt=hub.pull("hwchase17/react")


# "hwchase17/react" → this is the EXACT name
#                     of a famous, battle-tested
#                     ReAct prompt template
#                     made by LangChain's creator

# This prompt CONTAINS instructions like:
# "Think step by step.
#  Use this format:
#  Thought: ...
#  Action: ...
#  Observation: ...
#  Final Answer: ..."

agent=create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)
#agent is a configured agent, not running yet,just configured

agent_executor=AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=6,
    
    #stop after 3 tool calls, prevents infinite loop, if agent gets stuck
)

def ask_style_agent(question, jwt_token, user_city, chat_history=None):
    # Make JWT available to tools
    os.environ["USER_JWT"] = jwt_token

    # Build conversation history
    history_text = ""
    if chat_history:
        for msg in chat_history[-6:]:  # Last 3 user-assistant exchanges
            role = "User" if msg["role"] == "user" else "Stylist"
            history_text += f"{role}: {msg['content']}\n"

    # Build prompt for the agent
    full_question = f"""
The user lives in {user_city}. 

Previous conversation:
{history_text}

New question:
{question}
"""

    try:
        result = agent_executor.invoke({
            "input": full_question
        })
        print("=" * 50)
        print("RAW RESULT:", result)
        print("=" * 50)
        return result["output"]
    except Exception as e:
        print("=" * 50)
        print("AGENT EXCEPTION CAUGHT:", repr(e))
        print("=" * 50)
        return "The AI service is currently experiencing high demand. Please try again in a few moments."

    
        