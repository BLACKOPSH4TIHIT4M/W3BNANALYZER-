import gradio as gr
import time
import random
import pandas as pd
import os
import glob
import shutil # Import shutil untuk menghapus folder secara rekursif (e.g. __pycache__)
from typing import Generator, Any, List, Callable
from config import LLM_CONFIG, SUPPORTED_SEARCH_ENGINES, PRESET_COINS, FONT_PATH
from core.search_engine import get_search_engines
from core.selenium_crawler import SeleniumCrawler
from core.llm_service import LLMService
from core.data_handler import DataHandler
from core.output_formatter import format_summary_for_display, format_raw_data_for_display
from core.analysis import analyze_sentiment_simple, generate_word_cloud, create_sentiment_pie_chart

data_handler = DataHandler()

# --- PROTOKOL PENGHAPUSAN JEJAK (WIPE EVIDENCE) ---
def burn_evidence():
    """
    Menghapus semua file dan folder hasil operasi (metadata, data mentah, dan cache sistem).
    Ini adalah protokol penghapusan jejak digital komprehensif.
    """
    
    # 1. Target File Data dan Log Operasi
    data_patterns = ["*.csv", "*.log", "*.tmp", "*.txt"]
    files_to_wipe = []
    for pattern in data_patterns:
        files_to_wipe.extend(glob.glob(pattern))

    # 2. Target Folder Cache Sistem (Jejak Python)
    folders_to_wipe = ["__pycache__", "core/__pycache__"] # Menargetkan cache di root dan subfolder core

    deleted_count = 0
    
    # --- Eksekusi Penghapusan File ---
    for file_path in files_to_wipe:
        try:
            os.remove(file_path)
            deleted_count += 1
        except Exception as e:
            print(f"[ERROR WIPE] Gagal hapus file {file_path}: {e}")

    # --- Eksekusi Penghapusan Folder Rekursif (Cache) ---
    for folder_path in folders_to_wipe:
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path) # Hapus folder dan isinya
                deleted_count += 1 # Hitung 1 untuk penghapusan folder (meskipun isinya banyak)
            except Exception as e:
                print(f"[ERROR WIPE] Gagal hapus folder cache {folder_path}: {e}")

    # --- Laporan Status Akhir ---
    if deleted_count > 0:
        status_msg = f"🔥 BURN PROTOCOL V2.0 SUKSES: {deleted_count} jejak digital (Data, Log, dan Cache Sistem) dimusnahkan."
    else:
        status_msg = "ℹ️ Disk bersih. Tidak ada jejak yang ditemukan untuk dihapus."

    # 4. Reset Tampilan UI
    empty_df = format_raw_data_for_display([])
    
    # Return: Status, Summary, DataFrame, PieChart, WordCloud
    return status_msg, "", empty_df, None, None


def search_and_crawl_flow(api_key: str, base_url: str, model_name: str, search_engine_names: List[str],
                          time_period: str, query: str, search_count: float, crawl_count: float,
                          is_direct_crawl: bool = False) -> Generator[Any, None, None]:
    yield from unified_task_processor(
        api_key=api_key, base_url=base_url, model_name=model_name,
        search_engine_names=search_engine_names, time_period=time_period, query=query,
        search_count=search_count, crawl_count=crawl_count, is_direct_crawl=is_direct_crawl,
        url_list=None
    )


def targeted_crawl_flow(api_key: str, base_url: str, model_name: str, url_list_str: str) -> Generator[Any, None, None]:
    urls = [url.strip() for url in url_list_str.splitlines() if url.strip()]
    if not urls:
        yield "Error: Daftar URL kosong.", "Nihil", format_raw_data_for_display([]), None, None
        return
    yield from unified_task_processor(
        api_key=api_key, base_url=base_url, model_name=model_name,
        crawl_count=len(urls), url_list=urls, query="Targeted Crawl"
    )


