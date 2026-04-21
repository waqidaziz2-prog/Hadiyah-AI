"""
download_data.py
================
Run this script ONCE on Render (or any cloud server) to download all large
dataset files from Google Drive before starting the app.

Usage:
    python download_data.py

Set these environment variables on Render with your actual Google Drive file IDs:
    GDRIVE_MAIN_DF
    GDRIVE_HADITHS
    GDRIVE_EMBEDDINGS
    GDRIVE_TAFSEER
    GDRIVE_SURAH_INFO
    GDRIVE_ASMA
"""

import os
import requests

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def download_from_gdrive(file_id, dest_path):
    if os.path.exists(dest_path):
        print(f"  Already exists, skipping: {dest_path}")
        return True
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    print(f"  Downloading {os.path.basename(dest_path)} ...")
    session = requests.Session()
    response = session.get(url, stream=True)
    # Handle Google Drive large file confirmation
    token = None
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            token = value
            break
    if token:
        response = session.get(url, params={'confirm': token}, stream=True)
    with open(dest_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=32768):
            if chunk:
                f.write(chunk)
    print(f"  Saved: {dest_path}")
    return True

FILES = {
    'GDRIVE_MAIN_DF':      os.path.join(DATA_DIR, 'main_df.csv'),
    'GDRIVE_HADITHS':      os.path.join(DATA_DIR, 'kaggle_hadiths_clean.csv'),
    'GDRIVE_EMBEDDINGS':   os.path.join(DATA_DIR, 'quran_embeddings.npy'),
    'GDRIVE_TAFSEER':      os.path.join(DATA_DIR, 'Tafsir_al-Jalalayn_tafseer.csv'),
    'GDRIVE_SURAH_INFO':   os.path.join(DATA_DIR, 'surah_info.csv'),
    'GDRIVE_ASMA':         os.path.join(DATA_DIR, 'Asma_ul_Husna.csv'),
}

if __name__ == '__main__':
    print("Downloading dataset files from Google Drive...")
    for env_var, dest in FILES.items():
        file_id = os.environ.get(env_var)
        if not file_id:
            print(f"  WARNING: {env_var} environment variable not set, skipping.")
            continue
        download_from_gdrive(file_id, dest)
    print("Done!")
