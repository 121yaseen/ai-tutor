// voiceWave.js - Enhanced Futuristic Animation

const canvas = document.createElement('canvas');
canvas.width = 300; // Slightly larger for more space
canvas.height = 300;
canvas.style.width = '100%';
canvas.style.height = '100%';
canvas.style.display = 'block';

const ctx = canvas.getContext('2d');
const centerX = canvas.width / 2;
const centerY = canvas.height / 2;
const baseRadius = 80; // Adjusted base radius
const waveCount = 4; // Increased wave count for complexity
const idleWaveColors = [
  'rgba(100, 125, 222, 0.2)', // Softer blue
  'rgba(127, 83, 172, 0.15)', // Softer purple
  'rgba(200, 200, 255, 0.1)', // Faint white glow
  'rgba(150, 100, 200, 0.08)' // Fainter purple accent
];
const activeWaveColors = [
  'rgba(173, 216, 230, 0.4)', // Light blue, more prominent
  'rgba(221, 160, 221, 0.3)', // Orchid, more prominent
  'rgba(255, 255, 255, 0.25)', // Brighter white glow
  'rgba(199, 21, 133, 0.2)'  // MediumVioletRed accent, more prominent
];

let isActive = false;
let particles = [];
const particleCount = 30;

window.setVoiceWaveActive = function(active) {
  isActive = !!active;
  if (isActive && particles.length === 0) {
    for (let i = 0; i < particleCount; i++) {
      particles.push(createParticle());
    }
  } else if (!isActive) {
    particles = []; // Clear particles when inactive
  }
};

function createParticle() {
  return {
    x: centerX,
    y: centerY,
    radius: Math.random() * 1.5 + 0.5, // Smaller particles
    color: `rgba(255, 255, 255, ${Math.random() * 0.4 + 0.2})`,
    angle: Math.random() * Math.PI * 2,
    speed: Math.random() * 0.02 + 0.01, // Slower, more drift
    distance: baseRadius * 0.8 + Math.random() * (baseRadius * 0.4) // Keep within inner area
  };
}

function drawWave(time, waveIndex) {
  ctx.save();
  ctx.beginPath();
  const points = 70; // More points for smoother waves
  const angleStep = (Math.PI * 2) / points;
  const colors = isActive ? activeWaveColors : idleWaveColors;

  const baseMod = isActive ? 15 : 8;
  const radiusModFactor = isActive ? 1.3 : 1;
  const timeFactor = isActive ? 1.8 : 1.1;
  const overallAmplitudeFactor = isActive ? 1.1 : 1.0;

  const radiusMod = baseMod + waveIndex * (isActive ? 10 : 6);
  
  for (let i = 0; i <= points; i++) {
    const angle = i * angleStep;
    const wave = Math.sin(angle * (3 + waveIndex * 0.3) + time * timeFactor + waveIndex * 1.5) * radiusMod * radiusModFactor;
    const r = (baseRadius + wave + waveIndex * (10 - waveIndex * 1.5) + Math.sin(time * 0.8 + waveIndex) * (isActive ? 6 : 3)) * overallAmplitudeFactor;
    const x = centerX + Math.cos(angle) * r;
    const y = centerY + Math.sin(angle) * r;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.closePath();
  
  let color = colors[waveIndex];
  if (isActive && waveIndex < 2) { // More intense color pulse for inner waves when active
    const pulse = 0.6 + 0.4 * Math.sin(time * (2.5 + waveIndex * 0.5));
    color = waveIndex === 0 ? `rgba(255, 105, 180, ${0.3 + 0.4 * pulse})` : `rgba(135, 206, 250, ${0.25 + 0.35 * pulse})`;
  }

  ctx.shadowColor = color;
  ctx.shadowBlur = isActive ? (30 - waveIndex * 5) : (20 - waveIndex * 4); // Softer, larger shadows
  // Make the outermost wave (border) much fainter to blend, especially when idle
  if (waveIndex === waveCount -1) { // Assuming waveCount-1 is the outermost wave
    ctx.globalAlpha = isActive ? 0.3 : 0.15; // More visible when active, very faint when idle
  } else {
    ctx.globalAlpha = 1.0;
  }
  ctx.strokeStyle = color;
  ctx.lineWidth = isActive ? (1.5 + (waveCount - waveIndex) * 0.3) : (1 + (waveCount - waveIndex) * 0.25); // Thinner lines
  ctx.stroke();
  ctx.restore();
}

function drawParticles(time) {
  if (!isActive || particles.length === 0) return;

  particles.forEach(p => {
    p.angle += p.speed;
    const x = centerX + Math.cos(p.angle) * p.distance * (1 + Math.sin(time + p.angle) * 0.05);
    const y = centerY + Math.sin(p.angle) * p.distance * (1 + Math.cos(time + p.angle) * 0.05);
    
    ctx.beginPath();
    ctx.arc(x, y, p.radius, 0, Math.PI * 2);
    ctx.fillStyle = p.color;
    ctx.fill();
  });
}

function animate() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const time = performance.now() / 1000; // Slow down overall animation speed a bit
  
  drawParticles(time);

  for (let i = waveCount - 1; i >= 0; i--) {
    drawWave(time, i);
  }
  requestAnimationFrame(animate);
}

window.addEventListener('DOMContentLoaded', () => {
  const waveDiv = document.getElementById('voiceWave');
  if (waveDiv) {
    waveDiv.innerHTML = ''; // Clear any existing content
    waveDiv.appendChild(canvas);
    animate();
  }
}); 