def unified_task_processor(**kwargs) -> Generator[Any, None, None]:
    status, summary = "Sedang memulai tugas...", "Menunggu hasil analisis..."
    dataframe = format_raw_data_for_display([])
    pie_chart, word_cloud = None, None
    
    def yield_state(df_override: pd.DataFrame = None):
        display_df = df_override if df_override is not None else dataframe
        return status, summary, display_df, pie_chart, word_cloud

    crawler = SeleniumCrawler()
    if not crawler.driver:
        status = "Error: Selenium WebDriver gagal dimulai. Cek config.py."
        yield yield_state()
        return

    yield yield_state()

    url_list = kwargs.get('url_list')
    if url_list:
        search_results = [type('obj', (object,), {'link': url, 'title': f'URL Target {i + 1}', 'source': 'User Defined'}) for
                          i, url in enumerate(url_list)]
    else:
        search_engine_names = kwargs.get('search_engine_names', [])
        if not search_engine_names:
            status = "Error: Harap pilih setidaknya satu mesin pencari."
            yield yield_state()
            crawler.close()
            return

        search_count = int(kwargs.get('search_count', 10))
        crawl_count = int(kwargs.get('crawl_count', 5))
        
        status = f"Mencari via {', '.join(search_engine_names)}..."
        yield yield_state()
        
        search_engines = get_search_engines(search_engine_names)
        all_search_results = []
        for engine in search_engines:
            all_search_results.extend(
                engine.search(kwargs.get('query'), time_period=kwargs.get('time_period'), max_results=search_count))

        unique_links = set()
        search_results = [res for res in all_search_results if
                          res.link not in unique_links and not unique_links.add(res.link)]
        if not search_results:
            status = "Tidak ditemukan hasil yang relevan."
            yield yield_state()
            crawler.close()
            return

    dataframe = format_raw_data_for_display(search_results)
    status = "Pencarian selesai, mulai crawling..."
    yield yield_state()

    full_content, sentiments = "", []
    links_to_crawl = search_results[:int(kwargs.get('crawl_count', 5))]

    for i, result in enumerate(links_to_crawl):
        df_index = dataframe[dataframe['Link'] == result.link].index
        if df_index.empty: continue
        
        delay_seconds = random.uniform(2.0, 4.0)
        status = f"Crawling {i + 1}/{len(links_to_crawl)}... (Jeda {delay_seconds:.1f}s)"
        yield yield_state()
        time.sleep(delay_seconds)

        success, content_or_error = crawler.extract_content(result.link)
        
        dataframe.loc[df_index, 'Status'] = "Sukses" if success else "Gagal"
        if success:
            dataframe.loc[df_index, 'Konten'] = content_or_error
            full_content += content_or_error + "\n"
            sentiment = analyze_sentiment_simple(content_or_error)
            sentiments.append(sentiment)
            dataframe.loc[df_index, 'Sentimen'] = sentiment

        display_dataframe = dataframe.copy()
        display_dataframe['Konten'] = display_dataframe['Konten'].str.slice(0, 150) + '...'
        yield yield_state(df_override=display_dataframe)

    if full_content:
        status = "Membuat visualisasi..."
        yield yield_state()
        pie_chart = create_sentiment_pie_chart(sentiments)
        word_cloud = generate_word_cloud(full_content, FONT_PATH)
        yield yield_state()

    # Data persistensi (Data bocor ada di sini)
    data_handler.save_to_csv(dataframe.to_dict('records'), kwargs.get('query', 'task'))
    status = "Finalisasi data..."
    yield yield_state()

    # Logika LLM Summary
    if not kwargs.get('url_list') and not kwargs.get('is_direct_crawl') and full_content:
        user_key = kwargs.get('api_key', '')
        if user_key and "YOUR_API_KEY" not in user_key and len(user_key) > 10:
            status = "Meminta ringkasan AI..."
            yield yield_state()
            llm_service = LLMService(user_key, kwargs.get('base_url'), kwargs.get('model_name'))
            summary = format_summary_for_display(llm_service.summarize_news(full_content, kwargs.get('query')),
                                                 [res.link for res in links_to_crawl])
        else:
            summary = "Analisis LLM dilewati (API Key tidak diset)."
    else:
        summary = "Analisis LLM dilewati."

    status = "Tugas Selesai!"
    yield yield_state()
    crawler.close()


