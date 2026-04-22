# --- FULL VAWT PROJECT CODE: FIXED + DEPLOY READY ---

import streamlit as st

# ------------------ STREAMLIT INIT (MUST BE FIRST) ------------------

st.markdown("<h1>SWIFT</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Smart Wind Turbine with IoT and ML-based Feedback Tracking</div>", unsafe_allow_html=True)

# ------------------ IMPORTS ------------------

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import requests
import os

# ------------------ API KEY ------------------

API_KEY = os.getenv("API_KEY")  # set this in Render

# ------------------ WEATHER FUNCTION ------------------
def get_real_weather_smart(location_input):
    locations_to_try = [
        location_input,
        "Tagarapuvlasa",
        "Thagarapuvlasa",
        "Bheemunipatnam",
        "Visakhapatnam"
    ]

    locations_to_try = list(dict.fromkeys(locations_to_try))

    for city in locations_to_try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        try:
            response = requests.get(url, timeout=5)
            data = response.json()

            if data.get('cod') == 401:
                return "KEY_ERROR"

            if data.get('cod') == 200:
                return {
                    'temp': data['main']['temp'],
                    'pressure': data['main']['pressure'],
                    'humidity': data['main']['humidity'],
                    'wind': data['wind']['speed'],
                    'desc': data['weather'][0]['description'],
                    'name': data['name'],
                    'search_term': city
                }

        except:
            continue

    return None


# ------------------ MODEL (CACHED) ------------------

@st.cache_resource
def load_model():
    training_data = {
    'Temperature': [20, 25, 30, 15, 10, 35, 28, 22, 18, 12, 33, 29, 24, 21, 19],
    'Pressure': [1012, 1010, 1005, 1015, 1020, 1000, 1008, 1013, 1014, 1022, 1002, 1009, 1011, 1012, 1016],
    'Humidity': [60, 55, 45, 70, 80, 40, 50, 65, 68, 85, 42, 53, 58, 62, 75],
    'Wind_Speed': [3.5, 4.2, 6.5, 2.5, 1.5, 8.0, 5.2, 3.0, 2.8, 1.0, 7.5, 4.8, 3.9, 3.4, 2.6]
    }
    
    df = pd.DataFrame(training_data)
    X = df[['Temperature', 'Pressure', 'Humidity']]
    y = df['Wind_Speed']
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    return model


model = load_model()

# ------------------ UI ------------------

# CSS

st.markdown("""
<style>

/* Background */
body {
    background: linear-gradient(135deg, #0f172a, #020617);
}

/* Main container */
.main {
    background-color: transparent;
}

/* Title */
h1 {
    text-align: center;
    font-size: 42px;
    font-weight: 700;
    color: white;
    margin-bottom: 10px;
}

/* Subtitle */
.subtitle {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 30px;
}

/* Input box */
.stTextInput>div>div>input {
    background-color: #1e293b;
    color: white;
    border-radius: 10px;
    padding: 10px;
}

/* Button */
.stButton>button {
    background: linear-gradient(90deg, #3b82f6, #06b6d4);
    color: white;
    border-radius: 12px;
    padding: 10px 20px;
    font-weight: 600;
    border: none;
}

.stButton>button:hover {
    transform: scale(1.05);
}

/* Card */
.card {
    background: #111827;
    padding: 20px;
    border-radius: 16px;
    margin-top: 15px;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.4);
}

/* Section titles */
.card h3 {
    color: #38bdf8;
}

/* Metrics */
.metric {
    font-size: 18px;
    margin: 5px 0;
}

/* Status colors */
.green {
    color: #22c55e;
    font-weight: bold;
}

.red {
    color: #ef4444;
    font-weight: bold;
}

/* Loader box */
.info-box {
    background: #1e3a5f;
    padding: 12px;
    border-radius: 10px;
    margin-top: 10px;
    color: #93c5fd;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# Title


# Input

user_loc = st.text_input("📍 Enter Location", "Tagarapuvalasa")

if st.button("🚀 Get Live Data"):

    with st.spinner("Fetching real-time data..."):
        weather = get_real_weather_smart(user_loc)

    if weather == "KEY_ERROR":
        st.error("❌ API Key issue")

    elif weather is None:
        st.error("❌ Location not found")

    else:
        st.success("✅ Data fetched successfully")

        input_df = pd.DataFrame(
            [[weather['temp'], weather['pressure'], weather['humidity']]],
            columns=['Temperature', 'Pressure', 'Humidity']
        )

        predicted_wind = model.predict(input_df)[0]

        
   

    rho = 1.25
    area = 0.03125
    cp = 0.102

    power_watts = 0.5 * cp * rho * area * (predicted_wind ** 3)
    power_mw = power_watts * 1000
    

    
    # -------- MONTHLY GRAPH --------
    import numpy as np
    
    days = np.arange(1, 31)
    daily_power = power_watts + np.random.normal(0, power_watts * 0.1, size=30)
    
    df_power = pd.DataFrame({
        "Day": days,
        "Power (W)": daily_power
    })
    
    st.subheader("📊 Monthly Power Output")
    st.bar_chart(df_power.set_index("Day"))

    # Live Data
    st.markdown(f"""
    <div class="card">
        <h3>📊 Live Weather</h3>
        <p class="metric">🌡 Temp: {weather['temp']} °C</p>
        <p class="metric">💧 Humidity: {weather['humidity']} %</p>
        <p class="metric">🌬 Wind: {weather['wind']} m/s</p>
        <p class="metric">📈 Pressure: {weather['pressure']} hPa</p>
    </div>
    """, unsafe_allow_html=True)

    # AI
    st.markdown(f"""
    <div class="card">
        <h3>🧠 AI Prediction</h3>
        <p class="metric">Predicted Wind: {predicted_wind:.2f} m/s</p>
    </div>
    """, unsafe_allow_html=True)

    # Power
    status_color = "green" if predicted_wind > 3 else "red"
    status_text = "OPTIMAL" if predicted_wind > 3 else "LOW WIND"

    st.markdown(f"""
    <div class="card">
        <h3>⚡ Power Output</h3>
        <p class="metric">Power: {power_mw:.2f} mW</p>
        <p class="metric {status_color}">Status: {status_text}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style='position: fixed; bottom: 10px; right: 10px; 
    background-color: rgba(255,255,255,0.05); 
    padding: 8px 12px; border-radius: 10px; font-size: 12px; color: gray;'>
    
    NOTE: The entire UI is a demo. It does not show actual load values but displays predicted power outputs.
    
    </div>
    """, unsafe_allow_html=True)

