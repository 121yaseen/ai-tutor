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
        const canvas = canvasRef.current;
        if (!canvas) return;

        const canvasCtx = canvas.getContext('2d');
        if (!canvasCtx) return;

        const draw = (time: number) => {
            animationFrameId.current = requestAnimationFrame(draw);
            const { width, height } = canvas;
            canvasCtx.clearRect(0, 0, width, height);

            const centerX = width / 2;
            const centerY = height / 2;
            const baseRadius = Math.min(width, height) / 4;
            const numPoints = 128;

            let dataArray: Uint8Array | null = null;
            if (analyser) {
                dataArray = new Uint8Array(analyser.frequencyBinCount);
                analyser.getByteTimeDomainData(dataArray);
            }

            const drawWave = (color: string, lineWidth: number, amplitude: number, offset: number) => {
                canvasCtx.beginPath();
                canvasCtx.strokeStyle = color;
                canvasCtx.lineWidth = lineWidth;
                canvasCtx.globalAlpha = 0.7;

                for (let i = 0; i <= numPoints; i++) {
                    const angle = (i / numPoints) * 2 * Math.PI;
                    const dataIndex = Math.floor((i / numPoints) * (dataArray?.length || 1));
                    
                    let displacement = 0;
                    if (isActive && dataArray) {
                        displacement = ((dataArray[dataIndex] - 128) / 128) * amplitude;
                    } else {
                        const passiveWave = Math.sin(angle * 10 + time * 0.002) * 2;
                        const breathing = Math.sin(time * 0.001) * 3;
                        displacement = passiveWave + breathing;
                    }

                    const radius = baseRadius + displacement + offset;
                    const x = centerX + radius * Math.cos(angle);
                    const y = centerY + radius * Math.sin(angle);

                    if (i === 0) {
                        canvasCtx.moveTo(x, y);
                    } else {
                        canvasCtx.lineTo(x, y);
                    }
                }
                canvasCtx.closePath();
                canvasCtx.stroke();
            };
            
            drawWave('#0084ff', 1.5, baseRadius * 0.4, 0);
            drawWave('rgba(0, 132, 255, 0.5)', 1, baseRadius * 0.5, 5);
            drawWave('rgba(0, 132, 255, 0.2)', 0.5, baseRadius * 0.3, -5);
        };

        draw(0);

        return () => {
            if (animationFrameId.current) {
                cancelAnimationFrame(animationFrameId.current);
            }
        };
    }, [analyser, isActive]);

    // Ensure canvas is scaled correctly for high-DPI displays
    useEffect(() => {
        const canvas = canvasRef.current;
        if (canvas) {
            const dpr = window.devicePixelRatio || 1;
            const rect = canvas.getBoundingClientRect();
            canvas.width = rect.width * dpr;
            canvas.height = rect.height * dpr;
            const ctx = canvas.getContext('2d');
            ctx?.scale(dpr, dpr);
        }
    }, []);

    return <canvas ref={canvasRef} className={styles.voiceVisualizer} />;
};

export default VoiceVisualizer; 