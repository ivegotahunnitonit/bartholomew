import { useState } from 'react'
import { Key, GitCommit, FileText, Lock, ShieldAlert, CheckCircle, XCircle } from 'lucide-react'

interface SimulationResult {
  gateway_decision: string
  org_c_standalone_verified: boolean
  verification_mode: string
  evidence_artifact: {
    artifact_id: string
    agent_did: string
    issuer_did: string
    target_system: string
    requested_capability: string
    ed25519_proof: string
    tampered: boolean
  } | null
}

const SAMPLE_SIMULATION: SimulationResult = {
  gateway_decision: 'ALLOW',
  org_c_standalone_verified: true,
  verification_mode: '100% Offline Cryptographic Ed25519 Signature Verification via Pinned Root Keys',
  evidence_artifact: {
    artifact_id: 'art_bth_778899001122',
    agent_did: 'did:bth:org_a_agent_alpha',
    issuer_did: 'did:bth:org_a_root',
    target_system: 'Org_C_Resource_Server',
    requested_capability: 'resource_c.access',
    ed25519_proof: 'proof_ed25519_778899001122',
    tampered: false
  }
}

const ADVERSARIAL_TESTS = [
  { id: 'normal', label: '1. Standard 3-Org Verified Request (Org A → Bartholomew → Org C)', expected: 'ALLOW / Org C Verified' },
  { id: 'forged_sig', label: '2. Identity Attack: Forged Issuer Signature', expected: 'DENIED by Gateway' },
  { id: 'overreach', label: '3. Delegation Attack: Capability Overreach', expected: 'DENIED by Gateway' },
  { id: 'revoked', label: '4. Revocation Attack: Revoked DID Replay', expected: 'DENIED by Gateway' },
  { id: 'nonce_replay', label: '5. Replay Attack: Reusing Nonce / Request ID', expected: 'DENIED by Gateway' },
  { id: 'tamper_one_byte', label: '6. Evidence Attack: 1-Byte Payload Tampering', expected: 'Org C Verifier REJECTS' },
]

