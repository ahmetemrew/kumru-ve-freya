document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.getElementById('text-input');
    const seedInput = document.getElementById('seed-input');
    const stepsInput = document.getElementById('steps-input');
    const generateBtn = document.getElementById('generate-btn');
    const btnText = generateBtn.querySelector('.btn-text');
    const btnIcon = generateBtn.querySelector('i');
    const loader = document.getElementById('loader');
    const resultCard = document.getElementById('result-card');
    const audioPlayer = document.getElementById('audio-player');
    const downloadBtn = document.getElementById('download-btn');

    generateBtn.addEventListener('click', async () => {
        const text = textInput.value.trim();
        const seedValue = seedInput.value.trim();
        const stepsValue = stepsInput.value.trim();
        
        if (!text) {
            textInput.style.borderColor = '#ef4444';
            textInput.style.boxShadow = '0 0 0 4px rgba(239, 68, 68, 0.2)';
            setTimeout(() => {
                textInput.style.borderColor = 'rgba(255, 255, 255, 0.2)';
                textInput.style.boxShadow = 'none';
            }, 1000);
            return;
        }

        // Set Loading State
        generateBtn.disabled = true;
        btnText.textContent = 'Ses Üretiliyor...';
        btnIcon.style.display = 'none';
        loader.style.display = 'block';
        resultCard.classList.add('hidden');

        try {
            const payload = { 
                text: text,
                steps: stepsValue ? parseInt(stepsValue) : 32
            };
            if (seedValue) {
                payload.seed = parseInt(seedValue);
            }

            const response = await fetch('/api/synthesize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Bir hata oluştu');
            }

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            
            audioPlayer.src = url;
            downloadBtn.href = url;
            
            resultCard.classList.remove('hidden');
            
            // Auto play the generated audio
            audioPlayer.play().catch(e => console.log("Otomatik oynatma engellendi: ", e));
            
        } catch (error) {
            alert('Hata: ' + error.message);
        } finally {
            // Reset Loading State
            generateBtn.disabled = false;
            btnText.textContent = 'Seslendir';
            btnIcon.style.display = 'inline-block';
            loader.style.display = 'none';
        }
    });

    // Reset border color on input
    textInput.addEventListener('input', () => {
        textInput.style.borderColor = 'rgba(255, 255, 255, 0.2)';
    });
});
