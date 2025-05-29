document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded and parsed');
    const playStopButton = document.getElementById('playStopButton');
    const statusMessage = document.getElementById('statusMessage');
    let isRecording = false;
    let recognition;

    // Check for browser support for Web Speech API
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const speechSynthesis = window.speechSynthesis;

    if (!SpeechRecognition) {
        console.error('SpeechRecognition API not supported.');
        statusMessage.textContent = 'Speech recognition not supported in this browser. Please try Chrome or Edge.';
        playStopButton.disabled = true;
        return;
    }
    console.log('SpeechRecognition API is supported.');

    if (!speechSynthesis) {
        console.warn('SpeechSynthesis API not supported.');
        statusMessage.textContent = 'Speech synthesis not supported in this browser.';
    } else {
        console.log('SpeechSynthesis API is supported.');
    }

    recognition = new SpeechRecognition();
    recognition.continuous = false; // Process single utterances
    recognition.interimResults = false;
    recognition.lang = 'en-US'; // TODO: Make this configurable if needed
    console.log('SpeechRecognition initialized');

    playStopButton.addEventListener('click', () => {
        console.log('Play/Stop button clicked. isRecording:', isRecording);
        if (isRecording) {
            stopSession();
        } else {
            startSession();
        }
    });

    function startSession() {
        console.log('startSession() called');
        isRecording = true;
        playStopButton.textContent = 'Stop';
        playStopButton.classList.add('stop');
        statusMessage.textContent = 'Listening...';
        try {
            console.log('Attempting to call recognition.start()');
            recognition.start();
            console.log('recognition.start() called successfully');
        } catch (e) {
            console.error("Error calling recognition.start(): ", e.message, e);
            statusMessage.textContent = 'Error starting microphone.';
        }
    }

    function stopSession() {
        console.log('stopSession() called');
        isRecording = false;
        playStopButton.textContent = 'Play';
        playStopButton.classList.remove('stop');
        statusMessage.textContent = 'Click Play to start.';
        try {
            recognition.stop();
            console.log('recognition.stop() called');
        } catch (e) {
            console.error("Error calling recognition.stop():", e.message, e);
        }
        if (speechSynthesis) {
            speechSynthesis.cancel(); // Stop any ongoing speech
            console.log('speechSynthesis.cancel() called');
        }
    }

    recognition.onresult = (event) => {
        console.log('recognition.onresult event fired:', event);
        const transcript = event.results[event.results.length - 1][0].transcript.trim();
        statusMessage.textContent = `Recognized: "${transcript}" | Processing...`;
        console.log('User said (transcript):', transcript);
        sendTextToAgent(transcript);
    };

    recognition.onerror = (event) => {
        console.error('recognition.onerror event fired:', event.error, event);
        if (event.error === 'no-speech') {
            statusMessage.textContent = 'No speech detected. Try again.';
        } else if (event.error === 'audio-capture') {
            statusMessage.textContent = 'Microphone error. Please check permissions.';
        } else if (event.error === 'not-allowed') {
            statusMessage.textContent = 'Microphone access denied. Please allow microphone access and try again.';
        } else {
            statusMessage.textContent = `An error occurred: ${event.error}`;
        }
        
        if (isRecording) {
            console.log('Stopping session due to recognition error while recording.');
            stopSession(); 
        } else {
            playStopButton.textContent = 'Play';
            playStopButton.classList.remove('stop');
        }
    };

    recognition.onend = () => {
        console.log('recognition.onend event fired. isRecording:', isRecording);
        if (isRecording) {
            // If it ended prematurely and we are still in recording mode (e.g., timeout), restart.
            try {
                 if (playStopButton.classList.contains('stop')) { 
                    console.log('Recognition ended while still in recording state, attempting to restart...');
                    recognition.start();
                 }
            } catch (e) {
                console.error("Error restarting recognition from onend: ", e.message, e);
                stopSession();
            }
        } else {
            // This is a normal stop (e.g. user clicked stop, or after successful recognition and processing)
            statusMessage.textContent = 'Click Play to start.';
        }
    };

    async function sendTextToAgent(text) {
        console.log('sendTextToAgent() called with text:', text);
        statusMessage.textContent = `Sending: "${text}"`;
        try {
            const response = await fetch('/process_audio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text }),
            });
            console.log('fetch /process_audio - Response received from Flask:', response);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: response.statusText }));
                console.error('Flask /process_audio API error response:', response.status, errorData);
                speakText(`Sorry, there was an error processing your request: ${errorData.error || response.statusText}`);
                statusMessage.textContent = `Error: ${errorData.error || response.statusText}`;
                return;
            }

            const data = await response.json();
            console.log('Flask /process_audio - JSON data from response:', data);
            statusMessage.textContent = 'Speaking...';
            speakText(data.response);

        } catch (error) {
            console.error('Error in sendTextToAgent (fetching /process_audio):', error);
            speakText('I encountered a network problem connecting to the server. Please try again.');
            statusMessage.textContent = 'Network error. Please try again.';
        }
    }

    function speakText(text) {
        console.log('speakText() called with text:', text);
        if (!speechSynthesis) {
            statusMessage.textContent = "Agent: " + text + " (Speech synthesis not available)";
            if (isRecording) {
                statusMessage.textContent += ' | Listening...';
            }
            return;
        }
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US'; 
        utterance.onend = () => {
            console.log('speechSynthesis.speak() utterance.onend event fired.');
            if (isRecording) {
                statusMessage.textContent = 'Listening...';
                // No need to explicitly call recognition.start() here if recognition.onend handles continuous listening
            } else {
                statusMessage.textContent = 'Click Play to start.';
            }
        };
        utterance.onerror = (event) => {
            console.error('speechSynthesis.speak() utterance.onerror event fired:', event.error, event);
            statusMessage.textContent = 'Error playing audio response.';
            if (isRecording) {
                statusMessage.textContent += ' Try speaking again.';
            }
        };
        speechSynthesis.speak(utterance);
        console.log('speechSynthesis.speak() called.');
    }
}); 