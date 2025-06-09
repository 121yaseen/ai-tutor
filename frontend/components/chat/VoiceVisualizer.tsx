import React, { useRef, useEffect } from 'react';
import styles from '../../styles/ChatInterface.module.css';

interface VoiceVisualizerProps {
    analyser: AnalyserNode | null;
    isActive: boolean;
}

const VoiceVisualizer: React.FC<VoiceVisualizerProps> = ({ analyser, isActive }) => {
    const canvasRef = useRef<HTMLCanvasElement | null>(null);
    const animationFrameId = useRef<number | null>(null);

    useEffect(() => {
        if (!analyser || !canvasRef.current || !isActive) {
            if (animationFrameId.current) {
                cancelAnimationFrame(animationFrameId.current);
            }
            return;
        }

        const canvas = canvasRef.current;
        const canvasCtx = canvas.getContext('2d');
        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        const draw = () => {
            if (!canvasCtx || !analyser) return;

            animationFrameId.current = requestAnimationFrame(draw);
            analyser.getByteTimeDomainData(dataArray);

            const { width, height } = canvas;
            canvasCtx.clearRect(0, 0, width, height);

            const baseAmplitude = 5;
            const waveColor = 'rgba(255, 255, 255, 0.7)';
            
            let maxAmplitude = 0;
            for (let i = 0; i < dataArray.length; i++) {
                const v = dataArray[i] / 128.0;
                const amplitude = Math.abs(v - 1.0);
                if(amplitude > maxAmplitude) {
                    maxAmplitude = amplitude;
                }
            }
            
            const dynamicAmplitude = baseAmplitude + (maxAmplitude * height / 3);

            const drawWave = (offset: number, alpha: number, speed: number) => {
                canvasCtx.beginPath();
                canvasCtx.strokeStyle = `rgba(255, 255, 255, ${alpha})`;
                canvasCtx.lineWidth = 2;

                const sliceWidth = width * 1.0 / dataArray.length;
                let x = 0;

                for (let i = 0; i < dataArray.length; i++) {
                    const v = dataArray[i] / 128.0;
                    const y = (v * dynamicAmplitude) + (height / 2) + Math.sin(i * 0.1 + (Date.now() * speed)) * offset;
                    
                    if (i === 0) {
                        canvasCtx.moveTo(x, y);
                    } else {
                        canvasCtx.lineTo(x, y);
                    }
                    x += sliceWidth;
                }
                canvasCtx.stroke();
            };
            
            drawWave(5, 0.4, 0.001);
            drawWave(10, 0.6, 0.002);
            drawWave(2, 0.2, 0.003);
        };

        draw();

        return () => {
            if (animationFrameId.current) {
                cancelAnimationFrame(animationFrameId.current);
            }
        };
    }, [analyser, isActive]);

    return <canvas ref={canvasRef} className={styles.voiceVisualizer} />;
};

export default VoiceVisualizer; 