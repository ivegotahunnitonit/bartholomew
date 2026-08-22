import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import DesktopInstallerSection from './components/DesktopInstallerSection'
import InteractiveAgentSandbox from './components/InteractiveAgentSandbox'
import RuntimeThesisProof from './components/RuntimeThesisProof'
import VisualPolicyEditor from './components/VisualPolicyEditor'
import { LiveAttestationInspector } from './components/LiveAttestationInspector'
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
      <DesktopInstallerSection />
      <InteractiveAgentSandbox />
      <RuntimeThesisProof />
      <div id="policy-editor">
        <VisualPolicyEditor />
      </div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <LiveAttestationInspector />
      </div>
      <SDK />
      <LiveAPI />
    </>
  )
}

export default function App() {
  return (
    <Router>
      <ScrollToHash />
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-slate-950">
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
