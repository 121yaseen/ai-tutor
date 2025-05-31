// voiceWave.js
// Futuristic animated voice wave for the AI Tutor UI

const canvas = document.createElement('canvas');
canvas.width = 260;
canvas.height = 260;
canvas.style.width = '100%';
canvas.style.height = '100%';
canvas.style.display = 'block';

const ctx = canvas.getContext('2d');
const centerX = canvas.width / 2;
const centerY = canvas.height / 2;
const baseRadius = 90;
const waveCount = 3;
const waveColors = [
  'rgba(127,83,172,0.5)',
  'rgba(100,125,222,0.3)',
  'rgba(255,255,255,0.08)'
];

let isActive = false;

window.setVoiceWaveActive = function(active) {
  isActive = !!active;
};

function drawWave(time, waveIndex) {
  ctx.save();
  ctx.beginPath();
  const points = 64;
  const angleStep = (Math.PI * 2) / points;
  const baseMod = isActive ? 18 : 10;
  const radiusMod = baseMod + waveIndex * (isActive ? 12 : 8);
  for (let i = 0; i <= points; i++) {
    const angle = i * angleStep;
    const wave = Math.sin(angle * 3 + time * (isActive ? 2.2 : 1.2) + waveIndex * 1.5) * radiusMod * (isActive ? 1.2 : 1);
    const r = baseRadius + wave + waveIndex * 12 + Math.sin(time + waveIndex) * (isActive ? 8 : 4);
    const x = centerX + Math.cos(angle) * r;
    const y = centerY + Math.sin(angle) * r;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.closePath();
  let color = waveColors[waveIndex];
  if (isActive && waveIndex === 0) {
    const pulse = 0.5 + 0.5 * Math.sin(time * 2);
    color = `rgba(255, 99, 255, ${0.4 + 0.3 * pulse})`;
  }
  ctx.shadowColor = color;
  ctx.shadowBlur = 24 - waveIndex * 6;
  ctx.strokeStyle = color;
  ctx.lineWidth = 2 + (waveCount - waveIndex);
  ctx.stroke();
  ctx.restore();
}

function animate() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const time = performance.now() / 900;
  for (let i = waveCount - 1; i >= 0; i--) {
    drawWave(time, i);
  }
  requestAnimationFrame(animate);
}

window.addEventListener('DOMContentLoaded', () => {
  const waveDiv = document.getElementById('voiceWave');
  if (waveDiv) {
    waveDiv.innerHTML = '';
    waveDiv.appendChild(canvas);
    animate();
  }
}); 