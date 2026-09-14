import { BrowserRouter as Router, Routes, Route, useLocation, Link } from 'react-router-dom'
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
import BartholomewCloudDashboard from './components/BartholomewCloudDashboard'
import Pricing from './components/Pricing'
import Founder from './components/Founder'
import Footer from './components/Footer'
import OperatorPortal from './components/OperatorPortal'


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

// Enterprise Lead Tracking Beacon — fires silently post-load, zero UX impact
function LeadBeaconActivator() {
  const location = useLocation()
  useEffect(() => {
    const beacon = () => {
      fetch('https://bartolomew-cloud-engine-322603900775.us-central1.run.app/api/v1/telemetry/ingest', {
        method: 'POST',
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          events: [{
            event_id: `beacon_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
            timestamp: Date.now() / 1000,
            verdict: 'ALLOW',
            action_type: 'VISITOR_BEACON',
            rule_id: 'RULE_WEB_TELEMETRY',
            reason: `Visitor arrived on path ${location.pathname}`,
            metadata: {
              referrer: document.referrer,
              path: location.pathname,
              screen: `${window.screen.width}x${window.screen.height}`
            }
          }],
          client_version: '5.4.4'
        })
      }).catch(() => { /* silent fail */ })
    }
    if (document.readyState === 'complete') {
      beacon()
    } else {
      window.addEventListener('load', beacon, { once: true })
    }
  }, [location.pathname])
  return null
}

function StoreRedirect() {

  useEffect(() => {
    window.location.href = '/store/'
  }, [])
  return (
    <div className="min-h-[60vh] flex items-center justify-center font-mono text-xs text-zinc-400">
      Redirecting to Bartholomew Defense Store &amp; Pricing...
    </div>
  )
}

function EcosystemGatewayBanner() {
  return (
    <section className="py-16 bg-[#07070a] border-t border-b border-[#1b1b22] relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
        <div className="inline-block px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-xs font-semibold mb-3">
          ENTERPRISE EXPLORER &amp; DOCUMENTATION
        </div>
        <h3 className="text-2xl sm:text-3xl font-bold text-white mb-3 tracking-tight">
          Explore the Full Bartholomew Autonomous Platform
        </h3>
        <p className="text-zinc-400 text-sm max-w-xl mx-auto mb-8">
          Dedicated portals for framework adapters, compliance dossiers, cloud telemetry, and commercial licensing.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 max-w-5xl mx-auto">
          <Link
            to="/cloud"
            className="p-5 rounded-xl bg-[#0d0d14] border border-[#23232e] hover:border-cyan-500/50 transition-all text-left group hover:bg-[#12121c]"
          >
            <div className="text-cyan-400 font-mono text-xs font-bold mb-1 group-hover:translate-x-0.5 transition-transform flex items-center justify-between">
              <span>CLOUD CONSOLE</span>
              <span>&rarr;</span>
            </div>
            <div className="text-white font-bold text-sm mb-1">Live Control Plane</div>
            <div className="text-zinc-500 text-xs leading-relaxed">Multi-agent fleet telemetry, live threat event logs, and SIEM streaming.</div>
          </Link>

          <Link
            to="/cookbook"
            className="p-5 rounded-xl bg-[#0d0d14] border border-[#23232e] hover:border-emerald-500/50 transition-all text-left group hover:bg-[#12121c]"
          >
            <div className="text-emerald-400 font-mono text-xs font-bold mb-1 group-hover:translate-x-0.5 transition-transform flex items-center justify-between">
              <span>INTERACTIVE COOKBOOK</span>
              <span>&rarr;</span>
            </div>
            <div className="text-white font-bold text-sm mb-1">Universal Recipes</div>
            <div className="text-zinc-500 text-xs leading-relaxed">Tested recipes for Claude, OpenAI, Gemini, and AutoGen.</div>
          </Link>

          <Link
            to="/compliance"
            className="p-5 rounded-xl bg-[#0d0d14] border border-[#23232e] hover:border-purple-500/50 transition-all text-left group hover:bg-[#12121c]"
          >
            <div className="text-purple-400 font-mono text-xs font-bold mb-1 group-hover:translate-x-0.5 transition-transform flex items-center justify-between">
              <span>SOC 2 COMPLIANCE</span>
              <span>&rarr;</span>
            </div>
            <div className="text-white font-bold text-sm mb-1">Continuous Audit Pack</div>
            <div className="text-zinc-500 text-xs leading-relaxed">Cryptographic Ed25519 Merkle proof audit timeline &amp; evidence.</div>
          </Link>
        </div>
      </div>
    </section>
  )
}

function HomeView() {
  return (
    <>
      <Hero />
      <EnterpriseEcosystemBanner />
      <DesktopInstallerSection />
      <SecurityThreatModelSection />
      <Pricing />
      <EnterpriseDesignPartnerSection />
      <EcosystemGatewayBanner />
      <Founder />
    </>
  )
}

export default function App() {
  return (
    <Router>
      <ScrollToHash />
      <LeadBeaconActivator />
      <div className="min-h-screen bg-[#040406] text-[#e4e4e7] flex flex-col font-sans selection:bg-[#10b981]/30 selection:text-white">
        <Navbar />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<HomeView />} />
            <Route path="/operator" element={<div className="pt-16"><OperatorPortal /></div>} />
            <Route path="/arena" element={<div className="pt-16"><SwarmArbitrationArena /></div>} />
            <Route path="/cloud" element={<div className="pt-16"><BartholomewCloudDashboard /></div>} />
            <Route path="/cookbook" element={<div className="pt-16"><UniversalCookbookExplorer /></div>} />
            <Route path="/compliance" element={<div className="pt-16"><ContinuousComplianceTimeline /></div>} />
            <Route path="/pricing" element={<div className="pt-16"><Pricing /></div>} />
            <Route path="/store" element={<StoreRedirect />} />
            <Route path="*" element={<HomeView />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  )
}

