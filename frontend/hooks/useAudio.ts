import { useCallback, useRef, useState } from 'react';

// Helper function to stop a media stream
const stopMicrophone = (stream: MediaStream | null) => {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
};

export const useAudio = () => {
    const audioContextRef = useRef<AudioContext | null>(null);
    const mediaStreamRef = useRef<MediaStream | null>(null);
    
    // For recording
    const recorderWorkletNodeRef = useRef<AudioWorkletNode | null>(null);
    const mediaStreamSourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
    
    // For playback
    const playerWorkletNodeRef = useRef<AudioWorkletNode | null>(null);

    // For visualization
    const analyserRef = useRef<AnalyserNode | null>(null);
    const [analyser, setAnalyser] = useState<AnalyserNode | null>(null);

    const initializeAudio = async () => {
        if (!audioContextRef.current) {
            const context = new AudioContext({ sampleRate: 24000 });
            audioContextRef.current = context;

            const analyserNode = context.createAnalyser();
            analyserNode.fftSize = 2048;
            analyserRef.current = analyserNode;
            setAnalyser(analyserNode);

            // Connect analyser to destination to allow it to be part of the graph
            analyserNode.connect(context.destination);

            // Setup player worklet once
            await context.audioWorklet.addModule('/js/pcm-player-processor.js');
            const playerNode = new AudioWorkletNode(context, 'pcm-player-processor');
            playerNode.connect(analyserNode);
            playerWorkletNodeRef.current = playerNode;
        }

        if (audioContextRef.current.state === 'suspended') {
            await audioContextRef.current.resume();
        }
    };

    const startRecording = useCallback(async (onAudioData: (data: ArrayBuffer) => void) => {
        try {
            await initializeAudio();
            const context = audioContextRef.current!;

            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaStreamRef.current = stream;
            
            mediaStreamSourceRef.current = context.createMediaStreamSource(stream);

            await context.audioWorklet.addModule('/js/pcm-recorder-processor.js');
            const recorderNode = new AudioWorkletNode(context, 'pcm-recorder-processor');
            
            recorderNode.port.onmessage = (event) => onAudioData(event.data);
            
            mediaStreamSourceRef.current.connect(recorderNode);
            if (analyserRef.current) {
                mediaStreamSourceRef.current.connect(analyserRef.current);
            }
            
            recorderWorkletNodeRef.current = recorderNode;

        } catch (error) {
            console.error("Error starting audio recording:", error);
        }
    }, []);

    const stopRecording = useCallback(() => {
        if (mediaStreamRef.current) {
            mediaStreamRef.current.getTracks().forEach(track => track.stop());
            mediaStreamRef.current = null;
        }

        if (recorderWorkletNodeRef.current) {
            recorderWorkletNodeRef.current.port.onmessage = null;
            recorderWorkletNodeRef.current.disconnect();
            recorderWorkletNodeRef.current = null;
        }
        
        if (mediaStreamSourceRef.current) {
            mediaStreamSourceRef.current.disconnect();
            mediaStreamSourceRef.current = null;
        }

        // Suspend the context to save resources when not in use
        if (audioContextRef.current && audioContextRef.current.state === 'running') {
            audioContextRef.current.suspend();
        }

        // Also stop any ongoing playback
        if (playerWorkletNodeRef.current) {
            // A 'stop' message could be implemented in the worklet if needed
        }
    }, []);

    const playAudio = useCallback((audioData: ArrayBuffer) => {
        if (playerWorkletNodeRef.current && audioContextRef.current?.state === 'running') {
            playerWorkletNodeRef.current.port.postMessage({ type: 'data', buffer: audioData }, [audioData]);
        }
    }, []);

    return { startRecording, stopRecording, playAudio, analyser };
}; 