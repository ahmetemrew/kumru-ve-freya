document.addEventListener('DOMContentLoaded', () => {
    const micBtn = document.getElementById('mic-btn');
    const statusText = document.getElementById('status-text');
    const chatHistory = document.getElementById('chat-history');
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        statusText.textContent = "Tarayıcınız ses tanımayı desteklemiyor (Chrome kullanın).";
        micBtn.disabled = true;
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'tr-TR';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    let isListening = false;
    let isProcessing = false;
    let audioContext = null;
    let conversationHistory = [];

    micBtn.addEventListener('click', () => {
        if (isProcessing) return;
        
        if (!audioContext) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }

        if (isListening) {
            recognition.stop();
        } else {
            recognition.start();
        }
    });

    recognition.onstart = () => {
        isListening = true;
        micBtn.classList.add('listening');
        micBtn.innerHTML = '<i class="fa-solid fa-stop"></i>';
        statusText.textContent = "Sizi dinliyorum...";
    };

    recognition.onend = () => {
        isListening = false;
        if (!isProcessing) {
            resetMicBtn();
        }
    };

    recognition.onerror = (e) => {
        isListening = false;
        resetMicBtn();
        console.error("Speech recognition error", e);
    };

    recognition.onresult = async (event) => {
        const transcript = event.results[0][0].transcript;
        addMessage(transcript, 'user');
        conversationHistory.push({ role: 'user', content: transcript });
        
        isProcessing = true;
        micBtn.classList.remove('listening');
        micBtn.classList.add('processing');
        micBtn.innerHTML = '<i class="fa-solid fa-spinner"></i>';
        statusText.textContent = "Freya düşünüyor ve konuşuyor...";

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ history: conversationHistory })
            });

            if (!response.ok) {
                const err = await response.json();
                let errDetail = err.detail;
                if (typeof errDetail === 'object') {
                    errDetail = JSON.stringify(errDetail);
                }
                throw new Error(errDetail || "Sunucu hatası");
            }

            const data = await response.json();
            addMessage(data.text, 'system');
            conversationHistory.push({ role: 'model', content: data.text });

            const audioRes = await fetch(data.audio_url);
            const arrayBuffer = await audioRes.arrayBuffer();
            const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
            
            const source = audioContext.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(audioContext.destination);
            source.start(0);
            
            source.onended = () => {
                isProcessing = false;
                resetMicBtn();
                // Otomatik dinlemeye geç
                setTimeout(() => {
                    if (!isListening) micBtn.click();
                }, 500);
            };
            
        } catch (error) {
            console.error(error);
            addMessage("Hata: " + error.message, 'system');
            isProcessing = false;
            resetMicBtn();
        }
    };

    function resetMicBtn() {
        micBtn.classList.remove('processing', 'listening');
        micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
        statusText.textContent = "Dinlemek için mikrofona bas...";
    }

    function addMessage(text, type) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${type}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.innerHTML = type === 'user' ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-robot"></i>';
        
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        bubble.textContent = text;
        
        msgDiv.appendChild(avatar);
        msgDiv.appendChild(bubble);
        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
});
