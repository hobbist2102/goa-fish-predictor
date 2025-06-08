# 🌿 Goa Fish Predictor

**Physics-first fishing prediction system for Goa**
Uses live data — no catch logs required — to recommend the best species, tactics, and times to fish.

---

## 🌍 Live Environmental Intelligence

The model pulls real-time data from:

* **🌡️ Sea Surface Temperature (SST)** — via [CMEMS](https://marine.copernicus.eu/)
* **🌊 Tide Height** — via [INCOIS Tide Forecast](https://www.incois.gov.in/portal/ptidestext.jsp)
* **🌤️ Weather & Pressure** — via [OpenWeatherMap](https://openweathermap.org/)
* **🌙 Moon Phase** — approximated via astronomical model

---

## 🎯 What It Predicts

For any location in Goa (15.5°N, 73.8°E) and a time of your choice, it computes:

* ✅ Fish Activity Index (FAI)
* ✅ Top 3 target species (seasonally & environmentally accurate)
* ✅ Tactical playbook:

  * Best natural bait
  * Ideal lures and retrieve styles
  * Recommended rigs
  * Water column and habitat targeting

---

## 🧠 Powered by Biological Knowledge

The app uses a detailed `species.json` file built from:

* Local feeding patterns
* Moon & tide spawning behavior
* Seasonal migration cycles
* Pressure and turbidity triggers

No AI hallucinations. Only clean logic and real oceanography.

---

## 📦 How to Run Locally

1. Clone the repo:

   ```bash
   git clone https://github.com/hobbist2102/goa-fish-predictor.git
   cd goa-fish-predictor
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Add your secrets:
   Create a `.streamlit/secrets.toml` with:

   ```toml
   openweathermap_key = "your_owm_api_key"
   CMEMS_USER = "your_cmems_username"
   CMEMS_PASS = "your_cmems_password"
   ```

4. Run the app:

   ```bash
   streamlit run streamlit_app.py
   ```

---

## 📸 Screenshots

*Optional: add screenshots or demo gifs here.*

---

## 👨‍💻 Built By

**Abhishek Mehta** – [@hobbist2102](https://github.com/hobbist2102)
Open-source for marine research and conservation awareness 🐠

---

## 🪄 Coming Soon

* Goa location picker (estuary vs reef vs river mouth)
* Real-time map overlays
* Tactic simulator for beginners
