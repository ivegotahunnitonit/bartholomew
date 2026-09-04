import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import EnterpriseEcosystemBanner from './components/EnterpriseEcosystemBanner'
import DesktopInstallerSection from './components/DesktopInstallerSection'
import SecurityThreatModelSection from './components/SecurityThreatModelSection'
import InteractiveAgentSandbox from './components/InteractiveAgentSandbox'
import RuntimeThesisProof from './components/RuntimeThesisProof'
import VisualPolicyEditor from './components/VisualPolicyEditor'
import { LiveAttestationInspector } from './components/LiveAttestationInspector'
import EnterpriseDesignPartnerSection from './components/EnterpriseDesignPartnerSection'
import ContinuousComplianceTimeline from './components/ContinuousComplianceTimeline'
import Founder from './components/Founder'
import SDK from './components/SDK'
import LiveAPI from './components/LiveAPI'
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
      <InteractiveAgentSandbox />
      <EnterpriseDesignPartnerSection />
      <RuntimeThesisProof />
      <div id="policy-editor">
        <VisualPolicyEditor />
      </div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <LiveAttestationInspector />
      </div>
      <ContinuousComplianceTimeline />
      <Founder />
      <SDK />
      <LiveAPI />
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
