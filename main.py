# main.py
import sys
import logging
import warnings
import types

# ==========================================
# WARNING SILENCER (PRIORITAS TERTINGGI)
# ==========================================
# Kita pasang peredam suara di baris paling awal.
# Ini akan menangkap warning 'pkg_resources' bahkan saat kita mencoba meng-import-nya di bawah.
warnings.filterwarnings("ignore", category=UserWarning, module='jieba')
warnings.filterwarnings("ignore", message=".*pkg_resources is deprecated.*")
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ==========================================
# SYSTEM BYPASS & PATCHING
# ==========================================
# Masalah: Python 3.13+ membuang 'pkg_resources', tapi 'jieba' membutuhkannya.
# Solusi: Kita suntikkan modul palsu (Dummy) ke memori.

try:
    import pkg_resources
except ImportError:
    # Jika pkg_resources HILANG, kita buat versi palsunya
    fake_pkg = types.ModuleType("pkg_resources")
    # Jieba biasanya cuma cek versi, kita kasih return object kosong
    fake_pkg.get_distribution = lambda x: type('obj', (object,), {'version': '0.0.0'})()
    # Daftarkan ke sistem biar dianggap ada
    sys.modules["pkg_resources"] = fake_pkg

# ==========================================
# LOAD APLIKASI UTAMA
# ==========================================
from app_ui import create_ui

if __name__ == "__main__":
    # Konfigurasi logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - [%(module)s] - %(message)s'
    )

    print("[*] System Patch Applied: pkg_resources bypassed.")
    print("[*] Menginisialisasi Protokol Web3 News Analyzer...")
    print("[+] Interface siap. Akses di browser: http://127.0.0.1:7860")

    try:
        app = create_ui()
        app.launch()
    except KeyboardInterrupt:
        print("\n[!] Operasi dihentikan manual oleh user (SIGINT).")
        sys.exit(0)
    except TypeError as e:
        print(f"\n[X] Terjadi Error Kompatibilitas UI: {e}")
        print("    Saran: Error ini biasanya karena versi Gradio lama/baru. Fitur kosmetik sudah dimatikan.")
        sys.exit(1)
