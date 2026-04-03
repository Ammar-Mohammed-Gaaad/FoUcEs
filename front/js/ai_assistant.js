const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SpeechRecognition) {
    const recognition = new SpeechRecognition();
    recognition.lang = 'ar-EG';
    recognition.interimResults = false;

    const micBtn   = document.getElementById('micBtn');
    const micIcon  = document.getElementById('micIcon');
    const chatInput = document.getElementById('chatInput');

    if (micBtn) {
        micBtn.addEventListener('click', () => {
            if (micIcon) micIcon.style.color = '#10b981';
            if (chatInput) chatInput.placeholder = 'جاري الاستماع...';
            recognition.start();
        });
    }

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (chatInput) chatInput.value = transcript;
        if (typeof sendChatMessage === 'function') sendChatMessage();
        if (micIcon) micIcon.style.color = '';
    };

    recognition.onerror = (event) => {
        console.error('Speech Recognition Error:', event.error);
        if (micIcon) micIcon.style.color = '#ef4444';
        if (chatInput) chatInput.placeholder = 'حدث خطأ، حاول مرة أخرى...';
        setTimeout(() => {
            if (micIcon) micIcon.style.color = '';
            if (chatInput) chatInput.placeholder = 'اكتب أمرك هنا...';
        }, 2000);
    };

    recognition.onend = () => {
        if (micIcon) micIcon.style.color = '';
        if (chatInput && chatInput.value === '') chatInput.placeholder = 'اكتب أمرك هنا...';
    };
}

let synth = window.speechSynthesis;
let arabicVoice = null;

function loadVoices() {
    const voices = synth.getVoices();
    arabicVoice = voices.find(v => v.lang.includes('ar')) || voices[0];
}

if (speechSynthesis.onvoiceschanged !== undefined) {
    speechSynthesis.onvoiceschanged = loadVoices;
}

function speakText(text) {
    if (synth.speaking) return;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = arabicVoice;
    utterance.pitch = 1.0;
    utterance.rate = 1.0;
    utterance.lang = 'ar-SA';
    synth.speak(utterance);
}
