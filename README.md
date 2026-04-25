# WindyAI — Smart Travel Planner

WindyAI is a Streamlit web app that helps you plan trips around Ho Chi Minh City. It combines route optimization, turn-by-turn navigation, AI landmark recognition, weather forecasting, place recommendations, and a Gemini-powered chatbot — all in one interface.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Clone the Repository](#2-clone-the-repository)
3. [Set Up a Virtual Environment](#3-set-up-a-virtual-environment)
4. [Install Dependencies](#4-install-dependencies)
5. [Configure API Keys & Environment Variables](#5-configure-api-keys--environment-variables)
6. [Set Up the Database (Supabase)](#6-set-up-the-database-supabase)
7. [Run the App](#7-run-the-app)
8. [Using the App](#8-using-the-app)
9. [Project Structure](#9-project-structure)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.12+ | Check with `python --version` |
| pip | latest | Comes with Python |
| Git | any | To clone the repo |
| Internet connection | — | Required for maps, weather, and AI features |

---

## 2. Clone the Repository

```bash
git clone <your-repo-url>
cd <repo-folder>
```

Make sure you are in the **project root** (the folder that contains `requirements.txt` and the `app/` directory) for all commands below.

---

## 3. Set Up a Virtual Environment

Using a virtual environment keeps the project's dependencies isolated from your system Python.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt once it's active.

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs everything the app needs, including Streamlit, PyTorch, and the Supabase client.

> **Heads-up on PyTorch:** `torch` and `torchvision` are large packages (~1–2 GB). If the install stalls or fails on Windows, install PyTorch separately first using the official command from [pytorch.org/get-started](https://pytorch.org/get-started/locally/), then re-run `pip install -r requirements.txt`.

> **Heads-up on `psycopg2-binary`:** If you get a build error on Windows, try `pip install psycopg2-binary --only-binary :all:`.

---

## 5. Configure API Keys & Environment Variables

The app reads secrets from a `.env` file in the project root. Create that file now:

```
# .env  (place this file in the project root, next to requirements.txt)

# OpenWeatherMap — used for the weather forecast feature
OPENWEATHER_API_KEY=your_openweathermap_key_here

# Google Gemini — used for the AI chatbot
GEMINI_API_KEY=your_gemini_api_key_here

# Supabase — used for user accounts and saved schedules
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
```

### Where to get each key

**OpenWeatherMap API Key**
1. Go to [openweathermap.org](https://openweathermap.org) and create a free account.
2. Navigate to **API keys** in your profile.
3. Copy the default key (or generate a new one).
4. Free tier includes 1,000 calls/day — more than enough.

**Google Gemini API Key**
1. Go to [aistudio.google.com](https://aistudio.google.com).
2. Sign in with a Google account.
3. Click **Get API key** → **Create API key**.
4. Copy the key. Free tier is available.

**Supabase URL & Key**
1. Go to [supabase.com](https://supabase.com) and create a free account.
2. Create a new project (choose any name and region).
3. Once the project is ready, go to **Project Settings → API**.
4. Copy the **Project URL** → paste as `SUPABASE_URL`.
5. Copy the **anon / public** key → paste as `SUPABASE_KEY`.

> The app will still start without these keys, but affected features (weather, chatbot, user accounts) will be disabled or show error messages.

---

## 6. Set Up the Database (Supabase)

The app stores user accounts and saved itineraries in Supabase. You need to create the tables once before first use.

1. Log in to your [Supabase Dashboard](https://supabase.com/dashboard).
2. Select your project.
3. In the left sidebar, click **SQL Editor**.
4. Click **New query**.
5. Open the file `database/supabase_schema.sql` from this project.
6. Copy its entire contents and paste into the SQL Editor.
7. Click **Run** (or press `Ctrl + Enter`).

This creates three tables: `users`, `schedules`, and `feedback`.

To verify, go to **Table Editor** in the left sidebar — you should see all three tables listed.

---

## 7. Run the App

**Option A — Direct command (recommended):**
```bash
streamlit run app/main.py
```

**Option B — PowerShell script (Windows):**
```powershell
.\start.ps1
```

Streamlit will print something like:

```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

Open that URL in your browser. The app loads on port `8501` by default.

To stop the app, press `Ctrl + C` in the terminal.

---

## 8. Using the App

### Navigation

The top navigation bar has these pages:

| Page | Description |
|------|-------------|
| 🏠 Trang chủ | Home / landing page |
| ℹ️ Giới thiệu | About the project and team |
| ✅ Chức năng | All core features |
| 👤 Hồ sơ / Sign in | User account and saved itineraries |

---

### Chức năng (Core Features)

#### 🗓️ Tạo lịch trình gợi ý — Itinerary Planner

Automatically builds an optimized day-trip itinerary based on your preferences.

**How to use:**
1. Enter your **starting location** (e.g. "Quận 1, TP.HCM").
2. Tick the **interest categories** that apply to you (history, food, shopping, nature, etc.).
3. Set your **start and end times** and **maximum budget** (in VND).
4. Click **Tạo lịch trình tối ưu**.

The algorithm (Greedy + Lookahead) selects the best-scoring points of interest from a dataset of 7,700+ HCM locations, respects opening hours, travel time, entry fees, and your budget, and avoids scheduling two food stops too close together.

**Output:**
- A numbered itinerary with arrival/departure times and travel mode (walking, motorbike, taxi).
- An interactive map showing all stops connected by a route line.
- Google Maps links for each stop.
- A shareable link and a downloadable `.txt` file.
- A **Save** button (requires login) to store the itinerary in your profile.

---

#### 🚗 Tìm đường đi — Route Finder

Get turn-by-turn directions between two locations in HCM City.

**How to use:**
1. Enter a **start address** and a **destination address** in Vietnamese or English.
2. Choose your vehicle type: **Car** or **Motorbike**.
3. Click the search button.

The app geocodes both addresses (using Nominatim → Photon → Open-Meteo as fallbacks), then queries the OSRM routing engine for the optimal road route. If OSRM is unavailable, it falls back to a straight-line distance estimate.

**Output:**
- Total distance (km) and estimated travel time.
- Step-by-step turn instructions in Vietnamese.
- An interactive map with the route drawn on it.

---

#### 📷 Tìm vị trí ảnh — Landmark Image Recognition

Upload a photo and the app identifies which HCM City landmark it shows.

**How to use:**
1. Click **Browse files** and upload a `.jpg` or `.png` image.
2. The model runs automatically.

The app uses a fine-tuned ResNet-18 model (`model_vietnam.pth`) trained on 88 HCM City landmarks. It runs on CPU if no GPU is available, so results may take a few seconds.

**Output:**
- Predicted landmark name and confidence score.
- A Google Maps link to the identified location.

> **Note:** The model was trained on specific landmark categories. Photos of generic streets or non-landmark locations may produce low-confidence or incorrect results.

---

#### 🌤️ Báo thời tiết vị trí — Weather Forecast

Get current weather and a 3-day forecast for any location.

**How to use:**
1. Enter a location name (e.g. "Quận 7, TP.HCM" or "Đà Lạt").
2. Click the search button.

The app geocodes the location and fetches data from the Open-Meteo API (no API key required for this feature).

**Output:**
- Current temperature, feels-like temperature, humidity, wind speed, and weather description.
- 3-day forecast with daily high/low temperatures and UV index.

---

#### 📍 Gợi ý địa điểm — Place Recommender

Find places to visit based on your interests.

**How to use:**
1. Select one or more **interest tags** (food, history, park, shopping, etc.).
2. Optionally set a **minimum rating**.
3. Click the search button.

The recommender filters the POI dataset by your selected tags and returns the top results sorted by rating.

**Output:**
- A list of recommended places with name, rating, tags, opening hours, and entry fee.

---

#### 💬 Chatbot WindyAI

An AI assistant that answers travel questions about HCM City and guides you through the app's features.

**How to use:**
- Type your question in the chat input at the bottom of the page.
- The chatbot is powered by Google Gemini (`gemini-2.5-flash`) and is focused on HCM City travel topics and app usage guidance.

> Requires a valid `GEMINI_API_KEY` in your `.env` file.

---

### User Accounts

Click **Sign in / Sign up** in the navigation bar to create an account or log in.

- **Sign up:** Enter an email and password. You are logged in automatically after registration.
- **Sign in:** Enter your credentials. A session cookie keeps you logged in across browser refreshes.
- **Hồ sơ (Profile):** View and manage your saved itineraries. Requires login.

Passwords are stored as bcrypt hashes — never in plain text.

---

## 9. Project Structure

```
windyai/
├── app/
│   ├── main.py              # App entry point, navigation, session management
│   ├── config.py            # API keys and constants (reads from .env)
│   ├── style.css            # Global CSS styles
│   └── api/
│       └── chatbot_api.py   # Chatbot API endpoint
│
├── core/
│   ├── algo1/               # Itinerary optimizer (Greedy + Lookahead)
│   │   ├── solver_route.py  # Main planning algorithm
│   │   ├── scorer.py        # POI scoring logic
│   │   ├── optimizer.py     # Optimization helpers
│   │   ├── utils_geo.py     # Travel time & cost estimation
│   │   └── config.py        # Algorithm defaults
│   ├── algo2/               # Route finder (OSRM + Nominatim)
│   │   ├── routing.py       # Geocoding and OSRM integration
│   │   └── mapping.py       # Map rendering helpers
│   ├── algo3/               # Landmark image recognition (PyTorch ResNet-18)
│   │   ├── predict_vn.py    # Inference logic
│   │   ├── render_recognition.py  # Streamlit UI for this feature
│   │   ├── model_vietnam.pth      # Trained model weights
│   │   └── classes.txt      # 88 landmark class names
│   ├── algo4/
│   │   └── weather.py       # Open-Meteo weather integration
│   ├── algo5/
│   │   └── recommender.py   # Tag-based place recommender
│   └── algo6_chatbot/
│       ├── chatbot_engine.py      # Main chatbot orchestrator
│       ├── gemini_handler.py      # Google Gemini API wrapper
│       ├── intent_classifier.py   # User intent detection
│       ├── knowledge_base.py      # Static knowledge for the chatbot
│       └── response_generator.py  # Response formatting
│
├── pages/
│   ├── page_trang_chu.py    # Home page
│   ├── page_gioi_thieu.py   # About page
│   ├── page_chuc_nang.py    # Features page (all 6 features)
│   ├── page_ho_so.py        # User profile page
│   └── page_sign_in_up.py   # Sign in / Sign up page
│
├── services/
│   ├── db.py                # Supabase database operations
│   ├── utils.py             # Shared utility functions
│   └── feedback.py          # Feedback submission logic
│
├── data/
│   ├── pois_hcm_large.csv   # Main POI dataset (7,700+ locations)
│   └── train/               # Training images for algo3 (88 landmark classes)
│
├── database/
│   └── supabase_schema.sql  # SQL script to create all tables
│
├── assets/
│   ├── logo/                # App logo
│   ├── background/          # Background images and videos
│   └── images/members/      # Team member photos
│
├── docs/                    # Algorithm documentation
├── scripts/                 # Utility scripts (fetch POIs, train model, etc.)
├── .env                     # Your local secrets (not committed to git)
├── requirements.txt         # Python dependencies
├── runtime.txt              # Python version spec (python-3.12)
└── start.ps1                # Windows PowerShell startup script
```

---

## 10. Troubleshooting

**`ModuleNotFoundError: No module named 'services'` or `'pages'`**
You are running the app from inside the `app/` folder. Always run from the project root:
```bash
# Wrong
cd app
streamlit run main.py

# Correct
streamlit run app/main.py
```

**`ModuleNotFoundError: No module named 'core.algo3'` or PyTorch errors**
PyTorch may not have installed correctly. Try:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```
Then re-run `pip install -r requirements.txt`. The landmark recognition feature will still work on CPU.

**Supabase connection errors on startup**
- Double-check that `SUPABASE_URL` and `SUPABASE_KEY` in your `.env` are correct and have no extra spaces.
- Make sure you ran the SQL schema script in step 6.
- The app will still load without Supabase — only login/save features will be unavailable.

**Weather feature shows an error**
The weather feature uses Open-Meteo (no key needed) for the actual forecast, but geocoding the location name requires an internet connection. Check your connection and try a simpler location name.

**Chatbot replies "Xin lỗi, tôi chưa được cấu hình..."**
Your `GEMINI_API_KEY` is missing or invalid. Add it to `.env` and restart the app.

**Logo or background images not loading**
Make sure you are running from the project root and that the `assets/` folder is present. The app uses absolute paths resolved relative to `app/main.py`.

**Port 8501 already in use**
Run on a different port:
```bash
streamlit run app/main.py --server.port 8502
```

**`extra_streamlit_components` version conflict**
The app requires exactly `extra-streamlit-components==0.1.60`. If you see cookie-related errors, run:
```bash
pip install extra-streamlit-components==0.1.60 --force-reinstall
```

**App is slow on first load**
The first run loads the PyTorch model and the full POI dataset into memory. Subsequent interactions within the same session will be faster.
