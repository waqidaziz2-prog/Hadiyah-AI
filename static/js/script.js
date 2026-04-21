document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const resultsContainer = document.getElementById('results-container');
    const loadingElement = document.getElementById('loading');

    async function performSearch() {
        const query = searchInput.value.trim();
        if (!query) return;
        resultsContainer.innerHTML = '';
        loadingElement.classList.remove('hidden');
        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query, top_k: 5 }),
            });
            if (!response.ok) throw new Error('Search failed');
            const data = await response.json();
            renderResults(data.results, data.asma_result);
        } catch (error) {
            console.error('Error:', error);
            resultsContainer.innerHTML = `<div class="error">An error occurred while seeking knowledge. Please try again.</div>`;
        } finally {
            loadingElement.classList.add('hidden');
        }
    }

    function renderResults(results, asmaResult) {
        if (asmaResult) {
            const asmaCard = document.createElement('div');
            asmaCard.className = 'result-card-premium asma-card';
            asmaCard.innerHTML = `
                <div class="verse-header">
                    <span class="chapter-badge"><i class="fa-solid fa-star-and-crescent"></i> Asma ul Husna — ${asmaResult.english_name}</span>
                </div>
                <div class="quran-text">${asmaResult.arabic_name}</div>
                <div class="trans-text"><strong>${asmaResult.meaning}</strong></div>
                <div class="insight-box">
                    <div class="insight-title"><i class="fa-solid fa-circle-info"></i> Summary</div>
                    <div class="insight-content">${asmaResult.summary}</div>
                </div>
                ${asmaResult.details ? `<div class="insight-box"><div class="insight-title"><i class="fa-solid fa-book-open"></i> Details</div><div class="insight-content">${asmaResult.details}</div></div>` : ''}
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
            return;
        }

        results.forEach((item, index) => {
            const card = document.createElement('div');
            card.className = 'result-card-premium';
            card.style.animationDelay = `${index * 0.1}s`;

            // Multiple translations
            let translationsHtml = '';
            if (item.translations && Object.keys(item.translations).length > 1) {
                const extraTranslations = Object.entries(item.translations)
                    .filter(([k]) => k !== 'Muhammad Tahir-ul-Qadri')
                    .map(([name, text]) => `<li><strong>${name}:</strong> ${text}</li>`)
                    .join('');
                if (extraTranslations) {
                    translationsHtml = `
                        <div class="insight-box">
                            <div class="insight-title"><i class="fa-solid fa-language"></i> More Translations</div>
                            <ul class="hadith-list">${extraTranslations}</ul>
                        </div>`;
                }
            }

            // Multiple tafseers
            let tafseersHtml = '';
            if (item.tafseers && Object.keys(item.tafseers).length > 0) {
                tafseersHtml = Object.entries(item.tafseers).map(([name, text]) => `
                    <div class="insight-box">
                        <div class="insight-title"><i class="fa-solid fa-book-open"></i> ${name}</div>
                        <div class="insight-content">${text}</div>
                    </div>`).join('');
            }

            // Related hadiths
            let hadithHtml = '';
            if (item.hadiths && item.hadiths.length > 0) {
                hadithHtml = `
                    <div class="insight-box">
                        <div class="insight-title"><i class="fa-solid fa-scroll"></i> Related Hadith</div>
                        <ul class="hadith-list">
                            ${item.hadiths.map(h => `<li>${h}</li>`).join('')}
                        </ul>
                    </div>`;
            }

            const surahLabel = item.surah_name_roman
                ? `${item.surah_name_en} (${item.surah_name_roman})`
                : item.surah_name_en;

            card.innerHTML = `
                <div class="verse-header">
                    <span class="chapter-badge"><i class="fa-solid fa-book-quran"></i> ${surahLabel} — Verse ${item.ayah_no}</span>
                    <span class="match-score">Match: ${(item.score * 100).toFixed(0)}%</span>
                </div>
                <div class="quran-text">${item.arabic_text}</div>
                <div class="trans-text">${item.english_text}</div>
                ${translationsHtml}
                ${tafseersHtml}
                ${hadithHtml}
            `;
            resultsContainer.appendChild(card);
        });
    }

    searchBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });
});
