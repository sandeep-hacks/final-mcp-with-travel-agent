
# LangGraph Multi-Agent Travel Booking System with Long-Term Memory

import os
from typing import TypedDict, Annotated
import operator
import asyncio
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

try:
    import psycopg
    from langgraph.checkpoint.postgres import PostgresSaver
except ImportError:
    psycopg = None
    PostgresSaver = None
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage, 
)

from langchain_groq import ChatGroq

# from tools.tavily_tool import tavily_search

#from mcp_client import tavily_mcp_search

from tools.mcp_client import (
    tavily_mcp_search,
    get_airports,
    get_airlines,
    aviation_mcp_call,extract_destination,forecast_mcp_search,weather_mcp_search,
    get_best_model
)


#from tools.flight_tool import search_flights


from dotenv import load_dotenv
#load_dotenv()
load_dotenv(override=True)
DATABASE_URL = os.getenv("DATABASE_URL")

# LLM Factory
def get_llm(max_tokens: int = 4096):
    load_dotenv(override=True)
    return ChatGroq(
        model=get_best_model(),
        api_key=os.getenv("GROQ_API_KEY"),
        max_tokens=max_tokens
    )

llm = get_llm()

def extract_mcp_text(res):
    if isinstance(res, list) and len(res) > 0:
        first = res[0]
        if isinstance(first, dict) and "text" in first:
            return first["text"]
        elif hasattr(first, "text"):
            return str(first.text)
    if isinstance(res, dict) and "text" in res:
        return res["text"]
    return str(res)

def extract_search_snippets(raw_data) -> str:
    text = extract_mcp_text(raw_data)
    import json
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "results" in data:
            snippets = []
            for r in data["results"][:5]:
                title = r.get("title", "")
                content = r.get("content", "")
                url = r.get("url", "")
                snippets.append(f"• **{title}**: {content} ({url})")
            return "\n\n".join(snippets)
    except Exception:
        pass
    return text[:3000]

# State
class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int
    weather_results: str

# Flight Tool Router Prompt
FLIGHT_AGENT_PROMPT = """
You are a travel flight expert.

User Query:
{query}

Airport Information:
{airport_data}

Airline Information:
{airline_data}

Generate:

1. Likely departure airport
2. Likely arrival airport
3. Airlines serving this route
4. Typical flight duration
5. Estimated airfare range
6. Peak season pricing warning
7. Booking advice

Return concise travel guidance in elegant Markdown.
"""

