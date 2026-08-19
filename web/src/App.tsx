import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import CorePrimitives from './components/CorePrimitives'
import ObjectiveEngineViewer from './components/ObjectiveEngineViewer'
import VendorNeutralProtocolViewer from './components/VendorNeutralProtocolViewer'
import Applications from './components/Applications'
import ResourceGraphViewer from './components/ResourceGraphViewer'
import AsynchronousReasoning from './components/AsynchronousReasoning'
import OperationsWorkspace from './components/OperationsWorkspace'
import CommandCenter from './components/CommandCenter'
import Simulator from './components/Simulator'
import EpistemicEngines from './components/EpistemicEngines'
import Governance from './components/Governance'
import SDK from './components/SDK'
import LiveAPI from './components/LiveAPI'
import ExecutiveSummary from './components/ExecutiveSummary'
import Footer from './components/Footer'

function ScrollToHash() {
  const location = useLocation()
  
  useEffect(() => {
    if (location.hash) {
      const element = document.getElementById(location.hash.substring(1))
      if (element) {
        // Wait a small tick to ensure render is complete
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
      <CorePrimitives />
      <ObjectiveEngineViewer />
      <VendorNeutralProtocolViewer />
      <Applications />
      <Simulator />
      <CommandCenter />
      <ResourceGraphViewer />
      <AsynchronousReasoning />
      <EpistemicEngines />
      <Governance />
      <SDK />
      <LiveAPI />
      <ExecutiveSummary />
    </>
  )
}

function OperationsView() {
  return (
    <div className="pt-24 pb-16 min-h-screen">
      <OperationsWorkspace />
      <CommandCenter />
      <Simulator />
    </div>
  )
}

function DashboardView() {
  return (
    <div className="pt-24 pb-16 min-h-screen">
      <CommandCenter />
      <OperationsWorkspace />
      <Simulator />
    </div>
  )
}

function SimulatorView() {
  return (
    <div className="pt-24 pb-16 min-h-screen">
      <Simulator />
      <CommandCenter />
    </div>
  )
}

function DocsView() {
  return (
    <div className="pt-24 pb-16 min-h-screen">
      <SDK />
      <LiveAPI />
      <ExecutiveSummary />
    </div>
  )
}

export default function App() {
  return (
    <Router>
      <ScrollToHash />
      <div className="min-h-screen bg-bg text-slate-100 font-sans antialiased selection:bg-cyan-500/20 selection:text-cyan-300 flex flex-col">
        <Navbar />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<HomeView />} />
            <Route path="/operations" element={<OperationsView />} />
            <Route path="/dashboard" element={<DashboardView />} />
            <Route path="/simulator" element={<SimulatorView />} />
            <Route path="/docs" element={<DocsView />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  )
}
