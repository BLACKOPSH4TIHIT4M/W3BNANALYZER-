# config.py
# Kelola kunci API, jalur file, dan konfigurasi model Anda di sini (INTELLIGENCE OPERATIONS)

from typing import List, Dict, Optional
import os
import sys

# ==========================================
# KONFIGURASI WEBDRIVER (Auto-Detect untuk Kali Linux)
# ==========================================
# Prioritas 1: Driver Sistem Kali Linux (/usr/bin/chromedriver)
SYSTEM_DRIVER = "/usr/bin/chromedriver" 

# Prioritas 2: Driver Manual/Lokal (Default user path)
LOCAL_DRIVER = "/home/h4tihit4m/BL4CKOPS_GIT/Web3-News-Analyzer/chromedriver" 

if os.path.exists(SYSTEM_DRIVER):
    WEBDRIVER_PATH = SYSTEM_DRIVER
elif os.path.exists(LOCAL_DRIVER):
    WEBDRIVER_PATH = LOCAL_DRIVER
else:
    # Fallback jika tidak ditemukan
    WEBDRIVER_PATH = "chromedriver"


# ==========================================
# KONFIGURASI LLM (LARGE LANGUAGE MODEL)
# ==========================================
# API Key digunakan untuk Ringkasan Cepat dan Analisis Deep State
LLM_CONFIG: Dict[str, Optional[str]] = {
    "api_key": ""
    "base_url": None,
    "model_name": "gpt-3.5-turbo"
}

# ==========================================
# PENGATURAN TAMPILAN & FONT
# ==========================================
# Menggunakan font Inggris secara default untuk kompatibilitas plot
FONT_PATH = "DejaVuSans.ttf"

# ==========================================
# TARGET DATA
# ==========================================
# Daftar mesin pencari yang didukung. Google dihapus untuk fokus pada Deep Scan/Filter Evasion.
SUPPORTED_SEARCH_ENGINES: List[str] = ["Bing", "Baidu", "DuckDuckGo", "Yandex"] 

# Daftar koin kripto preset
PRESET_COINS: List[str] = ["BTC", "ETH", "SOL", "BNB"]

# ==========================================
# KONFIGURASI ANTI-SCRAPING (STEALTH)
# ==========================================
# User-Agent untuk menyamarkan bot sebagai browser pengguna asli
USER_AGENTS: List[str] = [
    # User Agent Chrome Terbaru (Okt 2024) - Paling kuat untuk Headless
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36", 
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
]

# TOR SOCKS5 Proxy Configuration for Dark Web Layer (Default port di Kali)
TOR_SOCKS_PROXY = "socks5://127.0.0.1:9050"

# Daftar Proxy (Format: "ip:port" atau "user:pass@ip:port")
PROXIES: List[str] = []
