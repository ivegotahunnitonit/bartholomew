import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import EnterpriseEcosystemBanner from './components/EnterpriseEcosystemBanner'
import DesktopInstallerSection from './components/DesktopInstallerSection'
import SecurityThreatModelSection from './components/SecurityThreatModelSection'
import SwarmArbitrationArena from './components/SwarmArbitrationArena'
import UniversalCookbookExplorer from './components/UniversalCookbookExplorer'
import EnterpriseDesignPartnerSection from './components/EnterpriseDesignPartnerSection'
import ContinuousComplianceTimeline from './components/ContinuousComplianceTimeline'
import Founder from './components/Founder'
import Footer from './components/Footer'

function ScrollToHash() {
  const location = useLocation()
  
  useEffect(() => {
    if (location.hash) {
      const element = document.getElementById(location.hash.substring(1))
      if (element) {
        setTimeout(() => {
          element.scrollIntoView({ behavior: 'smooth' })
        }, 100)
      }
    } else {
      window.scrollTo({ top: 0, left: 0, behavior: 'smooth' })
    }
  }, [location])
  
  return null
}

function HomeView() {
  return (
    <>
      <Hero />
      <EnterpriseEcosystemBanner />
      <DesktopInstallerSection />
      <SecurityThreatModelSection />
      <SwarmArbitrationArena />
      <UniversalCookbookExplorer />
      <EnterpriseDesignPartnerSection />
      <ContinuousComplianceTimeline />
      <Founder />
    </>
  )
}

export default function App() {
  return (
    <Router>
      <ScrollToHash />
      <div className="min-h-screen bg-[#040406] text-[#e4e4e7] flex flex-col font-sans selection:bg-[#10b981]/30 selection:text-white">
        <Navbar />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<HomeView />} />
            <Route path="*" element={<HomeView />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  )
}
