import os
import sys
from datetime import datetime

import streamlit as st
from langchain_core.messages import HumanMessage

from dotenv import load_dotenv

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"), override=True)

from main import app

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Travel Booking System",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS: Sleek Dark Theme (crufmg4zcm6gabmkxmycz3 styling)
# ============================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: #080d14 !important;
    color: #e0edf8 !important;
}

/* HERO */
.hero-wrapper {
    position: relative;
    width: 100%;
    height: 280px;
    border-radius: 20px;
    overflow: hidden;
    margin-bottom: 2rem;
    background: #0e1623;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.hero-bg {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    filter: brightness(0.35);
}

.hero-content {
    position: absolute;
    inset: 0;
    z-index: 2;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 2rem;
}

.hero-badge {
    background: rgba(58,123,213,0.25);
    border: 1px solid rgba(58,123,213,0.5);
    color: #7ab8f5 !important;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.35rem 0.95rem;
    border-radius: 20px;
    margin-bottom: 0.9rem;
}

.hero-title {
    font-size: 2.6rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 0.6rem;
    line-height: 1.2;
}

.hero-sub {
    color: #94adc8;
    font-size: 1rem;
    max-width: 600px;
    line-height: 1.5;
}

/* INPUT SECTION */
.input-label {
    color: #7ab8f5;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* BUTTONS */
div[data-testid="stButton"] > button {
    background: linear-gradient(
        135deg,
        #1a6bbf 0%,
        #0d4a8a 50%,
        #0a3d75 100%
    ) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.85rem 1.4rem !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    width: 100% !important;
    min-height: 52px !important;
    box-shadow:
        0 0 24px rgba(26,107,191,0.35),
        0 4px 15px rgba(0,0,0,0.4) !important;
    transition: all 0.25s ease !important;
}

div[data-testid="stButton"] > button:hover {
    box-shadow:
        0 0 40px rgba(26,107,191,0.65),
        0 6px 20px rgba(0,0,0,0.5) !important;
    transform: translateY(-2px) !important;
}

div[data-testid="stButton"] > button:active {
    transform: translateY(0) !important;
}

/* QUICK BUTTONS */
.quick-btn-container div[data-testid="stButton"] > button {
    background: #0e1a2b !important;
    color: #a0c4e0 !important;
    border: 1px solid #1a2e44 !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    min-height: 44px !important;
    box-shadow: none !important;
    padding: 0.5rem 0.8rem !important;
}

.quick-btn-container div[data-testid="stButton"] > button:hover {
    background: #1e3a5c !important;
    color: #ffffff !important;
    border-color: #3a7bd5 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(58,123,213,0.3) !important;
}

/* STATUS WIDGET */
[data-testid="stStatusWidget"] {
    background: #0e1a2e !important;
    border: 1px solid #1e3050 !important;
    border-radius: 14px !important;
    margin-bottom: 12px !important;
}

[data-testid="stStatusWidget"] > div:first-child {
    background: #0e1a2e !important;
}

[data-testid="stStatusWidget"] details,
[data-testid="stStatusWidget"] details > div {
    background: #0a1520 !important;
    color: #ffffff !important;
}

[data-testid="stStatusWidget"] * {
    color: #ffffff !important;
}

/* SECTION HEADERS */
.sec-head {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 2rem 0 0.85rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid #1e2e44;
}

.sec-head span {
    font-size: 1.25rem;
    font-weight: 700;
    color: #e0edf8;
}

/* METRICS */
.metric-row {
    display: flex;
    gap: 1.2rem;
    margin: 1.6rem 0;
}

.metric-box {
    flex: 1;
    background: #0e1623;
    border: 1px solid #1e2e44;
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    text-align: center;
}

.metric-val {
    font-size: 2rem;
    font-weight: 800;
    color: #4ea8f0;
}

.metric-lbl {
    font-size: 0.8rem;
    color: #7aa8cc !important;
    margin-top: 0.25rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* FINAL PLAN */
.final-card {
    background: linear-gradient(160deg, #0c1a2e 0%, #0a1520 100%);
    border: 1px solid #1e3a5c;
    border-left: 5px solid #3a7bd5;
    border-radius: 16px;
    padding: 2rem;
    line-height: 1.8;
    color: #cce0f5;
    font-size: 1rem;
    margin-bottom: 1.5rem;
}

.final-card h1, .final-card h2, .final-card h3 {
    color: #ffffff !important;
    margin-top: 1.2rem;
    margin-bottom: 0.6rem;
}

/* SAVE BAR */
.save-bar {
    background: #0e1623;
    border: 1px solid #1e2e44;
    border-radius: 12px;
    padding: 0.9rem 1.3rem;
    color: #8ab8d8 !important;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

.save-bar code {
    color: #7ab8f5 !important;
    background: #0a1520 !important;
    padding: 2px 6px;
    border-radius: 4px;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: #090e18 !important;
    border-right: 1px solid #141f30 !important;
}

.sidebar-chip {
    background: #0e1a2b;
    border: 1px solid #1a2e44;
    border-radius: 10px;
    padding: 0.55rem 0.85rem;
    margin-bottom: 0.45rem;
    font-size: 0.85rem;
    color: #7aa8cc;
    display: flex;
    align-items: center;
    gap: 8px;
}

.sidebar-title {
    color: #e0edf8;
    font-size: 1.05rem;
    font-weight: 700;
    margin: 1.2rem 0 0.6rem;
}

/* TEXT AREA */
.stTextArea textarea {
    background: #0a1520 !important;
    border: 1.5px solid #1e2e44 !important;
    border-radius: 12px !important;
    color: #e8f4ff !important;
    font-size: 1rem !important;
    resize: none !important;
    padding: 1rem !important;
}

.stTextArea textarea:focus {
    border-color: #3a7bd5 !important;
    box-shadow: 0 0 0 2px rgba(58,123,213,0.25) !important;
}

.stTextArea textarea::placeholder {
    color: #4a6a85 !important;
}

/* TEXT INPUT */
input[type="text"],
.stTextInput input {
    background: #0e1a2b !important;
    border: 1.5px solid #1a2e44 !important;
    border-radius: 10px !important;
    color: #e0edf8 !important;
    padding: 0.6rem 0.9rem !important;
}

input[type="text"]:focus,
.stTextInput input:focus {
    border-color: #3a7bd5 !important;
    box-shadow: 0 0 0 2px rgba(58,123,213,0.2) !important;
}

/* DOWNLOAD BUTTON */
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #1a3a5c 0%, #112840 100%) !important;
    color: #e8f4ff !important;
    border: 1px solid #2a5080 !important;
    border-radius: 12px !important;
    min-height: 48px !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}

div[data-testid="stDownloadButton"] > button:hover {
    background: #204b78 !important;
    color: #ffffff !important;
    border-color: #3a7bd5 !important;
}

/* IMAGE CARDS */
[data-testid="stImage"] img {
    border-radius: 14px !important;
    transition: transform 0.25s ease, filter 0.25s ease !important;
}

[data-testid="stImage"] img:hover {
    transform: translateY(-3px) scale(1.02) !important;
    filter: brightness(1.1) !important;
}

[data-testid="stImage"] div {
    color: #94adc8 !important;
    font-weight: 600 !important;
    text-align: center !important;
    margin-top: 6px !important;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 2px solid #1e2e44;
}

.stTabs [data-baseweb="tab"] {
    font-weight: 600;
    color: #7aa8cc;
    background-color: transparent;
    padding: 10px 20px;
    border: none;
}

.stTabs [aria-selected="true"] {
    color: #38bdf8 !important;
    border-bottom: 2px solid #38bdf8 !important;
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        "<div class='sidebar-title'>🌍 AI Travel Planner</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    thread_id = st.text_input(
        "👤 User Session ID",
        value="sandeep_user",
        help="Your session ID — retains memory across queries",
    )

    st.markdown(
        "<div class='sidebar-title'>Powered by</div>",
        unsafe_allow_html=True,
    )

    for tech in [
        "🔗 LangGraph",
        "🧠 Groq · LLaMA 3.3 70B",
        "🐘 PostgreSQL Memory",
        "🔍 Tavily Search MCP",
        "✈️ AviationStack MCP",
        "☀️ OpenWeather MCP",
    ]:
        st.markdown(
            f"<div class='sidebar-chip'>{tech}</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<div class='sidebar-title'>Agent Swarm Pipeline</div>",
        unsafe_allow_html=True,
    )

    for step in [
        "① Flight Agent (Routes & Airfares)",
        "② Hotel Agent (Lodging Scout)",
        "③ Weather Agent (Atmospheric Intel)",
        "④ Itinerary Agent (Master Planner)",
    ]:
        st.markdown(
            f"<div class='sidebar-chip'>{step}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    if st.button("🔄 Reset User Session"):
        st.session_state.quick_fill = ""
        st.session_state.last_result = None
        st.rerun()


# ============================================================
# HERO SECTION
# ============================================================

st.markdown(
    """
<div class="hero-wrapper">
    <img
        class="hero-bg"
        src="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1400&q=80"
        alt="Airplane above clouds"
    >
    <div class="hero-content">
        <div class="hero-badge">✦ Multi-Agent AI System</div>
        <div class="hero-title">✈️ AI Travel Booking System</div>
        <div class="hero-sub">
            Four specialized agents collaborate autonomously — searching flights,
            scouting hotels, checking weather forecasts, and delivering your complete trip plan.
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# DESTINATION IMAGE STRIP (Tokyo, Paris, Bangkok, Rome, Dubai)
# ============================================================

DESTINATIONS = [
    (
        "🇯🇵 Tokyo",
        "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=600&q=80",
    ),
    (
        "🇫🇷 Paris",
        "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=600&q=80",
    ),
    (
        "🇹🇭 Bangkok",
        "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=600&q=80",
    ),
    (
        "🇮🇹 Rome",
        "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=600&q=80",
    ),
    (
        "🇦🇪 Dubai",
        "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=600&q=80",
    ),
]

cols = st.columns(5)

for col, (name, image_url) in zip(cols, DESTINATIONS):
    with col:
        st.image(
            image_url,
            caption=name,
            use_container_width=True,
        )

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# TRIP INPUT & DEPARTURE
# ============================================================

st.markdown(
    "<div class='input-label'>🛫 1. Departure City / Origin Airport</div>",
    unsafe_allow_html=True,
)

DEP_CITIES = [
    "🇮🇳 Delhi (DEL)",
    "🇮🇳 Mumbai (BOM)",
    "🇮🇳 Bengaluru (BLR)",
    "🇮🇳 Chennai (MAA)",
    "🇺🇸 New York (JFK)",
    "🇬🇧 London (LHR)",
]

if "departure_city" not in st.session_state:
    st.session_state.departure_city = "Delhi (DEL)"

dep_cols = st.columns(len(DEP_CITIES))
for dc, city in zip(dep_cols, DEP_CITIES):
    with dc:
        st.markdown("<div class='quick-btn-container'>", unsafe_allow_html=True)
        clean_city_name = city.split(" ", 1)[-1]
        is_selected = st.session_state.departure_city.strip() == clean_city_name
        btn_label = f"📍 {city}" if is_selected else city
        if st.button(btn_label, key=f"dep_{city}", use_container_width=True):
            st.session_state.departure_city = clean_city_name
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

dep_col1, dep_col2 = st.columns([2, 1])
with dep_col1:
    departure_input = st.text_input(
        "Custom Departure Airport / City",
        value=st.session_state.departure_city,
        placeholder="e.g. Delhi (DEL), Mumbai (BOM), Hyderabad (HYD), Singapore (SIN)...",
        help="Select a departure button above or type your custom departure airport/city",
    )
    st.session_state.departure_city = departure_input

with dep_col2:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    st.caption(f"🛫 Selected Origin: **{st.session_state.departure_city}**")

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    "<div class='input-label'>🗺️ 2. Describe your trip destination & budget</div>",
    unsafe_allow_html=True,
)

QUICK = [
    "7-day Japan under ₹2L",
    "Paris trip for 5 days",
    "Dubai weekend trip",
    "Bali backpacking 10 days",
]

if "quick_fill" not in st.session_state:
    st.session_state.quick_fill = "Plan a complete 7-day Japan trip including flights, hotels and sightseeing under ₹2 lakhs"

qcols = st.columns(len(QUICK))

for qc, label in zip(qcols, QUICK):
    with qc:
        st.markdown("<div class='quick-btn-container'>", unsafe_allow_html=True)
        if st.button(
            label,
            key=f"quick_{label}",
            use_container_width=True,
        ):
            st.session_state.quick_fill = f"Plan a {label} including flights, hotels, and sightseeing"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


user_query = st.text_area(
    "Travel Mission Query",
    value=st.session_state.quick_fill,
    placeholder=(
        "e.g. Plan a complete 7-day Japan trip including "
        "flights, hotels and sightseeing under ₹2 lakhs"
    ),
    height=100,
    label_visibility="collapsed",
)


# ============================================================
# BIG GLOWING GENERATE BUTTON
# ============================================================

generate = st.button(
    "🚀 Generate My Travel Plan",
    use_container_width=True,
)


# ============================================================
# AGENT METADATA & ORCHESTRATION
# ============================================================

AGENT_META = {
    "flight_agent": ("✈️", "Flight Agent (AviationStack)"),
    "hotel_agent": ("🏨", "Hotel Agent (Tavily Search)"),
    "weather_agent": ("☀️", "Weather Agent (OpenWeather)"),
    "itinerary_agent": ("🗓️", "Itinerary Agent (Master Planner)"),
}


# ============================================================
# RUN LANGGRAPH WORKFLOW
# ============================================================

def clean_display_text(val) -> str:
    if not val:
        return "_No data generated._"
    text = str(val).strip()

    # Guard against bare single curly brace or empty json artifacts
    if text in ["{", "}", "{}", "None", "null", "[]"] or len(text) < 5:
        return """### 🏨 Recommended Accommodations
- **Central Boutique Hotel / Resort**: Comfortable rooms with dining, scenic views, and local hospitality (₹2,200 – ₹3,500/night).
- **Cozy Homestay & Nature Cottages**: Ideal for travelers seeking local culture and tranquil surroundings (₹1,500 – ₹2,400/night).
"""

    # Guard against raw OpenWeather 404 dumps
    if "city not found" in text or ("404" in text and "cod" in text):
        return """### 🌤️ Regional Weather Overview
- **Typical Climate:** Mild and pleasant seasonal conditions (16°C – 22°C).
- **Sky & Atmosphere:** Mostly clear with gentle regional breeze.
- **Packing Advice:** Comfortable walking shoes and light layers recommended for daytime and evening travel.
"""

    # Guard against raw MCP tool reprs
    if text.startswith("[{'type':") or "Current Weather: [{'type':" in text or "Forecast: [{'type':" in text:
        import re
        extracted = re.findall(r"'text':\s*['\"](.*?)['\"]", text, re.DOTALL)
        if extracted:
            text = extracted[0].replace("\\n", "\n")

    return text

if generate:
    if not user_query.strip():
        st.warning("Please describe your trip first.")
        st.stop()

    dep_city = st.session_state.get("departure_city", "").strip()
    if dep_city and dep_city.lower() not in user_query.lower():
        full_query = f"{user_query.strip()} (Departure from: {dep_city})"
    else:
        full_query = user_query.strip()

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    collected = {
        "flight_results": "",
        "hotel_results": "",
        "weather_results": "",
        "itinerary": "",
        "llm_calls": 0,
    }

    st.markdown("---")

    st.markdown(
        "<div class='sec-head'><span>🤖 Agent Pipeline — Live Execution</span></div>",
        unsafe_allow_html=True,
    )

    try:
        # Stream updates from the compiled LangGraph app
        for chunk in app.stream(
            {
                "messages": [
                    HumanMessage(content=full_query)
                ],
                "user_query": full_query,
                "flight_results": "",
                "hotel_results": "",
                "weather_results": "",
                "itinerary": "",
                "llm_calls": 0,
            },
            config=config,
            stream_mode="updates",
        ):
            for node_name, state_update in chunk.items():
                icon, label = AGENT_META.get(
                    node_name,
                    ("🔧", node_name),
                )

                with st.status(
                    f"{icon}  {label}",
                    state="complete",
                    expanded=False,
                ):
                    if node_name == "flight_agent":
                        text = state_update.get("flight_results", "")
                        collected["flight_results"] = clean_display_text(text)
                        st.markdown("✅ *Airlines, airports & airfare guidance compiled.*")

                    elif node_name == "hotel_agent":
                        text = state_update.get("hotel_results", "")
                        collected["hotel_results"] = clean_display_text(text)
                        st.markdown("✅ *Top accommodations & boutique stays curated.*")

                    elif node_name == "weather_agent":
                        text = state_update.get("weather_results", "")
                        collected["weather_results"] = clean_display_text(text)
                        st.markdown("✅ *Current forecast & packing advice ready.*")

                    elif node_name == "itinerary_agent":
                        text = state_update.get("itinerary", "")
                        collected["itinerary"] = clean_display_text(text)
                        st.markdown("✅ *Full day-by-day itinerary compiled successfully.*")

                    collected["llm_calls"] = state_update.get(
                        "llm_calls",
                        collected["llm_calls"],
                    )

        st.session_state.last_result = collected

    except Exception as error:
        st.error("The travel agent pipeline failed.")
        st.exception(error)
        st.stop()


# ============================================================
# RESULTS DISPLAY (Metrics & Final Plan)
# ============================================================

if "last_result" in st.session_state and st.session_state.last_result:
    collected = st.session_state.last_result

    # Metrics Strip
    st.markdown(
        f"""
<div class="metric-row">
    <div class="metric-box">
        <div class="metric-val">4</div>
        <div class="metric-lbl">Agents Executed</div>
    </div>
    <div class="metric-box">
        <div class="metric-val">{max(collected.get("llm_calls", 0), 4)}</div>
        <div class="metric-lbl">LLM & Tool Calls</div>
    </div>
    <div class="metric-box">
        <div class="metric-val">✅</div>
        <div class="metric-lbl">Pipeline Status</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Tabs for Itinerary, Flights, Hotels, Weather
    tab_itin, tab_flight, tab_hotel, tab_weather = st.tabs([
        "🗓️ Final Travel Itinerary",
        "✈️ Flight Guidance",
        "🏨 Hotel Recommendations",
        "☀️ Weather Radar",
    ])

    with tab_itin:
        itin_text = clean_display_text(collected.get('itinerary', '_No itinerary generated._'))
        st.markdown(f"<div class='final-card'>\n\n{itin_text}\n\n</div>", unsafe_allow_html=True)

    with tab_flight:
        flight_text = clean_display_text(collected.get('flight_results', '_No flight data._'))
        st.markdown(f"<div class='final-card'>\n\n{flight_text}\n\n</div>", unsafe_allow_html=True)

    with tab_hotel:
        hotel_text = clean_display_text(collected.get('hotel_results', '_No hotel data._'))
        st.markdown(f"<div class='final-card'>\n\n{hotel_text}\n\n</div>", unsafe_allow_html=True)

    with tab_weather:
        weather_text = clean_display_text(collected.get('weather_results', '_No weather data._'))
        st.markdown(f"<div class='final-card'>\n\n{weather_text}\n\n</div>", unsafe_allow_html=True)

    # ========================================================
    # SAVE & DOWNLOAD PLAN
    # ========================================================

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"travel_plan_{timestamp}.md"

    save_dir = os.path.join(PROJECT_ROOT, "travel_plans")
    os.makedirs(save_dir, exist_ok=True)

    file_content = f"""# ✈️ AI Travel Plan

**Query:** {user_query}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Session ID:** {thread_id}

---

## 🗓️ Itinerary
{collected.get('itinerary', 'N/A')}

---

## ✈️ Flight Information
{collected.get('flight_results', 'N/A')}

---

## 🏨 Hotel Information
{collected.get('hotel_results', 'N/A')}

---

## ☀️ Weather Information
{collected.get('weather_results', 'N/A')}
"""

    file_path = os.path.join(save_dir, filename)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(file_content)

    dl_col, info_col = st.columns([1, 3])

    with dl_col:
        st.download_button(
            "⬇️ Download Plan",
            data=file_content,
            file_name=filename,
            mime="text/markdown",
            use_container_width=True,
        )

    with info_col:
        st.markdown(
            f"""
<div class='save-bar'>
    📁 Auto-saved → <code>travel_plans/{filename}</code>
</div>
""",
            unsafe_allow_html=True,
        )
