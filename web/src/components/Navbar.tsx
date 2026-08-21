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
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-150 ${
        scrolled ? 'bg-black/95 border-b border-[#222222] backdrop-blur-md shadow-2xl' : 'bg-black/50 backdrop-blur-sm'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo & Box Status Tag */}
        <div className="flex items-center gap-4">
          <Link to="/" className="flex items-center no-underline" aria-label="Bartholomew Home">
            <Logo size={28} showText={true} />
          </Link>
          <div className="hidden sm:flex items-center gap-2 px-3 py-1 bg-[#0a0a0a] border border-[#2a2a2a] text-xs font-mono">
            <span className="w-2 h-2 bg-[#10b981] animate-pulse" />
            <span className="text-[#10b981] font-bold">[STATUS: ACTIVE]</span>
            <span className="text-[#666666]">|</span>
            <span className="text-[#d4d4d8]">BTP v2.2 ENGINE</span>
          </div>
        </div>

        {/* Monospace Desktop Nav Links */}
        <nav className="hidden md:flex items-center gap-7 text-xs sm:text-sm font-mono font-semibold text-[#c4c4cc]">
          <a href="#how-it-works" className="hover:text-[#ffffff] transition">
            [HOW IT WORKS]
          </a>
          <a href="#threat-simulator" className="hover:text-[#ffffff] transition">
            [THREAT DEMOS]
          </a>
          <a href="#policy-editor" className="hover:text-[#ffffff] transition">
            [RULE BUILDER]
          </a>
          <a href="#sdk" className="hover:text-[#ffffff] transition">
            [SDKS &amp; API]
          </a>
        </nav>

        {/* Action Buttons */}
        <div className="hidden sm:flex items-center gap-3">
          <a
            href="https://github.com/ivegotahunnitonit/bartholomew"
            target="_blank"
            rel="noopener noreferrer"
            className="px-3.5 py-1.5 text-xs sm:text-sm font-mono font-semibold bg-[#0a0a0a] border border-[#2a2a2a] text-[#e4e4e7] hover:text-[#ffffff] hover:border-[#555555] transition flex items-center gap-1.5"
          >
            <Code2 size={14} />
            <span>GITHUB</span>
            <ExternalLink size={12} className="text-[#9ca3af]" />
          </a>
          <a
            href="#download"
            className="px-4 py-1.5 text-xs sm:text-sm font-mono font-bold bg-[#f59e0b] hover:bg-[#d97706] text-[#000000] border border-[#f59e0b] transition flex items-center gap-1.5 shadow-sm"
          >
            <Download size={14} />
            <span>GET STARTED (FREE)</span>
          </a>
        </div>

        {/* Mobile Hamburger */}
        <button
          className="md:hidden p-2 text-[#c4c4cc] hover:text-[#ffffff]"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle menu"
        >
          {mobileOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="md:hidden bg-[#000000] border-b border-[#2a2a2a] px-5 py-5 space-y-4">
          <div className="flex items-center gap-2 px-3 py-1 bg-[#0a0a0a] border border-[#2a2a2a] text-xs font-mono mb-2">
            <span className="w-2 h-2 bg-[#10b981] animate-pulse" />
            <span className="text-[#10b981] font-bold">[STATUS: ACTIVE]</span>
            <span className="text-[#d4d4d8]">BTP v2.2 ENGINE</span>
          </div>
          <a
            href="#how-it-works"
            onClick={() => setMobileOpen(false)}
            className="block text-sm font-mono text-[#e4e4e7] hover:text-[#ffffff]"
          >
            [HOW IT WORKS]
          </a>
          <a
            href="#threat-simulator"
            onClick={() => setMobileOpen(false)}
            className="block text-sm font-mono text-[#e4e4e7] hover:text-[#ffffff]"
          >
            [THREAT DEMOS]
          </a>
          <a
            href="#policy-editor"
            onClick={() => setMobileOpen(false)}
            className="block text-sm font-mono text-[#e4e4e7] hover:text-[#ffffff]"
          >
            [RULE BUILDER]
          </a>
          <a
            href="#sdk"
            onClick={() => setMobileOpen(false)}
            className="block text-sm font-mono text-[#e4e4e7] hover:text-[#ffffff]"
          >
            [SDKS &amp; API]
          </a>
          <div className="pt-3 border-t border-[#2a2a2a] flex flex-col gap-2.5">
            <a
              href="#download"
              onClick={() => setMobileOpen(false)}
              className="w-full py-2.5 text-xs sm:text-sm font-mono font-bold bg-[#f59e0b] text-[#000000] text-center flex items-center justify-center gap-1.5"
            >
              <Download size={14} />
              <span>GET STARTED (FREE)</span>
            </a>
            <a
              href="https://github.com/ivegotahunnitonit/bartholomew"
              target="_blank"
              rel="noopener noreferrer"
              className="w-full py-2.5 text-xs sm:text-sm font-mono font-semibold bg-[#0a0a0a] border border-[#2a2a2a] text-[#e4e4e7] text-center flex items-center justify-center gap-1.5"
            >
              <Code2 size={14} />
              <span>GITHUB</span>
              <ExternalLink size={12} className="text-[#9ca3af]" />
            </a>
          </div>
        </div>
      )}
    </header>
  )
}
