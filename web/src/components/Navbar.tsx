import { useState, useEffect } from 'react'
import { Code2, Download, ExternalLink, Menu, X } from 'lucide-react'
import { Link } from 'react-router-dom'
import Logo from './Logo'

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    const scrollHandler = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', scrollHandler, { passive: true })
    return () => window.removeEventListener('scroll', scrollHandler)
  }, [])

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-200 ${
        scrolled ? 'bg-slate-950/90 backdrop-blur-md border-b border-slate-800/80 shadow-lg' : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-3 no-underline">
          <Logo />
          <div className="flex flex-col">
            <span className="font-extrabold text-sm sm:text-base tracking-tight text-white font-mono">
              BARTHOLOMEW
            </span>
            <span className="text-[10px] text-cyan-400 font-mono tracking-wider -mt-1 font-semibold">
              AI SAFETY INFRASTRUCTURE
            </span>
          </div>
        </Link>

        {/* Desktop Nav Links in Layman Terms */}
        <nav className="hidden lg:flex items-center gap-6 text-xs font-semibold text-slate-300">
          <a href="#how-it-works" className="hover:text-cyan-400 transition">
            How It Works
          </a>
          <a href="#download" className="hover:text-cyan-400 transition">
            Install CLI
          </a>
          <a href="#policy-editor" className="hover:text-cyan-400 transition">
            Rule Editor
          </a>
          <a href="#sdk" className="hover:text-cyan-400 transition">
            1-Line SDKs
          </a>
          <a href="#live-api" className="hover:text-cyan-400 transition">
            API Specs
          </a>
        </nav>

        {/* Action Buttons */}
        <div className="hidden sm:flex items-center gap-3">
          <a
            href="#download"
            className="px-3.5 py-2 rounded-xl text-xs font-bold bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/20 hover:border-cyan-400/60 transition flex items-center gap-1.5"
          >
            <Download size={13} />
            Install CLI
          </a>
          <a
            href="https://github.com/ivegotahunnitonit/bartholomew"
            target="_blank"
            rel="noopener noreferrer"
            className="px-3.5 py-2 rounded-xl text-xs font-bold bg-slate-900 border border-slate-700 text-slate-200 hover:text-white hover:border-slate-500 transition flex items-center gap-1.5"
          >
            <Code2 size={13} />
            GitHub
            <ExternalLink size={11} className="text-slate-400" />
          </a>
        </div>

        {/* Mobile Hamburger */}
        <button
          className="lg:hidden p-2 rounded-lg text-slate-400 hover:text-white"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle menu"
        >
          {mobileOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile Dropdown */}
      {mobileOpen && (
        <div className="lg:hidden bg-slate-950 border-b border-slate-800 px-4 py-4 space-y-3">
          <a
            href="#how-it-works"
            onClick={() => setMobileOpen(false)}
            className="block text-sm font-semibold text-slate-200 hover:text-cyan-400"
          >
            How It Works
          </a>
          <a
            href="#download"
            onClick={() => setMobileOpen(false)}
            className="block text-sm font-semibold text-slate-200 hover:text-cyan-400"
          >
            Install CLI
          </a>
          <a
            href="#policy-editor"
            onClick={() => setMobileOpen(false)}
            className="block text-sm font-semibold text-slate-200 hover:text-cyan-400"
          >
            Rule Editor
          </a>
          <a
            href="#sdk"
            onClick={() => setMobileOpen(false)}
            className="block text-sm font-semibold text-slate-200 hover:text-cyan-400"
          >
            1-Line SDKs
          </a>
          <a
            href="#live-api"
            onClick={() => setMobileOpen(false)}
            className="block text-sm font-semibold text-slate-200 hover:text-cyan-400"
          >
            API Specs
          </a>
        </div>
      )}
    </header>
  )
}