def create_ui():
    ALL_ENGINES = ["Bing", "Google", "Baidu", "DuckDuckGo"]
    
    with gr.Blocks(title="Web3 News Analyzer") as iface:
        gr.Markdown("# Web3 News Analyzer (Selenium Edition)")
        
        # --- KONFIGURASI ---
        with gr.Accordion("Konfigurasi API & Model", open=False):
            with gr.Row():
                api_key_input = gr.Textbox(label="API Key LLM", value=LLM_CONFIG["api_key"], type="password", scale=2)
                base_url_input = gr.Textbox(label="Base URL", value=LLM_CONFIG["base_url"] or "", scale=2)
                model_name_input = gr.Textbox(label="Model", value=LLM_CONFIG["model_name"], scale=1)

        # --- PANEL UTAMA ---
        with gr.Row(equal_height=False):
            # KIRI: INPUT
            with gr.Column(scale=4):
                with gr.Tabs():
                    with gr.TabItem("Mode 1: Search"):
                        with gr.Group():
                            gr.Markdown("### Parameter")
                            search_engine_input = gr.CheckboxGroup(label="Mesin Pencari", choices=ALL_ENGINES, value=[ALL_ENGINES[0]])
                            time_period_input = gr.Radio(label="Waktu", choices=["Semua Waktu", "24 Jam Terakhir", "1 Minggu Terakhir"], value="Semua Waktu")
                            search_count_input = gr.Number(label="Target Cari", value=10)
                            crawl_count_input = gr.Number(label="Target Baca", value=5)
                        with gr.Group():
                            gr.Markdown("### Eksekusi")
                            query_input = gr.Textbox(label="Kata Kunci", placeholder="Contoh: Binance Security")
                            analyze_button = gr.Button("🚀 Mulai Analisis", variant="primary")
                            
                            gr.Markdown("#### Preset:")
                            preset_buttons = [gr.Button(coin, size="sm") for coin in PRESET_COINS]

                    with gr.TabItem("Mode 2: URL"):
                        with gr.Group():
                            url_list_input = gr.Textbox(label="Daftar URL", lines=8, placeholder="https://...")
                            targeted_crawl_button = gr.Button("🚀 Mulai Crawling URL", variant="primary")
                
                # TOMBOL PENGHAPUSAN (BURN BUTTON)
                gr.Markdown("---")
                burn_button = gr.Button("🔥 Hapus Jejak / Wipe Evidence (WIPE DISK)", variant="stop")

            # KANAN: OUTPUT
            with gr.Column(scale=6):
                with gr.Group():
                    status_output = gr.Label(label="Status Operasi", value="Siap.")
                    summary_output = gr.Markdown(label="Laporan Intelijen (AI)")
                
                raw_data_output = gr.DataFrame(label="Tabel Data", interactive=False, wrap=True)
                
                with gr.Row():
                    sentiment_pie_chart = gr.Plot(label="Grafik Sentimen")
                    word_cloud_output = gr.Image(label="Peta Kata (WordCloud)")

        # --- WIRING ---
        standard_outputs = [status_output, summary_output, raw_data_output, sentiment_pie_chart, word_cloud_output]
        
        search_inputs = [api_key_input, base_url_input, model_name_input, search_engine_input, time_period_input,
                         query_input, search_count_input, crawl_count_input]
        analyze_button.click(fn=search_and_crawl_flow, inputs=search_inputs, outputs=standard_outputs)

        def create_preset_handler(coin):
            def handler(api_key, base_url, model_name, search_engines, time_period, search_count, crawl_count):
                yield from search_and_crawl_flow(
                    api_key, base_url, model_name, search_engines, time_period,
                    f"{coin} Crypto News", search_count, crawl_count, True
                )
            return handler

        preset_inputs = [api_key_input, base_url_input, model_name_input, search_engine_input, time_period_input,
                         search_count_input, crawl_count_input]
        for i, coin_button in enumerate(preset_buttons):
            coin_button.click(fn=create_preset_handler(PRESET_COINS[i]), inputs=preset_inputs, outputs=standard_outputs)

        targeted_inputs = [api_key_input, base_url_input, model_name_input, url_list_input]
        targeted_crawl_button.click(fn=targeted_crawl_flow, inputs=targeted_inputs, outputs=standard_outputs)
        
        burn_button.click(fn=burn_evidence, inputs=None, outputs=standard_outputs)

    return iface

