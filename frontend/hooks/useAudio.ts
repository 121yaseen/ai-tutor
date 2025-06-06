import { useCallback, useRef } from 'react';

// Helper function to stop a media stream
const stopMicrophone = (stream: MediaStream | null) => {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
};

export const useAudio = () => {
    const audioRecorderNode = useRef<AudioWorkletNode | null>(null);
    const audioPlayerNode = useRef<AudioWorkletNode | null>(null);
    const audioRecorderContext = useRef<AudioContext | null>(null);
    const audioPlayerContext = useRef<AudioContext | null>(null);
    const micStream = useRef<MediaStream | null>(null);

    const startAudio = useCallback(async (onAudioData: (data: ArrayBuffer) => void) => {
        try {
            // Player setup
            const playerCtx = new AudioContext({ sampleRate: 24000 });
            audioPlayerContext.current = playerCtx;
            await playerCtx.audioWorklet.addModule('/js/pcm-player-processor.js');
            const playerNode = new AudioWorkletNode(playerCtx, 'pcm-player-processor');
            playerNode.connect(playerCtx.destination);
            audioPlayerNode.current = playerNode;

            // Recorder setup
            const recorderCtx = new AudioContext({ sampleRate: 16000 });
            audioRecorderContext.current = recorderCtx;
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            micStream.current = stream;
            
            const source = recorderCtx.createMediaStreamSource(stream);
            await recorderCtx.audioWorklet.addModule('/js/pcm-recorder-processor.js');
            const recorderNode = new AudioWorkletNode(recorderCtx, 'pcm-recorder-processor');
            
            recorderNode.port.onmessage = (event) => {
                onAudioData(event.data);
            };
            
            source.connect(recorderNode);
            audioRecorderNode.current = recorderNode;

        } catch (error) {
            console.error("Error starting audio:", error);
        }
    }, []);

    const stopAudio = useCallback(() => {
        // Stop microphone stream
        stopMicrophone(micStream.current);
        micStream.current = null;

        // Clean up recorder
        if (audioRecorderNode.current) {
            audioRecorderNode.current.port.postMessage({ command: 'stop' });
            audioRecorderNode.current.disconnect();
            audioRecorderNode.current = null;
        }
        if (audioRecorderContext.current) {
            audioRecorderContext.current.close();
            audioRecorderContext.current = null;
        }

        // Clean up player
        if (audioPlayerNode.current) {
            audioPlayerNode.current.port.postMessage({ command: 'stop' });
            audioPlayerNode.current.disconnect();
            audioPlayerNode.current = null;
        }
        if (audioPlayerContext.current) {
            audioPlayerContext.current.close();
            audioPlayerContext.current = null;
        }
    }, []);

    const playAudio = useCallback((audioData: ArrayBuffer) => {
        if (audioPlayerNode.current) {
            audioPlayerNode.current.port.postMessage(audioData);
        }
    }, []);

    return { startAudio, stopAudio, playAudio };
}; 