import { useState, useCallback, useRef, useEffect } from 'react';
import { useAudio } from './useAudio';

// Helper to convert ArrayBuffer to Base64
const arrayBufferToBase64 = (buffer: ArrayBuffer) => {
    let binary = "";
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
};

// Helper to convert Base64 to ArrayBuffer
const base64ToArray = (base64: string) => {
    const binaryString = window.atob(base64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
};


interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    isPartial?: boolean;
}

// Add voiceWave to the window type
declare global {
    interface Window {
        setVoiceWaveActive: (isActive: boolean) => void;
    }
}

export const useChatSession = () => {
    const [isSessionActive, setIsSessionActive] = useState(false);
    const [isServerReadyForData, setIsServerReadyForData] = useState(false);
    const [conversation, setConversation] = useState<Message[]>([]);
    const { startAudio, stopAudio, playAudio, analyser } = useAudio();
    const eventSource = useRef<EventSource | null>(null);
    const [isThinking, setIsThinking] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);

    const handleAudioData = useCallback((pcmData: ArrayBuffer) => {
        if (isServerReadyForData && eventSource.current && eventSource.current.readyState === EventSource.OPEN) {
            const base64Data = arrayBufferToBase64(pcmData);
            fetch(`/api/send/${sessionStorage.getItem('sessionId')}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mime_type: "audio/pcm", data: base64Data }),
            }).catch(console.error);
        }
    }, [isServerReadyForData]);

    const startSession = useCallback(() => {
        setIsSessionActive(true);
        setIsServerReadyForData(false);
        setConversation([]);
        const sessionId = Math.floor(Math.random() * 1e9).toString();
        sessionStorage.setItem('sessionId', sessionId);

        if (window.setVoiceWaveActive) {
            window.setVoiceWaveActive(true);
        }

        const es = new EventSource(`/events/${sessionId}?is_audio=true`);
        eventSource.current = es;

        es.onopen = () => console.log("SSE connection opened.");
        es.onerror = () => {
            console.log("SSE connection error or closed.");
            stopSession();
        };
        es.onmessage = (event) => {
            const msg = JSON.parse(event.data);

            if (msg.type === "session_ready_for_data") {
                setIsServerReadyForData(true);
                return;
            }

            if (msg.mime_type === "text/plain" && msg.data.trim() === "[thinking]") {
                setIsThinking(true);
                // Clear any previous user "speaking" message
                setConversation(prev => prev.filter(m => m.id !== 'user-turn'));
                return;
            }

            if (msg.turn_complete) {
                setIsThinking(false);
                setIsSpeaking(false);
                // Finalize the last message by removing the partial flag
                setConversation(prev => prev.map(m => 
                    m.id === sessionStorage.getItem('currentMessageId') ? { ...m, isPartial: false } : m
                ));
                sessionStorage.removeItem('currentMessageId');
                return;
            }

            if (msg.mime_type === "audio/pcm" && msg.data) {
                if(isThinking) setIsThinking(false);
                if(!isSpeaking) setIsSpeaking(true);
                playAudio(base64ToArray(msg.data));
            }

            if (msg.mime_type === "text/plain" && msg.data) {
                if(isThinking) setIsThinking(false);
                if(!isSpeaking) setIsSpeaking(true);

                let currentMessageId = sessionStorage.getItem('currentMessageId');
                if (!currentMessageId) {
                    currentMessageId = Math.random().toString(36).substring(7);
                    sessionStorage.setItem('currentMessageId', currentMessageId);
                    setConversation(prev => {
                        const newConversation = prev.filter(m => m.role !== 'user' || !m.isPartial);
                        return [...newConversation, { id: currentMessageId!, role: 'assistant', content: msg.data, isPartial: true }];
                    });
                } else {
                    setConversation(prev => prev.map(m =>
                        m.id === currentMessageId ? { ...m, content: m.content + msg.data } : m
                    ));
                }
            }
        };

        startAudio(handleAudioData);

        // Add a temporary user message
        setConversation(prev => [...prev, {id: 'user-turn', role: 'user', content: 'Listening...', isPartial: true}]);

    }, [startAudio, playAudio, handleAudioData]);

    const stopSession = useCallback(() => {
        if (eventSource.current) {
            eventSource.current.close();
            eventSource.current = null;
        }
        stopAudio();
        setIsSessionActive(false);
        setIsServerReadyForData(false);
        sessionStorage.removeItem('sessionId');
        sessionStorage.removeItem('currentMessageId');
        
        setConversation(prev => prev.map(m => m.isPartial ? {...m, isPartial: false, content: m.content === 'Listening...' ? 'Session ended.' : m.content} : m));

        if (window.setVoiceWaveActive) {
            window.setVoiceWaveActive(false);
        }
    }, [stopAudio]);
    
    // Cleanup on unmount
    useEffect(() => {
        return () => {
            stopSession();
        };
    }, [stopSession]);


    return {
        isSessionActive,
        conversation,
        startSession,
        stopSession,
        analyser,
        isThinking,
        isSpeaking,
    };
}; 