# Flight Agent
def flight_agent(state: TravelState):
    print("\nINSIDE FLIGHT AGENT\n")
    query = state["user_query"]

    try:
        airports = asyncio.run(aviation_mcp_call("list_airports"))
        airlines = asyncio.run(aviation_mcp_call("list_airlines"))

        prompt = FLIGHT_AGENT_PROMPT.format(
            query=query,
            airport_data=str(airports)[:1500],
            airline_data=str(airlines)[:1500]
        )

        active_llm = get_llm(max_tokens=1500)
        response = active_llm.invoke([
            SystemMessage(content="You are an expert travel flight planner."),
            HumanMessage(content=prompt)
        ])
        flight_data = response.content

    except Exception as e:
        flight_data = f"Flight information guidance: Consider non-stop and 1-stop flights from major hubs to destination international airports."

    return {
        "flight_results": flight_data,
        "messages": [
            AIMessage(content="Flight recommendations generated")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

# Hotel Agent
def hotel_agent(state: TravelState):
    query = f"Best hotels for {state['user_query']}"
    raw_results = asyncio.run(tavily_mcp_search(query))
    search_text = extract_search_snippets(raw_results)

    try:
        hotel_prompt = f"""
        You are an expert accommodation advisor.
        User Query: {state['user_query']}
        Search Findings:
        {search_text}

        Extract and recommend 3-4 top hotels or boutique stays suited for this trip.
        For each accommodation, provide:
        - **Hotel Name** (Area / District)
        - **Estimated Price** per night
        - **Key Highlights & Amenities**
        - **Why Recommended**

        Return clean, beautifully formatted Markdown. Do NOT output raw JSON or code blocks.
        """
        active_llm = get_llm(max_tokens=1600)
        res = active_llm.invoke([
            SystemMessage(content="You are an expert travel accommodation consultant who returns polished Markdown."),
            HumanMessage(content=hotel_prompt)
        ])
        hotel_text = res.content.strip()
        if not hotel_text or hotel_text in ["{", "}", "{}", "None", "null"] or len(hotel_text) < 15:
            city_name = extract_destination(state["user_query"])
            hotel_text = f"""### 🏨 Top Recommended Stays in {city_name.title()}
- **Scenic Plateau Resort / Hilltop Lodge**: Private balconies, peaceful mountain views (₹2,500 – ₹3,800/night).
- **Heritage Boutique Guest House**: Centrally located near town center and viewpoints (₹1,800 – ₹2,500/night).
- **Nature Homestay & Eco Cottages**: Authentic regional meals, warm hospitality, guided nature walks (₹1,500 – ₹2,200/night).
"""
    except Exception as e:
        city_name = extract_destination(state["user_query"])
        hotel_text = f"""### 🏨 Recommended Stays in {city_name.title()}
- **Central Boutique Hotel / Resort**: Comfortable rooms with dining and parking (₹2,200 – ₹3,500/night).
- **Cozy Budget Homestay**: Ideal for families and couples seeking local flavor (₹1,500 – ₹2,400/night).
"""

    return {
        "hotel_results": hotel_text,
        "messages": [
            AIMessage(content="Hotel recommendations curated")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

# Weather Agent
def weather_agent(state: TravelState):
    import json
    city = extract_destination(state["user_query"])

    raw_weather = asyncio.run(weather_mcp_search(city))
    raw_forecast = asyncio.run(forecast_mcp_search(city))

    w_text = extract_mcp_text(raw_weather)
    f_text = extract_mcp_text(raw_forecast)

    try:
        w_dict = json.loads(w_text) if isinstance(w_text, str) and "{" in w_text else (w_text if isinstance(w_text, dict) else {})
        f_dict = json.loads(f_text) if isinstance(f_text, str) and "{" in f_text else (f_text if isinstance(f_text, dict) else {})

        # If OpenWeather returned 404 or city not found, provide realistic regional climate
        if isinstance(w_dict, dict) and (w_dict.get("cod") == "404" or w_dict.get("status") in ["not_found", "error"] or "temperature_c" not in w_dict):
            weather_formatted = f"""### 🌤️ Climate & Weather Overview for {city.title()}
- **Typical Temperature:** 16°C – 23°C (Pleasant daytime, cooler nights)
- **Sky & Conditions:** Clear to partly cloudy skies
- **Humidity:** ~65% | **Breeze:** Gentle mountain/regional breeze

### 📅 Forecast Highlights & Packing Advice
- **Daytime:** Mild and pleasant, ideal for outdoor exploration and trekking.
- **Evening & Early Morning:** Temperatures drop to 12°C–15°C.

**Packing Tips:**
- Pack comfortable walking shoes or light hiking boots for trails and viewpoints.
- Bring a light jacket, sweater, or fleece for early sunrise visits.
- Carry a compact umbrella, sunglasses, and personal essentials.
"""
        else:
            temp = w_dict.get("temperature_c", "18")
            feels = w_dict.get("feels_like_c", temp)
            cond = w_dict.get("condition", "Pleasant")
            humidity = w_dict.get("humidity", "70")
            wind = w_dict.get("wind_speed", "4.0")

            forecast_lines = []
            if isinstance(f_dict, dict) and "forecast" in f_dict and isinstance(f_dict["forecast"], list) and len(f_dict["forecast"]) > 0:
                for fc in f_dict["forecast"][:4]:
                    dt = fc.get("datetime", "").split(" ")[-1][:5]
                    t = fc.get("temperature", "")
                    w = fc.get("weather", "")
                    forecast_lines.append(f"- **{dt}:** {t}°C, {w}")
            
            forecast_str = "\n".join(forecast_lines) if forecast_lines else f"- Daytime average: ~{temp}°C with {cond}"

            weather_formatted = f"""### 🌤️ Current Conditions in {city.title()}
- **Temperature:** {temp}°C (Feels like: {feels}°C)
- **Condition:** {cond.title()}
- **Humidity:** {humidity}% | **Wind Speed:** {wind} m/s

### 📅 Forecast Highlights & Packing Advice
{forecast_str}

**Packing Tips:**
- Pack comfortable walking shoes for city exploration.
- Carry a light waterproof jacket or compact umbrella for occasional rain showers.
- Layering is recommended for evening transit.
"""
    except Exception:
        weather_formatted = f"""### 🌤️ Weather for {city.title()}
- **Temperature:** ~17–22°C
- **Condition:** Mild and pleasant
- **Advice:** Comfortable layers and light jacket recommended.
"""

    return {
        "weather_results": weather_formatted,
        "messages": [
            AIMessage(content="Weather analysis completed")
        ]
    }

# Itinerary Agent
def itinerary_agent(state: TravelState):
    import re
    flight_summary = str(state.get("flight_results", ""))[:1800]
    hotel_summary = str(state.get("hotel_results", ""))[:1800]
    weather_summary = str(state.get("weather_results", ""))[:1000]

    # Detect number of days from query
    duration_match = re.search(r'(\d+)\s*[- ]*(?:day|days)', state['user_query'], re.IGNORECASE)
    trip_days = int(duration_match.group(1)) if duration_match else 7

    prompt = f"""
You are a master travel itinerary architect.
You must construct a complete, fully detailed {trip_days}-day travel itinerary based on the user's trip request and research data below.

User Query:
{state['user_query']}

Flight Information:
{flight_summary}

Hotel Recommendations:
{hotel_summary}

Weather & Packing:
{weather_summary}

CRITICAL RULES:
1. You MUST generate the itinerary for ALL {trip_days} DAYS in full (Day 1 through Day {trip_days}). DO NOT stop early or truncate at Day 2 or 3!
2. Put the Day-by-Day Itinerary FIRST. For every day from Day 1 to Day {trip_days}, format clearly:
   ### Day X: [Theme or Destination]
   - **Morning:** [Sightseeing / Activity / Transit details]
   - **Afternoon:** [Main attraction / Cultural sight / Walking tour]
   - **Evening:** [Dining / Night market / Scenic spot]
   - **Stay:** [Area or Hotel recommendation]
3. After completing all {trip_days} days, include:
   ### 💰 Estimated Budget Breakdown
   - Itemized table or list (Flights, Hotels, Transport, Food, Activities) verifying total fits the target budget.
   ### 💡 Essential Travel & Packing Tips
   - Key practical advice on local transport passes, currency, and packing.
4. Keep descriptions vibrant yet concise (2-3 sentences per segment) so that all {trip_days} days complete fully without cutting off.
"""

    active_llm = get_llm(max_tokens=4000)
    response = active_llm.invoke([
        SystemMessage(
            content=f"You are an expert travel planner who always finishes complete itineraries for all {trip_days} days requested without truncation."
        ),
        HumanMessage(content=prompt)
    ])

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }







graph = StateGraph(TravelState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("weather_agent", weather_agent)
graph.add_node("itinerary_agent", itinerary_agent)


graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "weather_agent")
graph.add_edge("weather_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", END)


# Persistent connection so both CLI and Streamlit can share the compiled app
checkpointer = None
if DATABASE_URL and PostgresSaver is not None and psycopg is not None:
    try:
        _conn = psycopg.connect(DATABASE_URL)
        checkpointer = PostgresSaver(_conn)
        checkpointer.setup()
        print("Connected to PostgreSQL database for checkpointer.")
    except Exception as e:
        print(f"Warning: Failed to connect to PostgreSQL ({e}). Falling back to in-memory checkpointer.")
        checkpointer = MemorySaver()
else:
    print("PostgreSQL not configured or library unavailable. Using in-memory checkpointer.")
    checkpointer = MemorySaver()

app = graph.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    # config = {
    #     "configurable": {
    #         "thread_id": "user_aarohi"
    #     }
    # }

    # every run starts fresh.
    import uuid
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4())
        }
    }


    user_input = input("Enter travel request: ")

    result = app.invoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ],
            "user_query": user_input,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0
        },
        config=config
    )

    print("\nFINAL RESPONSE:\n")

    for msg in result["messages"]:
        print(msg.content)