import Hero from '../components/Hero'
import Features from '../components/Features'
import Platforms from '../components/Platforms'
import Architecture from '../components/Architecture'
import CTA from '../components/CTA'
import Footer from '../components/Footer'

export default function Home() {
  return (
    <main>
      <Hero />
      <Features />
      <Platforms />
      <Architecture />
      <CTA />
      <Footer />
    </main>
  )
}