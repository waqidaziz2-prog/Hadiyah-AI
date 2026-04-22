document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const voiceBtn = document.getElementById('voice-btn');
    const urduModeToggle = document.getElementById('urdu-mode');
    const resultsContainer = document.getElementById('results-container');
    const loadingElement = document.getElementById('loading');

    // --- Voice Recognition Setup ---
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    let isRecording = false;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = () => {
            isRecording = true;
            voiceBtn.classList.add('recording');
            searchInput.placeholder = "Listening...";
        };

        recognition.onend = () => {
            isRecording = false;
            voiceBtn.classList.remove('recording');
            searchInput.placeholder = "Ask a question (e.g., 'What is Zakat?', 'Patience')...";
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            searchInput.value = transcript;
            performSearch();
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            alert('Voice search error: ' + event.error);
        };
    } else {
        voiceBtn.style.display = 'none';
        console.warn('Speech Recognition not supported in this browser.');
    }

    voiceBtn.addEventListener('click', () => {
        if (!recognition) return;
        if (isRecording) {
            recognition.stop();
        } else {
            // Set language based on mode
            recognition.lang = urduModeToggle.checked ? 'ur-PK' : 'en-US';
            recognition.start();
        }
    });

    // --- Speech Synthesis (Text-to-Speech) ---
    function speakText(text, lang = 'en-US') {
        window.speechSynthesis.cancel(); // Stop any current speech
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang;
        window.speechSynthesis.speak(utterance);
    }

    // --- Search Logic ---
    async function performSearch() {
        const query = searchInput.value.trim();
        if (!query) return;
        resultsContainer.innerHTML = '';
        loadingElement.classList.remove('hidden');
        
        const useUrdu = urduModeToggle.checked;

        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    query: query, 
                    top_k: 5,
                    use_urdu: useUrdu
                }),
            });
            if (!response.ok) throw new Error('Search failed');
            const data = await response.json();
            renderResults(data.results, data.asma_result, useUrdu);
        } catch (error) {
            console.error('Error:', error);
            resultsContainer.innerHTML = `<div class="error">An error occurred while seeking knowledge. Please try again.</div>`;
        } finally {
            loadingElement.classList.add('hidden');
        }
    }

    function renderResults(results, asmaResult, useUrdu) {
        if (asmaResult) {
            const asmaCard = document.createElement('div');
            asmaCard.className = 'result-card-premium asma-card';
            
            const meaning = useUrdu ? asmaResult.urdu_meaning : asmaResult.meaning;
            const summary = useUrdu ? asmaResult.urdu_summary : asmaResult.summary;

            asmaCard.innerHTML = `
                <div class="verse-header">
                    <span class="chapter-badge"><i class="fa-solid fa-star-and-crescent"></i> Asma ul Husna — ${asmaResult.english_name}</span>
                </div>
                <button class="play-btn" data-text="${meaning}. ${summary}" data-lang="${useUrdu ? 'ur-PK' : 'en-US'}">
                    <i class="fa-solid fa-volume-high"></i> Listen
                </button>
                <div class="quran-text">${asmaResult.arabic_name}</div>
                <div class="trans-text ${useUrdu ? 'hidden' : ''}"><strong>${asmaResult.meaning}</strong></div>
                <div class="urdu-text ${useUrdu ? '' : 'hidden'}">${asmaResult.urdu_meaning}</div>
                
                <div class="insight-box">
                    <div class="insight-title"><i class="fa-solid fa-circle-info"></i> Summary</div>
                    <div class="insight-content">${summary}</div>
                </div>
            `;
            resultsContainer.appendChild(asmaCard);
        }

        if (!results || results.length === 0) {
            if (!asmaResult) {
                resultsContainer.innerHTML = `
                    <div class="result-card-premium" style="text-align: center;">
                        <h3>No results found.</h3>
                        <p style="color: var(--text-secondary);">Try asking differently or use different keywords.</p>
                    </div>`;
            }
        } else {
            results.forEach((item, index) => {
                const card = document.createElement('div');
                card.className = 'result-card-premium';
                card.style.animationDelay = `${index * 0.1}s`;

                const mainText = useUrdu ? item.urdu_text : item.english_text;

                card.innerHTML = `
                    <div class="verse-header">
                        <span class="chapter-badge"><i class="fa-solid fa-book-quran"></i> ${item.surah_name_en} — Verse ${item.ayah_no}</span>
                        <span class="match-score">Match: ${(item.score * 100).toFixed(0)}%</span>
                    </div>
                    <button class="play-btn" data-text="${mainText}" data-lang="${useUrdu ? 'ur-PK' : 'en-US'}">
                        <i class="fa-solid fa-volume-high"></i> Listen
                    </button>
                    <div class="quran-text">${item.arabic_text}</div>
                    <div class="trans-text ${useUrdu ? 'hidden' : ''}">${item.english_text}</div>
                    <div class="urdu-text ${useUrdu ? '' : 'hidden'}">${item.urdu_text}</div>
                    
                    ${item.hadiths && item.hadiths.length > 0 ? `
                        <div class="insight-box">
                            <div class="insight-title"><i class="fa-solid fa-scroll"></i> Related Hadith</div>
                            <ul class="hadith-list">
                                ${item.hadiths.map(h => `<li>${h}</li>`).join('')}
                            </ul>
                        </div>` : ''}
                `;
                resultsContainer.appendChild(card);
            });
        }

        // Add listeners to play buttons
        document.querySelectorAll('.play-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                speakText(btn.dataset.text, btn.dataset.lang);
            });
        });
    }

    searchBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });
});
