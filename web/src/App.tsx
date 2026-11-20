import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import ParticleButton from '@/components/kokonutui/particle-button'

export default function App() {
  const title = useRef<HTMLHeadingElement>(null)
  useEffect(() => {
    gsap.from(title.current, { y: -30, opacity: 0, duration: 0.8 })
  }, [])
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6">
      <h1 ref={title} className="text-3xl font-bold">DownloadWeb</h1>
      <ParticleButton>Download</ParticleButton>
    </main>
  )
}
