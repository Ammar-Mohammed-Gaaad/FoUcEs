const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.lang = 'ar-SA';
recognition.interimResults = false;

function startVoiceCommand() {
    const micBtn = document.getElementById('micBtn');
    if (micBtn) micBtn.classList.add('active');
    recognition.start();
}

recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    const aiInput = document.getElementById('chatInput');
    if (aiInput) aiInput.value = transcript;

    // auto send if sendMessage exists
    if (typeof sendChatMessage === "function") sendChatMessage();

    const micBtn = document.getElementById('micBtn');
    if (micBtn) micBtn.classList.remove('active');
};

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
