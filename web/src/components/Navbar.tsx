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
        scrolled 
          ? 'bg-[#08080b]/90 border-b border-[#27272a]/80 backdrop-blur-xl shadow-[0_15px_30px_-15px_rgba(0,0,0,0.8)]' 
          : 'bg-[#040406]/60 backdrop-blur-md border-b border-[#1f1f23]/40'
      }`}
    >
      {/* Top Ambient Glow Line */}
      <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-[#10b981]/40 to-transparent pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo & Box Status Tag */}
        <div className="flex items-center gap-4">
          <Link to="/" className="flex items-center no-underline" aria-label="Bartholomew Home">
            <Logo size={28} showText={true} />
          </Link>
        </div>

        {/* Monospace Desktop Nav Links */}
        <nav className="hidden md:flex items-center gap-6 text-xs font-mono font-semibold text-[#a1a1aa]">
          <a href="#threat-simulator" className="hover:text-[#ffffff] transition hover:text-[#10b981]">
            [SANDBOX]
          </a>
          <a href="#enterprise" className="text-[#10b981] hover:text-[#34d399] transition flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-[#10b981] animate-pulse" />
            <span>[ENTERPRISE PILOT]</span>
          </a>
          <a href="#policy-editor" className="hover:text-[#ffffff] transition hover:text-[#10b981]">
            [POLICY TESTER]
          </a>
          <a href="#founder" className="hover:text-[#ffffff] transition hover:text-[#10b981]">
            [FOUNDER &amp; TEAM]
          </a>
          <a href="#sdk" className="hover:text-[#ffffff] transition hover:text-[#10b981]">
            [SDK / CLI]
          </a>
        </nav>

        {/* Action Buttons */}
        <div className="hidden sm:flex items-center gap-2.5">
          <a
            href="https://www.producthunt.com/products/bartholomew-2"
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-1.5 text-xs font-mono font-bold bg-[#ff6154]/10 border border-[#ff6154]/40 hover:border-[#ff6154] text-[#ff6154] transition flex items-center gap-1.5 rounded-md shadow-sm"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-[#ff6154] animate-pulse" />
            <span>PRODUCT HUNT</span>
          </a>
          <a
            href="https://github.com/ivegotahunnitonit/bartholomew"
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-1.5 text-xs font-mono font-semibold bg-[#111115] border border-[#27272a] text-[#d4d4d8] hover:text-[#ffffff] hover:border-[#10b981]/50 transition flex items-center gap-1.5 rounded-md"
          >
            <Code2 size={13} />
            <span>GITHUB</span>
          </a>
          <a
            href="#download"
            className="px-3.5 py-1.5 text-xs font-mono font-bold bg-[#10b981]/15 hover:bg-[#10b981]/25 text-[#10b981] border border-[#10b981]/40 hover:border-[#10b981] transition flex items-center gap-1.5 rounded-md shadow-[0_0_15px_rgba(16,185,129,0.15)]"
          >
            <Download size={13} />
            <span>INSTALL</span>
          </a>
        </div>

        {/* Mobile Hamburger */}
        <button
          className="md:hidden p-2 text-[#a1a1aa] hover:text-[#ffffff]"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle menu"
        >
          {mobileOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="md:hidden bg-[#000000] border-b border-[#222222] px-5 py-5 space-y-4">
          <div className="flex items-center gap-2 px-2.5 py-1 bg-[#0a0a0a] border border-[#222222] text-xs font-mono mb-2">
            <span className="w-1.5 h-1.5 bg-[#10b981] animate-pulse" />
            <span className="text-[#10b981] font-bold">[STATUS: ACTIVE]</span>
            <span className="text-[#a1a1aa]">BTP v2.2 ENGINE</span>
          </div>
          <a
            href="#how-it-works"
            onClick={() => setMobileOpen(false)}
            className="block text-sm font-mono text-[#d4d4d8] hover:text-[#ffffff]"
          >
            [HOW IT WORKS]
          </a>
          <a
            href="#threat-simulator"
            onClick={() => setMobileOpen(false)}
            className="block text-sm font-mono text-[#d4d4d8] hover:text-[#ffffff]"
          >
            [THREAT DEMOS]
          </a>
          <a
            href="#policy-editor"
            onClick={() => setMobileOpen(false)}
            className="block text-sm font-mono text-[#d4d4d8] hover:text-[#ffffff]"
          >
            [RULE BUILDER]
          </a>
          <a
            href="#sdk"
            onClick={() => setMobileOpen(false)}
            className="block text-sm font-mono text-[#d4d4d8] hover:text-[#ffffff]"
          >
            [SDKS &amp; API]
          </a>
          <div className="pt-3 border-t border-[#222222] flex flex-col gap-2.5">
            <a
              href="#download"
              onClick={() => setMobileOpen(false)}
              className="w-full py-2 text-xs font-mono font-bold bg-[#f59e0b] text-[#000000] text-center flex items-center justify-center gap-1.5"
            >
              <Download size={13} />
              <span>GET STARTED (FREE)</span>
            </a>
            <a
              href="https://github.com/ivegotahunnitonit/bartholomew"
              target="_blank"
              rel="noopener noreferrer"
              className="w-full py-2 text-xs font-mono font-semibold bg-[#0a0a0a] border border-[#222222] text-[#d4d4d8] text-center flex items-center justify-center gap-1.5"
            >
              <Code2 size={13} />
              <span>GITHUB</span>
              <ExternalLink size={11} className="text-[#71717a]" />
            </a>
          </div>
        </div>
      )}
    </header>
  )
}
