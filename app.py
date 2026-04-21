import os
import requests
import pandas as pd
import numpy as np
import re
from flask import Flask, render_template, request, jsonify
from deep_translator import GoogleTranslator
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

QURAN_CSV       = os.path.join(DATA_DIR, 'main_df.csv')
HADITH_CSV      = os.path.join(DATA_DIR, 'kaggle_hadiths_clean.csv')
ASMA_CSV        = os.path.join(DATA_DIR, 'Asma_ul_Husna.csv')
EMBEDDINGS_PATH = os.path.join(DATA_DIR, 'quran_embeddings.npy')

model             = None
loaded_embeddings = None
quran_df          = None
hadith_df         = None
asma_df           = None


# ──────────────────────────────────────────────────────────────
# Auto-download data files from Google Drive (for cloud/Render)
# ──────────────────────────────────────────────────────────────
def download_from_gdrive(file_id: str, dest_path: str):
    if os.path.exists(dest_path):
        return
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    print(f"Downloading {os.path.basename(dest_path)} from Google Drive...")
    url = "https://drive.google.com/uc?export=download"
    session = requests.Session()
    resp = session.get(url, params={"id": file_id}, stream=True)
    # Handle large-file warning cookie
    token = next((v for k, v in resp.cookies.items() if k.startswith("download_warning")), None)
    if token:
        resp = session.get(url, params={"id": file_id, "confirm": token}, stream=True)
    with open(dest_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=32768):
            if chunk:
                f.write(chunk)
    print(f"  Saved: {dest_path}")


def ensure_data_files():
    """Download data files from Google Drive if running on cloud and files are missing."""
    gdrive_ids = {
        'GDRIVE_MAIN_DF':    QURAN_CSV,
        'GDRIVE_HADITHS':    HADITH_CSV,
        'GDRIVE_EMBEDDINGS': EMBEDDINGS_PATH,
        'GDRIVE_ASMA':       ASMA_CSV,
    }
    for env_var, dest in gdrive_ids.items():
        file_id = os.environ.get(env_var)
        if file_id and not os.path.exists(dest):
            download_from_gdrive(file_id, dest)


# ──────────────────────────────────────────────────────────────
# Data loading
# ──────────────────────────────────────────────────────────────
def load_data():
    global model, loaded_embeddings, quran_df, hadith_df, asma_df
    print("Loading models and data...")

    ensure_data_files()

    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model loaded.")
    except Exception as e:
        print(f"Error loading model: {e}")
        model = None

    try:
        if os.path.exists(EMBEDDINGS_PATH):
            loaded_embeddings = np.load(EMBEDDINGS_PATH)
            print(f"Embeddings loaded: shape {loaded_embeddings.shape}")
        else:
            print(f"Embeddings file not found at {EMBEDDINGS_PATH}")
            return False
    except Exception as e:
        print(f"Error loading embeddings: {e}")
        return False

    try:
        if not os.path.exists(QURAN_CSV):
            print(f"Missing: {QURAN_CSV}")
            return False
        quran_df = pd.read_csv(QURAN_CSV, encoding='utf-8').reset_index(drop=True)
        print(f"Quran data loaded: {len(quran_df)} rows")
    except Exception as e:
        print(f"Error loading Quran CSV: {e}")
        return False

    try:
        if os.path.exists(HADITH_CSV):
            h_df = pd.read_csv(HADITH_CSV, encoding='utf-8')
            hadith_df = h_df[['text_en']].dropna().rename(columns={'text_en': 'text'}).reset_index(drop=True)
            print(f"Hadith loaded: {len(hadith_df)} rows")
    except Exception as e:
        print(f"Error loading Hadith: {e}")

    try:
        if os.path.exists(ASMA_CSV):
            asma_df = pd.read_csv(ASMA_CSV, encoding='utf-8')
            print(f"Asma ul Husna loaded: {len(asma_df)} rows")
    except Exception as e:
        print(f"Error loading Asma ul Husna: {e}")

    print("Data loaded successfully.")
    return True


# ──────────────────────────────────────────────────────────────
# Search helpers
# ──────────────────────────────────────────────────────────────
def normalize_text(text):
    text = str(text).strip()
    text = re.sub(r'\s+', ' ', text)
    return text.lower()


def search_asma(query):
    if asma_df is None:
        return None
    norm = normalize_text(query)
    keywords = ['name', 'allah', 'asma', 'husna', 'attribute', 'names of god', 'al-']
    if not any(k in norm for k in keywords):
        return None
    for col in ['Name in English', 'Name Meaning', 'Short Summary']:
        if col in asma_df.columns:
            mask = asma_df[col].str.lower().str.contains(norm, na=False)
            hits = asma_df[mask]
            if not hits.empty:
                row = hits.iloc[0]
                return {
                    'arabic_name':  row.get('Arabic Name', ''),
                    'english_name': row.get('Name in English', ''),
                    'meaning':      row.get('Name Meaning', ''),
                    'summary':      row.get('Short Summary', ''),
                    'details':      row.get('Long Summary', ''),
                }
    return None


