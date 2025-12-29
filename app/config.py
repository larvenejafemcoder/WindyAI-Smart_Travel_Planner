#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File cấu hình - chứa các hằng số và API keys
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Endpoints
NOMINATIM = "https://nominatim.openstreetmap.org"
OSRM = "https://router.project-osrm.org"
OPENWEATHER = "https://api.openweathermap.org/data/2.5/weather"

# API Keys
# Ưu tiên lấy từ biến môi trường, nếu không có thì dùng giá trị mặc định
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")

# Headers
USER_AGENT = {"User-Agent": "OSM-Demo-Combined/1.0 (contact: your_email@example.com)"}

# Timeouts
GEOCODE_DELAY = 1.0  # Giây
API_TIMEOUT = 120    # Giây
