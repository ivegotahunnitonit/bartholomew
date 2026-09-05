import { useState, useEffect } from 'react'
import { Download, Menu, X, ShoppingBag } from 'lucide-react'
import { Link } from 'react-router-dom'
import Logo from './Logo'
import { BTP_ENGINE_LABEL } from '../constants/version'

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

        {/* Action Logo Buttons (Tailored Product Hunt, GitHub, and Install) */}
        <div className="hidden sm:flex items-center gap-2">
          {/* Product Hunt Official Mark */}
          <a
            href="https://www.producthunt.com/products/bartholomew-2"
            target="_blank"
            rel="noopener noreferrer"
            title="Product Hunt — Join Launch Discussion"
            aria-label="Product Hunt"
            className="w-9 h-9 flex items-center justify-center rounded-lg bg-[#ff6154]/10 border border-[#ff6154]/30 hover:border-[#ff6154] text-[#ff6154] hover:bg-[#ff6154]/20 transition-all shadow-sm hover:shadow-[0_0_14px_rgba(255,97,84,0.35)] group relative"
          >
            <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-[#ff6154] animate-pulse shadow-[0_0_6px_#ff6154]" />
            <svg className="w-4 h-4 transition-transform group-hover:scale-110" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="12" fill="#ff6154" />
              <path d="M13.6 13.2h-2.8V8.4h2.8c1.325 0 2.4 1.075 2.4 2.4s-1.075 2.4-2.4 2.4zm0-6.8H8.8v11.2h2v-2.4h2.8c2.43 0 4.4-1.97 4.4-4.4s-1.97-4.4-4.4-4.4z" fill="#ffffff" />
            </svg>
          </a>

          {/* GitHub Official Mark */}
          <a
            href="https://github.com/ivegotahunnitonit/bartholomew"
            target="_blank"
            rel="noopener noreferrer"
            title="GitHub — Source Code & Releases"
            aria-label="GitHub"
            className="w-9 h-9 flex items-center justify-center rounded-lg bg-[#111115] border border-[#27272a] hover:border-[#10b981]/60 text-[#d4d4d8] hover:text-white hover:bg-[#181820] transition-all shadow-sm hover:shadow-[0_0_14px_rgba(16,185,129,0.25)] group"
          >
            <svg className="w-4 h-4 transition-transform group-hover:scale-110" viewBox="0 0 24 24" fill="currentColor">
              <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
            </svg>
          </a>

          {/* Install Logo Button */}
          <a
            href="#download"
            title="Install Bartholomew CLI & SDK"
            aria-label="Install Bartholomew"
            className="w-9 h-9 flex items-center justify-center rounded-lg bg-[#10b981]/15 hover:bg-[#10b981]/25 text-[#10b981] border border-[#10b981]/40 hover:border-[#10b981] transition-all shadow-[0_0_15px_rgba(16,185,129,0.15)] hover:shadow-[0_0_20px_rgba(16,185,129,0.35)] group"
          >
            <Download size={16} className="transition-transform group-hover:scale-110 group-hover:translate-y-0.5" />
          </a>

          {/* Storefront / Shop Icon Button */}
          <a
            href="/store/"
            title="Bartholomew Defense Storefront & Licenses"
            aria-label="Defense Storefront"
            className="w-9 h-9 flex items-center justify-center rounded-lg bg-[#38bdf8]/10 hover:bg-[#38bdf8]/20 text-[#38bdf8] border border-[#38bdf8]/30 hover:border-[#38bdf8] transition-all shadow-sm hover:shadow-[0_0_14px_rgba(56,189,248,0.35)] group"
          >
            <ShoppingBag size={16} className="transition-transform group-hover:scale-110" />
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
            <span className="text-[#a1a1aa]">{BTP_ENGINE_LABEL}</span>
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
          <a
            href="/store/"
            onClick={() => setMobileOpen(false)}
            className="flex items-center gap-2 text-sm font-mono text-[#38bdf8] hover:text-[#ffffff] transition"
          >
            <ShoppingBag size={14} />
            <span>[STORE &amp; LICENSES]</span>
          </a>
          <div className="pt-3 border-t border-[#222222] flex flex-col gap-2.5">
            <a
              href="#download"
              onClick={() => setMobileOpen(false)}
              className="w-full py-2.5 text-xs font-mono font-bold bg-[#10b981]/15 border border-[#10b981]/40 text-[#10b981] text-center flex items-center justify-center gap-2 rounded-lg shadow-[0_0_12px_rgba(16,185,129,0.15)]"
            >
              <Download size={14} />
              <span>INSTALL BTP RUNTIME</span>
            </a>
            <div className="grid grid-cols-2 gap-2">
              <a
                href="https://www.producthunt.com/products/bartholomew-2"
                target="_blank"
                rel="noopener noreferrer"
                className="py-2.5 text-xs font-mono font-semibold bg-[#ff6154]/10 border border-[#ff6154]/30 text-[#ff6154] text-center flex items-center justify-center gap-2 rounded-lg"
              >
                <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="12" fill="#ff6154" />
                  <path d="M13.6 13.2h-2.8V8.4h2.8c1.325 0 2.4 1.075 2.4 2.4s-1.075 2.4-2.4 2.4zm0-6.8H8.8v11.2h2v-2.4h2.8c2.43 0 4.4-1.97 4.4-4.4s-1.97-4.4-4.4-4.4z" fill="#ffffff" />
                </svg>
                <span>PRODUCT HUNT</span>
              </a>
              <a
                href="https://github.com/ivegotahunnitonit/bartholomew"
                target="_blank"
                rel="noopener noreferrer"
                className="py-2.5 text-xs font-mono font-semibold bg-[#0a0a0a] border border-[#222222] text-[#d4d4d8] text-center flex items-center justify-center gap-2 rounded-lg"
              >
                <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
                  <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
                </svg>
                <span>GITHUB</span>
              </a>
            </div>
          </div>
        </div>
      )}
    </header>
  )
}
