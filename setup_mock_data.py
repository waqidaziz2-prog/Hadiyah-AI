import pandas as pd
import numpy as np
import os
from sentence_transformers import SentenceTransformer
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
quran_data = [
    [1, 1, 'Al-Fatiha', 'بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ', 'In the name of Allah, the Most Gracious, the Most Merciful.'],
    [1, 2, 'Al-Fatiha', 'ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَٰلَمِينَ', 'All praise is due to Allah, the Lord of the Worlds.'],
    [1, 3, 'Al-Fatiha', 'ٱلرَّحْمَٰنِ ٱلرَّحِيمِ', 'The Most Gracious, the Most Merciful.'],
    [1, 4, 'Al-Fatiha', 'مَٰلِكِ يَوْمِ ٱلدِّينِ', 'Master of the Day of Judgment.'],
    [1, 5, 'Al-Fatiha', 'إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ', 'You alone we worship, and You alone we ask for help.'],
    [2, 43, 'Al-Baqarah', 'وَأَقِيمُوا۟ ٱلصَّلَوٰةَ وَءَاتُوا۟ ٱلزَّكَوٰةَ', 'And establish prayer and give zakat and bow with those who bow [in worship and obedience].'],
    [2, 153, 'Al-Baqarah', 'يَٰٓأَيُّهَا ٱلَّذِينَ ءَامَنُوا۟ ٱسْتَعِينُوا۟ بِٱلصَّبْرِ وَٱلصَّلَوٰةِ', 'O you who have believed, seek help through patience and prayer. Indeed, Allah is with the patient.'],
    [2, 183, 'Al-Baqarah', 'يَٰٓأَيُّهَا ٱلَّذِينَ ءَامَنُوا۟ كُتِبَ عَلَيْكُمُ ٱلصِّيَامُ', 'O you who have believed, decreed upon you is fasting as it was decreed upon those before you that you may become righteous.'],
    [2, 196, 'Al-Baqarah', 'وَأَتِمُّوا۟ ٱلْحَجَّ وَٱلْعُمْرَةَ لِلَّهِ', 'And complete the Hajj and Umrah for Allah.'],
    [2, 261, 'Al-Baqarah', 'مَّثَلُ ٱلَّذِينَ يُنفِقُونَ أَمْوَٰلَهُمْ فِي سَبِيلِ ٱللَّهِ', 'The example of those who spend their wealth in the way of Allah is like a seed [of grain] which grows seven spikes; in each spike is a hundred grains.'],
    [3, 97, 'Al-Imran', 'وَلِلَّهِ عَلَى ٱلنَّاسِ حِجُّ ٱلْبَيْتِ', 'And [due] to Allah from the people is a pilgrimage to the House - for whoever is able to find thereto a way.'],
    [93, 7, 'Ad-Duhaa', 'وَوَجَدَكَ ضَالًّا فَهَدَىٰ', 'And He found you lost and guided [you].'],
    [94, 5, 'Ash-Sharh', 'فَإِنَّ مَعَ ٱلْعُسْرِ يُسْرًا', 'For indeed, with hardship [will be] ease.'],
    [112, 1, 'Al-Ikhlas', 'قُلْ هُوَ ٱللَّهُ أَحَدٌ', 'Say, "He is Allah, [who is] One."'],
    [103, 1, 'Al-Asr', 'وَٱلْعَصْرِ', 'By time,'],
    [103, 2, 'Al-Asr', 'إِنَّ ٱلإِنسَٰنَ لَفِى خُسْرٍ', 'Indeed, mankind is in loss,'],
    [109, 1, 'Al-Kafirun', 'قُلْ يَٰٓأَيُّهَا ٱلْكَٰفِرُونَ', 'Say, "O disbelievers,"'],
]
df_quran = pd.DataFrame(quran_data, columns=['Surah', 'Ayat', 'Name', 'Arabic', 'Translation - Muhammad Tahir-ul-Qadri'])
df_quran.to_csv(os.path.join(DATA_DIR, 'main_df.csv'), index=False)
print("Created main_df.csv")
surah_info_data = [
    [1, 'الفاتحة', 'The Opening'],
    [93, 'الضحى', 'The Morning Hours'],
    [94, 'الشرح', 'The Relief'],
    [112, 'الإخلاص', 'The Sincerity'],
]
df_surah = pd.DataFrame(surah_info_data, columns=['SurahNumber', 'ArabicTitle', 'EnglishTitle'])
df_surah.to_csv(os.path.join(DATA_DIR, 'surah_info.csv'), index=False)
print("Created surah_info.csv")
tafseer_data = [
    'Tafseer for verse ' + str(i+1) for i in range(len(df_quran))
]
df_tafseer = pd.DataFrame(tafseer_data, columns=['Tafseer'])
df_tafseer.to_csv(os.path.join(DATA_DIR, 'Tafsir_al-Jalalayn_tafseer.csv'), index=False)
print("Created Tafsir_al-Jalalayn_tafseer.csv")
hadith_data = [
    ['The best of you are those who learn the Quran and teach it.'],
    ['Actions are judged by intentions.'],
    ['None of you will have faith till he wishes for his (Muslim) brother what he likes for himself.'],
]
df_hadith = pd.DataFrame(hadith_data, columns=['text_en'])
df_hadith.to_csv(os.path.join(DATA_DIR, 'kaggle_hadiths_clean.csv'), index=False)
print("Created kaggle_hadiths_clean.csv")
print("Loading model to generate actual embeddings...")
model = SentenceTransformer('all-MiniLM-L6-v2')
texts = df_quran['Translation - Muhammad Tahir-ul-Qadri'].tolist()
embeddings = model.encode(texts, convert_to_numpy=True)
np.save(os.path.join(DATA_DIR, 'quran_embeddings.npy'), embeddings)
print("Created quran_embeddings.npy with shape:", embeddings.shape)
