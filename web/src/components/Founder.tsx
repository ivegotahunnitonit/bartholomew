import { ArrowRight } from 'lucide-react'

export default function Founder() {
  return (
    <section className="py-24 px-5 sm:px-8">
      <div className="section-divider mb-24" />
      <div className="max-w-4xl mx-auto">
        <div
          className="rounded-2xl p-8 md:p-12 flex flex-col md:flex-row items-center gap-8"
          style={{
            background: 'linear-gradient(135deg, rgba(16,185,129,0.08), rgba(6,182,212,0.06), rgba(139,92,246,0.05))',
            border: '1px solid rgba(56,189,248,0.2)',
          }}
        >
          {/* Avatar */}
          <div className="shrink-0">
            <img
              src="../founder_avatar.jpg"
              alt="Founder"
              className="rounded-full object-cover"
              style={{
                width: '120px',
                height: '120px',
                border: '3px solid rgba(52,211,153,0.4)',
                boxShadow: '0 0 30px rgba(16,185,129,0.25)',
              }}
              onError={e => {
                (e.target as HTMLImageElement).style.display = 'none'
              }}
            />
          </div>

          {/* Text */}
          <div className="flex-1 text-center md:text-left">
            <div className="badge badge-emerald mb-3 inline-flex">Founder Note</div>
            <h2
              className="font-bold text-xl md:text-2xl mb-3 leading-snug"
              style={{ color: '#f1f5f9', fontFamily: '"Plus Jakarta Sans", sans-serif' }}
            >
              "AI agents are executing code, writing emails, and moving money.
              We built the security layer that should have been there from day one."
            </h2>
            <p className="text-sm mb-6" style={{ color: '#94a3b8' }}>
              Bartholomew is independently owned and operated. All engines — ECE, EV Governor, provenance tracking, attestation chain — are proprietary and unencumbered.
            </p>
            <div className="flex flex-wrap gap-3 justify-center md:justify-start">
              <a href="/dashboard/admin.html?tour=1" className="btn-primary" style={{ fontSize: '0.85rem', padding: '0.6rem 1.2rem' }}>
                <ArrowRight size={15} />
                Start the tour
              </a>
              <a
                href="https://github.com/ivegotahunnitonit/bartholomew"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-secondary"
                style={{ fontSize: '0.85rem', padding: '0.6rem 1.2rem' }}
              >
                GitHub
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
