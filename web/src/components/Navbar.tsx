import { useState, useEffect, useRef } from 'react'
import { ChevronDown, ShieldCheck, Cpu, Code2, Terminal, Lock } from 'lucide-react'
import Logo from './Logo'

import { Link } from 'react-router-dom'

interface NavCategory {
  title: string
  icon: any
  items: { label: string; href: string; description?: string }[]
}

const CATEGORIZED_NAV: NavCategory[] = [
  {
    title: 'Protocol & Architecture',
    icon: Cpu,
    items: [
      { label: 'Core Primitives', href: '/#primitives', description: 'Perceive, Reason, Verify, Act, Learn' },
      { label: 'Objective Engine', href: '/#objective-engine', description: 'Closed-loop utility vs risk control' },
      { label: 'BTP Protocol (v0.1)', href: '/#protocol', description: 'Vendor-neutral zero-trust trust fabric' },
      { label: 'Resource Graph', href: '/#resource-graph', description: 'Multi-party exchange cycle discovery' },
      { label: 'Async Reasoning', href: '/#async-reasoning', description: 'Continuous offline scenario replay' },
    ]
  },
  {
    title: 'Applications & Solutions',
    icon: ShieldCheck,
    items: [
      { label: 'Application Domains', href: '/#applications', description: 'Security, Research, Swarm Orchestration' },
      { label: 'Executive Briefing', href: '/#executive-summary', description: 'Strategic posture & ROI overview' },
    ]
  },
  {
    title: 'Operations Workspace',
    icon: Terminal,
    items: [
      { label: 'Operations Command Center', href: '/operations', description: 'Role-gated task & agent management' },
      { label: 'Threat Simulator', href: '/operations#simulator', description: 'OWASP & trajectory attack simulation' },
      { label: 'Epistemic Engines', href: '/#engines', description: 'Bayesian contradiction & risk analysis' },
    ]
  },
  {
    title: 'Developers & Spec',
    icon: Code2,
    items: [
      { label: 'SDK & REST API', href: '/#sdk', description: 'Python, Node, Go, Rust BTP integration' },
      { label: 'BTP Test Vectors', href: '/api/v1/btp/test-vectors', description: 'Language-neutral RFC 8785 vectors' },
    ]
  }
]

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null)
  const [mobileOpen, setMobileOpen] = useState(false)
  const navRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const scrollHandler = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', scrollHandler, { passive: true })
    return () => window.removeEventListener('scroll', scrollHandler)
  }, [])

  useEffect(() => {
    const clickOutsideHandler = (e: MouseEvent) => {
      if (navRef.current && !navRef.current.contains(e.target as Node)) {
        setActiveDropdown(null)
      }
    }
    document.addEventListener('mousedown', clickOutsideHandler)
    return () => document.removeEventListener('mousedown', clickOutsideHandler)
  }, [])

  return (
    <header
      ref={navRef}
      className="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
      style={{
        background: scrolled ? 'rgba(3, 11, 24, 0.95)' : 'rgba(3, 11, 24, 0.8)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        borderBottom: scrolled ? '1px solid rgba(255,255,255,0.08)' : '1px solid rgba(255,255,255,0.04)',
      }}
    >
      <div className="max-w-7xl mx-auto px-5 sm:px-8 flex items-center justify-between h-16">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2.5 no-underline group">
          <Logo size={34} />
        </Link>

        {/* Categorized Dropdown Navigation */}
        <nav className="hidden lg:flex items-center gap-1">
          {CATEGORIZED_NAV.map((cat) => {
            const Icon = cat.icon
            const isOpen = activeDropdown === cat.title
            return (
              <div key={cat.title} className="relative">
                <button
                  onClick={() => setActiveDropdown(isOpen ? null : cat.title)}
                  className={`px-3.5 py-2 rounded-xl text-xs font-semibold tracking-wide transition-all duration-200 flex items-center gap-1.5 ${
                    isOpen ? 'bg-white/10 text-white' : 'text-slate-300 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <Icon size={14} className="text-cyan-400" />
                  <span>{cat.title}</span>
                  <ChevronDown
                    size={13}
                    className={`transition-transform duration-200 text-slate-400 ${isOpen ? 'rotate-180 text-white' : ''}`}
                  />
                </button>

                {/* Dropdown Menu */}
                {isOpen && (
                  <div className="absolute top-full left-0 mt-2 w-72 p-2 rounded-2xl bg-slate-950/95 border border-white/10 shadow-2xl backdrop-blur-xl z-50 animate-fadeIn space-y-1">
                    {cat.items.map((item) => (
                      item.href.startsWith('http') ? (
                        <a
                          key={item.href}
                          href={item.href}
                          onClick={() => setActiveDropdown(null)}
                          className="block p-2.5 rounded-xl hover:bg-white/5 text-left transition-all no-underline group"
                        >
                          <div className="text-xs font-bold text-slate-200 group-hover:text-cyan-300 flex items-center justify-between">
                            <span>{item.label}</span>
                          </div>
                          {item.description && (
                            <div className="text-[10px] text-slate-400 mt-0.5 font-sans">
                              {item.description}
                            </div>
                          )}
                        </a>
                      ) : (
                        <Link
                          key={item.href}
                          to={item.href}
                          onClick={() => setActiveDropdown(null)}
                          className="block p-2.5 rounded-xl hover:bg-white/5 text-left transition-all no-underline group"
                        >
                          <div className="text-xs font-bold text-slate-200 group-hover:text-cyan-300 flex items-center justify-between">
                            <span>{item.label}</span>
                          </div>
                          {item.description && (
                            <div className="text-[10px] text-slate-400 mt-0.5 font-sans">
                              {item.description}
                            </div>
                          )}
                        </Link>
                      )
                    ))}
                  </div>
                )}
              </div>
            )
          })}
        </nav>

        {/* Action Buttons */}
        <div className="hidden md:flex items-center gap-3">
          <Link
            to="/operations"
            className="px-3.5 py-2 rounded-xl text-xs font-bold bg-slate-900 border border-cyan-500/30 text-cyan-300 hover:border-cyan-400/60 transition-all flex items-center gap-1.5"
          >
            <Lock size={13} />
            Operations Workspace
          </Link>
          <Link
            to="/#protocol"
            className="btn-primary py-2 px-4 text-xs font-bold"
          >
            Deploy Protocol
          </Link>
        </div>

        {/* Mobile Hamburger */}
        <button
          className="lg:hidden p-2 rounded-lg text-slate-400 hover:text-white"
          onClick={() => setMobileOpen(o => !o)}
          aria-label="Toggle menu"
        >
          <div className="w-5 flex flex-col gap-1.5">
            <span className={`block h-0.5 bg-current rounded transition-all ${mobileOpen ? 'rotate-45 translate-y-2' : ''}`} />
            <span className={`block h-0.5 bg-current rounded transition-all ${mobileOpen ? 'opacity-0' : ''}`} />
            <span className={`block h-0.5 bg-current rounded transition-all ${mobileOpen ? '-rotate-45 -translate-y-2' : ''}`} />
          </div>
        </button>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileOpen && (
        <div className="lg:hidden p-5 bg-slate-950 border-b border-white/10 space-y-4 max-h-[80vh] overflow-y-auto">
          {CATEGORIZED_NAV.map((cat) => (
            <div key={cat.title} className="space-y-2">
              <div className="text-xs font-bold text-cyan-400 uppercase tracking-wider font-mono">
                {cat.title}
              </div>
              <div className="space-y-1 pl-2">
                {cat.items.map((item) => (
                  item.href.startsWith('http') ? (
                    <a
                      key={item.href}
                      href={item.href}
                      onClick={() => setMobileOpen(false)}
                      className="block py-1.5 text-xs text-slate-300 hover:text-white"
                    >
                      {item.label}
                    </a>
                  ) : (
                    <Link
                      key={item.href}
                      to={item.href}
                      onClick={() => setMobileOpen(false)}
                      className="block py-1.5 text-xs text-slate-300 hover:text-white"
                    >
                      {item.label}
                    </Link>
                  )
                ))}
              </div>
            </div>
          ))}
          <div className="pt-3 border-t border-white/10 flex flex-col gap-2">
            <Link to="/operations" onClick={() => setMobileOpen(false)} className="btn-secondary text-center text-xs py-2">
              Operations Workspace
            </Link>
            <Link to="/#protocol" onClick={() => setMobileOpen(false)} className="btn-primary text-center text-xs py-2">
              Deploy Protocol
            </Link>
          </div>
        </div>
      )}
    </header>
  )
}
