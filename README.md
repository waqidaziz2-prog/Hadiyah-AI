# Hadiyah-AI: Quranic Chatbot

A powerful AI-driven chatbot designed to provide divine guided wisdom from the Quran and Hadith.

## Features
- **Semantic Search**: Find verses based on meaning, not just keywords.
- **Multi-language Support**: Search in English or Roman Urdu.
- **Hadith Integration**: Relevant Hadiths are provided alongside Quranic verses.
- **Asma ul Husna**: Search and learn about the Names of Allah.

## Quick Start (Windows)

1. **Setup**: Run `setup_venv.bat` to create a virtual environment and install dependencies.
2. **Run**: Run `python start.py`. This script will:
   - Download missing data files.
   - Generate embeddings (if needed).
   - Start the Flask server.

## Terminal Commands

If you prefer using the terminal manually:

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate it
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the master script
python start.py
```

## Permanent Storage & Version Control

This project is already initialized with Git and linked to GitHub:
- **Repository**: `https://github.com/waqidaziz2-prog/Hadiyah-AI`

To save your changes permanently:
```bash
git add .
git commit -m "Your update message"
git push origin main
```

## Data Files
Large data files are stored in the `data/` directory. If they are missing, `start.py` will attempt to download them from Google Drive using IDs set in environment variables.