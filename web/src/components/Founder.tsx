import { ExternalLink, Code2, Mail, ShieldCheck, FileText, Globe } from 'lucide-react'

export default function Founder() {
  return (
    <section id="founder" className="py-24 px-5 sm:px-8 bg-black text-white border-t border-[#1c1c1c]">
      <div className="max-w-5xl mx-auto">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#0a0a0a] border border-[#222222] text-[#10b981] text-xs font-mono font-bold uppercase tracking-wider mb-3">
            <ShieldCheck size={13} />
            <span>[ OPERATIONAL TRANSPARENCY & CORE LEADERSHIP ]</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white font-sans">
            Founder &amp; Engineering Leadership
          </h2>
          <p className="mt-3 text-[#a1a1aa] text-sm sm:text-base font-sans">
            Bartholomew is an independently built, sovereign security architecture backed by verifiable academic prior art and open cryptographic standards.
          </p>
        </div>

        {/* Founder Card */}
        <div
          className="rounded-xl p-8 md:p-10 bg-[#0a0a0a] border border-[#222222] shadow-2xl relative overflow-hidden flex flex-col md:flex-row items-center md:items-start gap-8"
        >
          {/* Avatar with fallback */}
          <div className="shrink-0">
            <div className="relative inline-block">
              <img
                src="/founder_avatar.jpg"
                alt="Itsub Alemayehu - Founder & Lead Architect"
                className="w-32 h-32 rounded-full object-cover border-2 border-[#10b981] shadow-[0_0_25px_rgba(16,185,129,0.25)] cursor-pointer"
                onClick={() => window.open('/founder_avatar.jpg', '_blank')}
                onError={(e) => {
                  const img = e.target as HTMLImageElement
                  img.onerror = null
                  img.src = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='128' height='128' viewBox='0 0 24 24' fill='none' stroke='%2310b981' stroke-width='1.5'%3E%3Ccircle cx='12' cy='8' r='5'/%3E%3Cpath d='M20 21a8 8 0 0 0-16 0'/%3E%3C/svg%3E`
                }}
              />
              <span className="absolute bottom-1 right-1 w-4 h-4 bg-[#10b981] border-2 border-black rounded-full" title="Active Core Engineer" />
            </div>
          </div>

          {/* Details & Third Party Links */}
          <div className="flex-1 text-center md:text-left space-y-4">
            <div>
              <div className="flex flex-wrap items-center justify-center md:justify-start gap-2.5 mb-1">
                <h3 className="text-2xl font-bold text-white font-sans">Itsub Alemayehu</h3>
                <span className="px-2 py-0.5 bg-[#10b981]/10 text-[#10b981] border border-[#10b981]/30 font-mono text-[11px] font-bold">
                  FOUNDER &amp; LEAD ARCHITECT
                </span>
              </div>
              <p className="text-xs font-mono text-[#f59e0b]">
                Autonomous Systems Laboratory &bull; Bartholomew Project Lead
              </p>
            </div>

            <p className="text-sm text-[#d4d4d8] leading-relaxed font-sans">
              "As autonomous AI agents shift from passive conversational chatbots into active corporate workers with direct shell, database, and financial API authority, prompt guidelines and post-hoc filters are no longer enough. We architected the Bartholomew Trust Protocol (BTP v2.4) as an uncompromising, transactional in-memory safety proxy—giving enterprise teams the confidence to deploy fully autonomous systems with sub-5µs rollbacks, strict mathematical invariants, and tamper-proof digital accountability."
            </p>

            <div className="pt-2 border-t border-[#1c1c1c] grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono">
              <div className="flex items-center gap-2 text-[#a1a1aa]">
                <Globe size={13} className="text-[#38bdf8]" />
                <span>Domain: <a href="https://bartholomew.info" className="text-white hover:underline">bartholomew.info</a></span>
              </div>
              <div className="flex items-center gap-2 text-[#a1a1aa]">
                <Mail size={13} className="text-[#f59e0b]" />
                <span>Contact: <a href="mailto:itsub@bartholomew.info" className="text-white hover:underline">itsub@bartholomew.info</a></span>
              </div>
            </div>

            {/* Verifiable Third-Party Public Links (Google Compliance Criteria 3) */}
            <div className="pt-3 flex flex-wrap gap-2.5 justify-center md:justify-start">
              <a
                href="https://github.com/ivegotahunnitonit"
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1.5 bg-[#000000] border border-[#222222] text-xs font-mono text-[#d4d4d8] hover:text-white hover:border-[#444444] transition inline-flex items-center gap-1.5"
              >
                <Code2 size={13} className="text-[#10b981]" />
                <span>GitHub Profile</span>
                <ExternalLink size={10} className="text-[#71717a]" />
              </a>

              <a
                href="https://doi.org/10.5281/zenodo.22076536"
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1.5 bg-[#000000] border border-[#222222] text-xs font-mono text-[#d4d4d8] hover:text-white hover:border-[#444444] transition inline-flex items-center gap-1.5"
              >
                <FileText size={13} className="text-[#f59e0b]" />
                <span>Zenodo Academic DOI</span>
                <ExternalLink size={10} className="text-[#71717a]" />
              </a>

              <a
                href="/dashboard/admin.html"
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1.5 bg-[#f59e0b] text-black font-bold text-xs font-mono transition inline-flex items-center gap-1.5 hover:bg-[#d97706]"
              >
                <ShieldCheck size={13} />
                <span>Live Admin Command Center</span>
              </a>
            </div>

          </div>
        </div>

      </div>
    </section>
  )
}

