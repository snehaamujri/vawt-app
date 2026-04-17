# --- FULL VAWT PROJECT CODE: FIXED + DEPLOY READY ---

import streamlit as st

# ------------------ STREAMLIT INIT (MUST BE FIRST) ------------------

st.set_page_config(page_title="VAWT AI Bot", page_icon="🌪️", layout="centered")

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
    "Tagarapuvalasa",
    "Thagarapuvalasa",
    "Bheemunipatnam",
    "Visakhapatnam"
    ]
    
    ```
    locations_to_try = list(dict.fromkeys(locations_to_try))
    
    for city in locations_to_try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
    
            if data['cod'] == 401:
                return "KEY_ERROR"
    
            if data['cod'] == 200:
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
```


# ------------------ MODEL (CACHED) ------------------

@st.cache_resource
def load_model():
training_data = {
'Temperature': [20, 25, 30, 15, 10, 35, 28, 22, 18, 12, 33, 29, 24, 21, 19],
'Pressure': [1012, 1010, 1005, 1015, 1020, 1000, 1008, 1013, 1014, 1022, 1002, 1009, 1011, 1012, 1016],
'Humidity': [60, 55, 45, 70, 80, 40, 50, 65, 68, 85, 42, 53, 58, 62, 75],
'Wind_Speed': [3.5, 4.2, 6.5, 2.5, 1.5, 8.0, 5.2, 3.0, 2.8, 1.0, 7.5, 4.8, 3.9, 3.4, 2.6]
}

```
df = pd.DataFrame(training_data)
X = df[['Temperature', 'Pressure', 'Humidity']]
y = df['Wind_Speed']

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

return model
```

model = load_model()

# ------------------ UI ------------------

# CSS

st.markdown("""

<style>
body { background-color: #0e1117; }
.main { background-color: #0e1117; }
h1 { text-align: center; color: white; }
.card {
    background-color: #161b22;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 15px;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.4);
}
.metric { font-size: 20px; font-weight: bold; }
.green { color: #00ff9f; }
.red { color: #ff4b4b; }
</style>

""", unsafe_allow_html=True)

# Title

st.markdown("<h1>🌪️ VAWT AI Weather & Power Bot</h1>", unsafe_allow_html=True)

# Input

user_loc = st.text_input("📍 Enter Location", "Tagarapuvalasa")

if st.button("🚀 Get Live Data"):

```
st.info("Fetching real-time data...")

weather = get_real_weather_smart(user_loc)

if weather == "KEY_ERROR":
    st.error("❌ API Key issue")
elif weather is None:
    st.error("❌ Location not found")
else:
    input_df = pd.DataFrame([[weather['temp'], weather['pressure'], weather['humidity']]],
                            columns=['Temperature', 'Pressure', 'Humidity'])

    predicted_wind = model.predict(input_df)[0]

    rho = 1.25
    area = 0.03125
    cp = 0.102

    power_watts = 0.5 * cp * rho * area * (predicted_wind ** 3)
    power_mw = power_watts * 1000

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
```
