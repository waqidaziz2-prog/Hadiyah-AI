import pandas as pd
import numpy as np
import os
from sentence_transformers import SentenceTransformer

DATA_DIR = 'data'
QURAN_CSV = os.path.join(DATA_DIR, 'main_df.csv')
EMBEDDINGS_PATH = os.path.join(DATA_DIR, 'quran_embeddings.npy')

def main():
    print("Loading Quran data...")
    if not os.path.exists(QURAN_CSV):
        print(f"Error: {QURAN_CSV} not found!")
        return

    df = pd.read_csv(QURAN_CSV)
    print(f"Loaded {len(df)} verses.")

    print("Loading model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    print("Extracting English translation text...")
    # Fill NaN with empty string just in case
    texts = df['Translation - Muhammad Tahir-ul-Qadri'].fillna("").tolist()

    print("Generating embeddings... This will take a few minutes.")
    # Show progress bar using tqdm if possible, but encode handles it internally mostly.
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)

    print("Saving embeddings...")
    np.save(EMBEDDINGS_PATH, embeddings)
    print(f"Successfully saved embeddings with shape: {embeddings.shape} to {EMBEDDINGS_PATH}")

if __name__ == '__main__':
    main()
