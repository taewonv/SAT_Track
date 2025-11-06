# 🛰️ NEONSAT TLE Tracker

Predict satellite orbits by loading TLE data using **NEON SAT’s NORAD ID (59587)**.

<img width="998" height="596" alt="image" src="https://github.com/user-attachments/assets/cb864e90-51aa-4829-8481-909ca6ec3348" />


## 🚀 Features
- Auto-fetch latest TLE from Celestrak
- Propagate orbit using SGP4
- Visualize ground track on world map

## 🧩 How to Run
```bash
pip install sgp4 cartopy requests matplotlib
python NEONSAT_TLE_PREDICT.py