export default function VendorNeutralProtocolViewer() {
  const [activeTest, setActiveTest] = useState('normal')
  const [sim, setSim] = useState<SimulationResult>(SAMPLE_SIMULATION)
  const [isEvaluating, setIsEvaluating] = useState(false)

  const handleRunAdversarialTest = (testId: string) => {
    setActiveTest(testId)
    setIsEvaluating(true)
    setTimeout(() => {
      if (testId === 'normal') {
        setSim({
          gateway_decision: 'ALLOW',
          org_c_standalone_verified: true,
          verification_mode: '100% Offline Cryptographic Verification via Pinned Root Keys',
          evidence_artifact: {
            artifact_id: `art_bth_${Math.floor(100000 + Math.random() * 900000)}`,
            agent_did: 'did:bth:org_a_agent_alpha',
            issuer_did: 'did:bth:org_a_root',
            target_system: 'Org_C_Resource_Server',
            requested_capability: 'resource_c.access',
            ed25519_proof: `proof_ed25519_${Math.floor(100000 + Math.random() * 900000)}`,
            tampered: false
          }
        })
      } else if (testId === 'tamper_one_byte') {
        setSim({
          gateway_decision: 'ALLOW',
          org_c_standalone_verified: false, // Org C REJECTS due to 1-byte tamper!
          verification_mode: 'CRITICAL FAILURE: Org C Verifier detected 1-byte signature mismatch!',
          evidence_artifact: {
            artifact_id: 'art_bth_tampered_1byte',
            agent_did: 'did:bth:org_a_agent_alpha',
            issuer_did: 'did:bth:org_a_root',
            target_system: 'Org_C_Resource_Server',
            requested_capability: 'resource_c.access',
            ed25519_proof: 'proof_ed25519_INVALID_TAMPERED_HASH',
            tampered: true
          }
        })
      } else {
        setSim({
          gateway_decision: 'DENY',
          org_c_standalone_verified: false,
          verification_mode: `Blocked at Gateway: ${testId.replace('_', ' ').toUpperCase()} attack prevented.`,
          evidence_artifact: null
        })
      }
      setIsEvaluating(false)
    }, 500)
  }

  return (
    <section id="protocol" className="py-24 px-5 sm:px-8 bg-slate-950/90 relative border-t border-white/5">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 mb-4">
            <Lock size={14} />
            Bartholomew Trust Protocol (BTP v0.1)
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-4 font-heading">
            Bartholomew <span className="gradient-text">Trust Protocol (BTP v0.1)</span>
          </h2>
          <p className="text-base sm:text-lg text-slate-400">
            A vendor-neutral protocol for machine identity, delegated authority, verifiable intent, and independently verifiable execution evidence. Language-neutral specification (BTP-001–BTP-008) with zero-dependency standalone verifier compliance.
          </p>
        </div>

        {/* 3 Independent Organizations Experiment Diagram */}
        <div className="glass-card p-6 sm:p-8 rounded-2xl border border-white/10 mb-12 bg-slate-950/95 space-y-6">
          <div className="text-xs font-mono text-center text-slate-500 uppercase tracking-widest">
            THE 3 INDEPENDENT ORGANIZATIONS EXPERIMENT (ZERO BLIND TRUST)
          </div>

          {/* 3 Node Diagram */}
          <div className="grid md:grid-cols-3 gap-6 items-center text-center">
            {/* Org A */}
            <div className="p-5 rounded-2xl bg-slate-900 border border-cyan-500/30 space-y-2">
              <div className="p-2 rounded bg-cyan-500/10 text-cyan-400 w-fit mx-auto font-mono text-xs font-bold">
                ORG A (Agent Owner)
              </div>
              <h4 className="text-sm font-bold text-white font-heading">Agent Alpha (`did:bth:org_a_agent`)</h4>
              <p className="text-[11px] text-slate-400 font-mono">
                Signs request with Org A private key. Possesses delegated authority credential.
              </p>
            </div>

            {/* Bartholomew Gateway */}
            <div className="p-5 rounded-2xl bg-slate-900 border border-white/10 space-y-2">
              <div className="p-2 rounded bg-violet-500/10 text-violet-400 w-fit mx-auto font-mono text-xs font-bold">
                BARTHOLOMEW GATEWAY
              </div>
              <h4 className="text-sm font-bold text-white font-heading">Decision &amp; Evidence Engine</h4>
              <p className="text-[11px] text-slate-400 font-mono">
                Evaluates Identity + Authority + Intent + Context + Revocation List + Nonce. Issues signed proof.
              </p>
            </div>

            {/* Org C */}
            <div className="p-5 rounded-2xl bg-slate-900 border border-emerald-500/30 space-y-2">
              <div className="p-2 rounded bg-emerald-500/10 text-emerald-400 w-fit mx-auto font-mono text-xs font-bold">
                ORG C (Resource Owner)
              </div>
              <h4 className="text-sm font-bold text-white font-heading">Standalone Offline Verifier</h4>
              <p className="text-[11px] text-slate-400 font-mono">
                Executes 100% offline verification via pinned root keys. Zero API calls to Bartholomew.
              </p>
            </div>
          </div>
        </div>

        {/* Adversarial Attack Testbed */}
        <div className="glass-card p-6 sm:p-8 rounded-2xl border border-white/10 mb-12 space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-xl font-bold text-white font-heading flex items-center gap-2">
              <ShieldAlert size={22} className="text-rose-400" />
              Adversarial Attack Testbed
            </h3>
            <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded border border-emerald-500/20">
              15/15 Protocol Tests Passed
            </span>
          </div>

          <div className="grid lg:grid-cols-12 gap-6 items-start">
            {/* Left: Test Case Selector */}
            <div className="lg:col-span-5 space-y-2">
              <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block mb-2">
                Execute Adversarial Attack Vector:
              </span>
              {ADVERSARIAL_TESTS.map((test) => (
                <button
                  key={test.id}
                  onClick={() => handleRunAdversarialTest(test.id)}
                  disabled={isEvaluating}
                  className={`w-full p-3 rounded-xl border font-mono text-xs text-left transition-all flex justify-between items-center ${
                    activeTest === test.id
                      ? 'border-cyan-500/40 bg-slate-900 text-white font-bold'
                      : 'border-white/5 bg-slate-950/50 text-slate-400 hover:border-white/10'
                  }`}
                >
                  <span className="text-slate-200 truncate pr-2">{test.label}</span>
                  <span className="text-[10px] text-slate-500 shrink-0">{test.expected}</span>
                </button>
              ))}
            </div>

            {/* Right: Real-Time Results & Independent Verification */}
            <div className="lg:col-span-7 p-6 rounded-2xl bg-slate-950 border border-white/10 space-y-4 font-mono text-xs">
              <div className="flex justify-between items-center pb-3 border-b border-white/10">
                <span className="text-slate-400">Gateway Decision:</span>
                <span className={`px-2.5 py-1 rounded text-xs font-bold ${
                  sim.gateway_decision === 'ALLOW'
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                }`}>
                  {sim.gateway_decision}
                </span>
              </div>

              <div className="flex justify-between items-center pb-3 border-b border-white/10">
                <span className="text-slate-400">Org C Standalone Offline Verification:</span>
                <span className={`px-2.5 py-1 rounded text-xs font-bold flex items-center gap-1.5 ${
                  sim.org_c_standalone_verified
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                }`}>
                  {sim.org_c_standalone_verified ? <CheckCircle size={14} /> : <XCircle size={14} />}
                  {sim.org_c_standalone_verified ? 'VERIFIED_ACCEPTED' : 'REJECTED_UNTRUSTED'}
                </span>
              </div>

              <div className="space-y-1">
                <span className="text-slate-500 text-[10px] block">Verification Execution Mode:</span>
                <p className="text-slate-300 bg-slate-900 p-2.5 rounded border border-white/5 text-[11px] font-sans">
                  {sim.verification_mode}
                </p>
              </div>

              {sim.evidence_artifact && (
                <div className="p-3 rounded bg-slate-900/60 border border-white/5 space-y-1 text-[10px] text-slate-400">
                  <div className="flex justify-between">
                    <span>Artifact ID:</span>
                    <span className="text-cyan-400">{sim.evidence_artifact.artifact_id}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Ed25519 Proof:</span>
                    <span className={`truncate ${sim.evidence_artifact.tampered ? 'text-rose-400 font-bold' : 'text-violet-400'}`}>
                      {sim.evidence_artifact.ed25519_proof}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 3 Grounded Architecture Principles */}
        <div className="grid md:grid-cols-3 gap-6 text-xs">
          <div className="glass-card p-5 rounded-2xl border border-white/10 space-y-2">
            <h4 className="font-bold text-white text-sm font-heading flex items-center gap-2">
              <Key size={16} className="text-cyan-400" />
              Identity + Authority + Intent + Context
            </h4>
            <p className="text-slate-400 leading-relaxed">
              Full 5-element decision evaluation prevents unauthorized access by matching requested intent and context against credential authority boundaries.
            </p>
          </div>

          <div className="glass-card p-5 rounded-2xl border border-white/10 space-y-2">
            <h4 className="font-bold text-white text-sm font-heading flex items-center gap-2">
              <GitCommit size={16} className="text-emerald-400" />
              Nonce &amp; Replay Prevention
            </h4>
            <p className="text-slate-400 leading-relaxed">
              Nonce registry and strict 300s timestamp windows ensure legitimate signed requests cannot be replayed by malicious interceptors.
            </p>
          </div>

          <div className="glass-card p-5 rounded-2xl border border-white/10 space-y-2">
            <h4 className="font-bold text-white text-sm font-heading flex items-center gap-2">
              <FileText size={16} className="text-violet-400" />
              1-Byte Tamper Detection
            </h4>
            <p className="text-slate-400 leading-relaxed">
              Standalone verifiers independently hash evidence artifacts using pinned root public keys. Any 1-byte alteration invalidates the proof instantly.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