def semantic_search_logic(query, top_k=5):
    # Translate Roman Urdu / any language to English
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(query)
        print(f"Query: '{query}' → '{translated}'")
        query = translated
    except Exception as e:
        print(f"Translation error: {e}")

    asma_result = search_asma(query)

    synonyms = {
        'roza': 'fasting', 'sawm': 'fasting', 'siyam': 'fasting',
        'namaz': 'prayer', 'salah': 'prayer', 'salat': 'prayer', 'solat': 'prayer',
        'zakat': 'charity', 'sadaqah': 'charity',
        'hajj': 'pilgrimage', 'umrah': 'pilgrimage',
        'quran': 'recitation', 'tawbah': 'repentance',
        'jannah': 'paradise', 'jahannam': 'hellfire',
        'jihad': 'striving', 'sabr': 'patience',
        'tawakkul': 'trust in god', 'ikhlas': 'sincerity',
        'yateem': 'orphan', 'masakeen': 'poor needy',
    }

    norm_query = normalize_text(query)
    search_terms = [norm_query]
    for word, syn in synonyms.items():
        if word in norm_query:
            search_terms.append(syn)

    # Keyword search
    keyword_indices = []
    if quran_df is not None and 'Translation - Muhammad Tahir-ul-Qadri' in quran_df.columns:
        for term in search_terms:
            mask = quran_df['Translation - Muhammad Tahir-ul-Qadri'].str.lower().str.contains(
                re.escape(term), na=False)
            keyword_indices.extend(quran_df[mask].index.tolist())
    keyword_indices = list(set(keyword_indices))

    # Semantic search
    scores = np.zeros(len(quran_df)) if quran_df is not None else np.array([])
    semantic_indices = []
    if model is not None and loaded_embeddings is not None and len(loaded_embeddings) > 0:
        try:
            q_vec = model.encode([norm_query], convert_to_numpy=True)
            scores = cosine_similarity(q_vec, loaded_embeddings)[0]
            top_idx = np.argsort(scores)[-top_k:][::-1]
            semantic_indices = [int(i) for i in top_idx if scores[i] > 0.20]
        except Exception as e:
            print(f"Search error: {e}")

    # Merge results
    seen, final_indices = set(), []
    for idx in keyword_indices:
        if idx not in seen:
            final_indices.append(idx)
            seen.add(idx)
    for idx in semantic_indices:
        if idx not in seen:
            final_indices.append(idx)
            seen.add(idx)
    final_indices = final_indices[:top_k]

    results = []
    for idx in final_indices:
        if quran_df is None or idx >= len(quran_df):
            continue
        row = quran_df.iloc[idx]
        score = 1.0 if idx in keyword_indices else float(scores[idx]) if idx < len(scores) else 0.0

        translations = {}
        for col in ['Translation - Muhammad Tahir-ul-Qadri', 'Translation - Arthur J', 'Translation - Marmaduke Pickthall']:
            if col in quran_df.columns:
                val = row.get(col, '')
                if pd.notna(val) and str(val).strip():
                    translations[col.replace('Translation - ', '')] = str(val)

        tafseers = {}
        for col in ['Tafaseer - Tafsir al-Jalalayn', 'Tafaseer - Tanwir al-Miqbas min Tafsir Ibn Abbas']:
            if col in quran_df.columns:
                val = row.get(col, '')
                if pd.notna(val) and str(val).strip():
                    tafseers[col.replace('Tafaseer - ', '')] = str(val)

        h_texts = []
        if hadith_df is not None and not hadith_df.empty:
            keyword = norm_query.split()[0] if norm_query else ''
            if keyword:
                mask = hadith_df['text'].str.lower().str.contains(re.escape(keyword), na=False)
                rel = hadith_df[mask]
                h_texts = rel.head(2)['text'].tolist() if len(rel) > 0 else hadith_df.sample(2)['text'].tolist()
            else:
                h_texts = hadith_df.sample(2)['text'].tolist()

        results.append({
            'surah_no':        int(row.get('Surah', 0)),
            'ayah_no':         int(row.get('Ayat', 0)),
            'surah_name_en':   str(row.get('Name', '')),
            'surah_name_ar':   str(row.get('ArabicTitle', '')),
            'surah_name_roman':str(row.get('RomanTitle', '')),
            'arabic_text':     str(row.get('Arabic', '')),
            'english_text':    str(translations.get('Muhammad Tahir-ul-Qadri', '')),
            'translations':    translations,
            'tafseers':        tafseers,
            'hadiths':         h_texts,
            'score':           score,
        })

    return results, asma_result


# ──────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/api/search', methods=['POST'])
def search():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'No query provided'}), 400
    results, asma_result = semantic_search_logic(data['query'], data.get('top_k', 5))
    return jsonify({'results': results, 'asma_result': asma_result})

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'quran_rows': len(quran_df) if quran_df is not None else 0})


if __name__ == '__main__':
    if load_data():
        app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    else:
        print("Failed to initialize application data. Please check data files.")
