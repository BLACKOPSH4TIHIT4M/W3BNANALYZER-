import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def test_driver():
    print("=== MULAI DIAGNOSTIK DRIVER ===")
    
    # Path yang akan dites (Sesuai Config baru)
    path = "/usr/bin/chromedriver"
    
    if not os.path.exists(path):
        print(f"[X] FILE HILANG: {path} tidak ditemukan.")
        print("    SOLUSI: Jalankan 'sudo apt install chromium-driver'")
        return

    print(f"[OK] File ditemukan di: {path}")
    if not os.access(path, os.X_OK):
        print("[X] IZIN DITOLAK: File tidak bisa dieksekusi.")
        print(f"    SOLUSI: chmod +x {path}")
        return

    print("--- Mencoba Menjalankan Browser ---")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox") # Wajib untuk Kali Root
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        service = Service(executable_path=path)
        driver = webdriver.Chrome(service=service, options=options)
        print("[SUKSES] WebDriver berhasil start!")
        print(f"Versi Browser: {driver.capabilities['browserVersion']}")
        driver.quit()
    except Exception as e:
        print("\n[GAGAL] Error Detail:")
        print(e)

if __name__ == "__main__":
    test_driver()
