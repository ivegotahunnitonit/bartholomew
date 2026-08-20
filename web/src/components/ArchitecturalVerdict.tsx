export default function ArchitecturalVerdict() {
  return (
    <section className="py-12 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto">
      <div 
        className="relative overflow-hidden rounded-2xl p-8 sm:p-12 text-center"
        style={{
          background: 'linear-gradient(135deg, rgba(10,16,34,0.95), rgba(4,8,19,0.98))',
          border: '1px solid rgba(0,242,254,0.25)',
          boxShadow: '0 0 50px rgba(0,242,254,0.08)'
        }}
      >
        <div 
          className="absolute top-0 left-1/2 -translate-x-1/2 w-96 h-48 pointer-events-none"
          style={{
            background: 'radial-gradient(circle, rgba(0,242,254,0.12), transparent 70%)',
            filter: 'blur(40px)'
          }}
        />
        
        <div className="text-xs font-mono font-bold tracking-widest text-cyan-400 uppercase mb-2">
          THE ARCHITECTURAL VERDICT
        </div>
        <h2 className="text-2xl sm:text-3xl font-extrabold text-white mb-8 tracking-tight font-sans">
          Zero Fluff. The Honest Reality.
        </h2>

        <div className="max-w-2xl mx-auto space-y-4 text-left">
          {/* Item 01 */}
          <div className="flex items-start gap-4 p-5 rounded-xl bg-white/[0.03] border border-white/10">
            <span className="font-mono font-bold text-xs text-slate-400 bg-white/5 px-2.5 py-1 rounded shrink-0">
              01
            </span>
            <div>
              <div className="text-sm font-bold text-slate-200 mb-1">
                If you're running a toy script with no write permissions...
              </div>
              <p className="text-sm text-slate-400 leading-relaxed m-0">
                You don't need Bartholomew. Standard API wrappers and basic try/catch blocks are fine.
              </p>
            </div>
          </div>

          {/* Item 02 */}
          <div 
            className="flex items-start gap-4 p-5 rounded-xl border"
            style={{
              background: 'linear-gradient(135deg, rgba(0,242,254,0.08), rgba(79,172,254,0.04))',
              borderColor: 'rgba(0,242,254,0.3)',
              boxShadow: '0 0 20px rgba(0,242,254,0.08)'
            }}
          >
            <span className="font-mono font-bold text-xs text-cyan-400 bg-cyan-400/15 px-2.5 py-1 rounded shrink-0">
              02
            </span>
            <div>
              <div className="text-sm font-bold text-white mb-1">
                If you're running an agent with database write access, API credentials, or financial spend authority...
              </div>
              <p className="text-sm text-slate-300 leading-relaxed m-0">
                You either use a standardized, sub-millisecond cryptographic verification layer like <strong className="text-cyan-400">Bartholomew</strong>, or you write and maintain your own from scratch. <strong className="text-white">There is no third option.</strong>
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
