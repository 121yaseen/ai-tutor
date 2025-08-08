'use client'

import { useEffect, useRef } from 'react'

type Particle = {
  x: number
  y: number
  vx: number
  vy: number
  size: number
}

type ParticleBackgroundProps = {
  className?: string
  maxParticles?: number
  speed?: number
}

export default function ParticleBackground({ className = '', maxParticles = 120, speed = 1 }: ParticleBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const animationRef = useRef<number | null>(null)
  const particlesRef = useRef<Particle[]>([])

  useEffect(() => {
    const canvasEl = canvasRef.current as HTMLCanvasElement | null
    if (!canvasEl) return

    const context = canvasEl.getContext('2d')
    if (!context) return
    const ctx = context

    const dpi = Math.min(window.devicePixelRatio || 1, 2)

    function resizeCanvas() {
      const el = canvasEl
      if (!el) return
      const { clientWidth, clientHeight } = el
      el.width = Math.floor(clientWidth * dpi)
      el.height = Math.floor(clientHeight * dpi)
      ctx.scale(dpi, dpi)
    }

    function createParticles() {
      const el = canvasEl
      if (!el) return
      const width = el.clientWidth
      const height = el.clientHeight

      const densityBase = Math.max(60, Math.min(maxParticles, Math.floor((width * height) / 24000)))
      const particles: Particle[] = []
      for (let i = 0; i < densityBase; i += 1) {
        particles.push({
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.3 * speed,
          vy: (Math.random() - 0.5) * 0.3 * speed,
          size: 1.4 + Math.random() * 1.6,
        })
      }
      particlesRef.current = particles
    }

    function step() {
      const el = canvasEl
      if (!el) return
      const width = el.clientWidth
      const height = el.clientHeight

      ctx.clearRect(0, 0, width, height)

      ctx.save()
      ctx.fillStyle = 'rgba(255,255,255,0.35)'
      ctx.shadowBlur = 3
      ctx.shadowColor = 'rgba(255,255,255,0.18)'

      const particles = particlesRef.current
      for (let i = 0; i < particles.length; i += 1) {
        const p = particles[i]
        // Update
        p.x += p.vx
        p.y += p.vy

        // Soft wrap around edges
        if (p.x < -10) p.x = width + 10
        if (p.x > width + 10) p.x = -10
        if (p.y < -10) p.y = height + 10
        if (p.y > height + 10) p.y = -10

        // Draw
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
        ctx.fill()
      }
      ctx.restore()

      animationRef.current = requestAnimationFrame(step)
    }

    // Initialize
    resizeCanvas()
    createParticles()
    step()

    const onResize = () => {
      // Reset transform before resizing to avoid compound scales
      ctx.setTransform(1, 0, 0, 1, 0, 0)
      resizeCanvas()
      createParticles()
    }
    const resizeObserver = new ResizeObserver(onResize)
    if (canvasEl) resizeObserver.observe(canvasEl)

    return () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current)
      resizeObserver.disconnect()
    }
  }, [maxParticles, speed])

  return (
    <div className={`pointer-events-none absolute inset-0 ${className}`}>
      <canvas ref={canvasRef} className="w-full h-full" />
    </div>
  )
}


