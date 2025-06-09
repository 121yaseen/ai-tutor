import { useCallback, useRef, useState } from 'react';

// Helper function to stop a media stream
const stopMicrophone = (stream: MediaStream | null) => {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
};

export const useAudio = () => {
    const audioContextRef = useRef<AudioContext | null>(null);
    const micStreamRef = useRef<MediaStream | null>(null);
    const recorderNodeRef = useRef<AudioWorkletNode | null>(null);
    const playerNodeRef = useRef<AudioWorkletNode | null>(null);
    const audioSourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
    const analyserRef = useRef<AnalyserNode | null>(null);
    
    const [analyser, setAnalyser] = useState<AnalyserNode | null>(null);

    const startAudio = useCallback(async (onAudioData: (data: ArrayBuffer) => void) => {
        try {
            let context = audioContextRef.current;
            if (!context) {
                context = new AudioContext({ sampleRate: 24000 });
                audioContextRef.current = context;
            }

            if (context.state === 'suspended') {
                await context.resume();
            }

            if (!analyserRef.current) {
                const analyserNode = context.createAnalyser();
                analyserNode.fftSize = 2048;
                analyserRef.current = analyserNode;
                setAnalyser(analyserNode);
            }

            if (!playerNodeRef.current) {
                await context.audioWorklet.addModule('/js/pcm-player-processor.js');
                const playerNode = new AudioWorkletNode(context, 'pcm-player-processor');
                playerNode.connect(analyserRef.current!).connect(context.destination);
                playerNodeRef.current = playerNode;
            }

            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            micStreamRef.current = stream;
            
            const source = context.createMediaStreamSource(stream);
            audioSourceRef.current = source;

            await context.audioWorklet.addModule('/js/pcm-recorder-processor.js');
            const recorderNode = new AudioWorkletNode(context, 'pcm-recorder-processor', {
                processorOptions: { inputSampleRate: context.sampleRate, outputSampleRate: 16000 }
            });
            
            recorderNode.port.onmessage = (event) => onAudioData(event.data);
            
            source.connect(recorderNode);
            source.connect(analyserRef.current!);
            recorderNodeRef.current = recorderNode;

        } catch (error) {
            console.error("Error starting audio:", error);
        }
    }, []);

    const stopAudio = useCallback(() => {
        stopMicrophone(micStreamRef.current);
        micStreamRef.current = null;

        if (recorderNodeRef.current) {
            recorderNodeRef.current.disconnect();
            recorderNodeRef.current = null;
        }
        
        if (audioSourceRef.current) {
            audioSourceRef.current.disconnect();
            audioSourceRef.current = null;
        }
        // Do not close the context or disconnect the player/analyser, just stop the source
    }, []);

    const playAudio = useCallback((audioData: ArrayBuffer) => {
        if (playerNodeRef.current && audioContextRef.current?.state === 'running') {
            playerNodeRef.current.port.postMessage(audioData, [audioData]);
        }
    }, []);

    return { startAudio, stopAudio, playAudio, analyser };
}; 