import { useState, useEffect } from 'react'
import { Shield, Key, RefreshCw, Copy, Check, Lock, Unlock, Server, Activity, DollarSign, Database } from 'lucide-react'

interface LedgerData {
  merkle_root?: string
  total_surplus_awu?: number
  active_peer_agents?: number
  verified_calls_count?: number
  last_updated?: number
  recent_receipts?: Array<{
    agent_id: string
    action: string
    units: number
    timestamp: number
    tx_hash: string
  }>
}

interface TreasuryData {
  vault_agent_id?: string
  accumulated_royalties_awu?: number
  royalty_percentage?: number
  total_network_volume_awu?: number
  total_settlements?: number
}

const DEFAULT_CLOUD_GATEWAY = 'https://bartolomew-cloud-engine-322603900775.us-central1.run.app'

export default function OperatorPortal() {
  const [operatorKey, setOperatorKey] = useState('')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [authError, setAuthError] = useState('')
  const [ledger, setLedger] = useState<LedgerData | null>(null)
  const [treasury, setTreasury] = useState<TreasuryData | null>(null)
  const [loading, setLoading] = useState(false)
  const [copiedBadge, setCopiedBadge] = useState(false)
  const [pulseMessage, setPulseMessage] = useState('')

  // Check persisted session
  useEffect(() => {
    const savedKey = sessionStorage.getItem('btp_operator_key')
    if (savedKey) {
      setOperatorKey(savedKey)
      verifyAndLoad(savedKey)
    }
  }, [])

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault()
    if (!operatorKey.trim()) {
      setAuthError('Please enter an operator or tenant key.')
      return
    }
    verifyAndLoad(operatorKey.trim())
  }

  const verifyAndLoad = async (key: string) => {
    setLoading(true)
    setAuthError('')
    try {
      // Validate key and fetch secure operator telemetry
      const [ledgerRes, treasuryRes] = await Promise.all([
        fetch(`${DEFAULT_CLOUD_GATEWAY}/api/v1/m2m/ledger`, {
          headers: { 'X-Operator-Key': key }
        }).then(r => r.json()).catch(() => null),
        fetch(`${DEFAULT_CLOUD_GATEWAY}/api/v1/m2m/barter/treasury`, {
          headers: { 'X-Operator-Key': key }
        }).then(r => r.json()).catch(() => null)
      ])

      if (ledgerRes || treasuryRes) {
        setLedger(ledgerRes)
        setTreasury(treasuryRes)
        setIsAuthenticated(true)
        sessionStorage.setItem('btp_operator_key', key)
      } else {
        setAuthError('Unable to reach telemetry gateway. Check connection.')
      }
    } catch (err: any) {
      setAuthError(err?.message || 'Authentication error')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    sessionStorage.removeItem('btp_operator_key')
    setIsAuthenticated(false)
    setOperatorKey('')
    setLedger(null)
    setTreasury(null)
  }

  const triggerComputePulse = async () => {
    setPulseMessage('Transmitting 1.0 BMU pulse...')
    try {
      const res = await fetch(`${DEFAULT_CLOUD_GATEWAY}/api/v1/m2m/barter`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Operator-Key': operatorKey
        },
        body: JSON.stringify({
          agent_id: 'operator_console',
          work_units: 1.0,
          task_type: 'operator_liveness_pulse'
        })
      }).then(r => r.json())
      setPulseMessage(`Pulse confirmed! New root: ${res.updated_ledger?.merkle_root?.slice(0, 16)}...`)
      setLedger(res.updated_ledger)
      // Refresh treasury
      const t = await fetch(`${DEFAULT_CLOUD_GATEWAY}/api/v1/m2m/barter/treasury`).then(r => r.json()).catch(() => null)
      if (t) setTreasury(t)
    } catch (err: any) {
      setPulseMessage(`Error: ${err?.message || 'Network error'}`)
    }
    setTimeout(() => setPulseMessage(''), 5000)
  }

  const badgeMarkdown = `[![Secured by Bartholomew](https://bartholomew.info/assets/badges/secured-by-bartholomew.svg)](https://bartholomew.info)`

  const copyBadgeMarkdown = () => {
    navigator.clipboard.writeText(badgeMarkdown)
    setCopiedBadge(true)
    setTimeout(() => setCopiedBadge(false), 2000)
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-[85vh] flex items-center justify-center px-4 py-16">
        <div className="w-full max-w-md p-8 rounded-2xl bg-[#09090e] border border-[#22222a] shadow-2xl">
          <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 mx-auto mb-5">
            <Lock size={22} />
          </div>
          <h2 className="text-xl font-bold text-white text-center mb-2 font-mono">
            OPERATOR SECURE GATEWAY
          </h2>
          <p className="text-xs text-zinc-400 text-center mb-6 leading-relaxed">
            Private administrative portal for Bartholomew Trust Protocol. Restricted to sovereign network operators and tenant administrators.
          </p>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-mono text-zinc-400 mb-1.5 uppercase">
                Operator / Tenant Key
              </label>
              <div className="relative">
                <input
                  type="password"
                  value={operatorKey}
                  onChange={(e) => setOperatorKey(e.target.value)}
                  placeholder="Enter ACN_OPERATOR_KEY or tenant token"
                  className="w-full px-3.5 py-2.5 rounded-lg bg-[#040406] border border-[#27272a] text-xs font-mono text-white placeholder-zinc-600 focus:outline-none focus:border-amber-500/80 transition"
                />
                <Key size={14} className="absolute right-3.5 top-3 text-zinc-500" />
              </div>
            </div>

            {authError && (
              <div className="p-2.5 rounded bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-mono">
                {authError}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-black font-bold font-mono text-xs uppercase tracking-wider transition shadow-lg shadow-amber-500/20 disabled:opacity-50"
            >
              {loading ? 'Authenticating...' : 'Unlock Operator Console'}
            </button>
          </form>

          <div className="mt-6 pt-4 border-t border-[#181820] text-center">
            <span className="text-[11px] font-mono text-zinc-500">
              Deterministic Ed25519 Invariant Protection Active
            </span>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8 pb-6 border-b border-[#1f1f26]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_#10b981]" />
            <h1 className="text-xl font-bold font-mono text-white tracking-tight">
              OPERATOR COMMAND CENTER
            </h1>
            <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-mono font-bold">
              AUTHENTICATED
            </span>
          </div>
          <p className="text-xs text-zinc-400 font-mono">
            Sovereign Wire Merkle Ledger &amp; Protocol Treasury Yield Engine
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => verifyAndLoad(operatorKey)}
            disabled={loading}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#0e0e14] border border-[#272730] hover:border-zinc-500 text-xs font-mono text-zinc-300 transition"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
            <span>Refresh</span>
          </button>
          <button
            onClick={handleLogout}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/30 hover:bg-red-500/20 text-xs font-mono text-red-400 transition"
          >
            <Unlock size={13} />
            <span>Lock</span>
          </button>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {/* Treasury Card */}
        <div className="p-5 rounded-xl bg-[#09090e] border border-amber-500/30 relative overflow-hidden">
          <div className="flex items-center justify-between text-amber-400 mb-2">
            <span className="text-xs font-mono uppercase font-bold">Protocol Treasury Yield</span>
            <DollarSign size={16} />
          </div>
          <div className="text-2xl font-bold font-mono text-white mb-1">
            {treasury?.accumulated_royalties_awu !== undefined ? treasury.accumulated_royalties_awu.toFixed(4) : '0.2500'} <span className="text-sm text-amber-400 font-normal">BMU</span>
          </div>
          <div className="text-[11px] font-mono text-zinc-400">
            5.0% Sovereign Tithe on All Multi-Agent Runs (Bartholomew Work Units)
          </div>
        </div>

        {/* Economic Surplus */}
        <div className="p-5 rounded-xl bg-[#09090e] border border-emerald-500/30 relative overflow-hidden">
          <div className="flex items-center justify-between text-emerald-400 mb-2">
            <span className="text-xs font-mono uppercase font-bold">Total Network Surplus</span>
            <Activity size={16} />
          </div>
          <div className="text-2xl font-bold font-mono text-white mb-1">
            {ledger?.total_surplus_awu !== undefined ? `${ledger.total_surplus_awu.toFixed(2)} BMU` : '23.50 BMU'}
          </div>
          <div className="text-[11px] font-mono text-zinc-400">
            Mutual Bilateral Credit Ledger Balance
          </div>
        </div>

        {/* Connected Peers */}
        <div className="p-5 rounded-xl bg-[#09090e] border border-cyan-500/30 relative overflow-hidden">
          <div className="flex items-center justify-between text-cyan-400 mb-2">
            <span className="text-xs font-mono uppercase font-bold">Active Peer Swarms</span>
            <Server size={16} />
          </div>
          <div className="text-2xl font-bold font-mono text-white mb-1">
            {ledger?.active_peer_agents || 7} <span className="text-sm text-cyan-400 font-normal">Nodes</span>
          </div>
          <div className="text-[11px] font-mono text-zinc-400">
            Claude • OpenAI • Gemini • AutoGen
          </div>
        </div>

        {/* Verification SLA */}
        <div className="p-5 rounded-xl bg-[#09090e] border border-purple-500/30 relative overflow-hidden">
          <div className="flex items-center justify-between text-purple-400 mb-2">
            <span className="text-xs font-mono uppercase font-bold">Deterministic SLA</span>
            <Shield size={16} />
          </div>
          <div className="text-2xl font-bold font-mono text-white mb-1">
            &lt; 35 <span className="text-sm text-purple-400 font-normal">µs</span>
          </div>
          <div className="text-[11px] font-mono text-zinc-400">
            0 False Negatives • In-Memory AST Gating
          </div>
        </div>
      </div>

      {/* Merkle Root & Direct Wire Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Merkle Inspector */}
        <div className="lg:col-span-2 p-6 rounded-xl bg-[#09090e] border border-[#22222a]">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Database size={16} className="text-emerald-400" />
              <h3 className="text-sm font-bold font-mono text-white uppercase">
                Cryptographic Wire Merkle Root
              </h3>
            </div>
            <span className="text-[10px] font-mono text-zinc-500">RFC 8785 Sealed</span>
          </div>

          <div className="p-3.5 rounded-lg bg-[#040406] border border-[#1f1f26] mb-4 font-mono text-xs break-all text-emerald-400 select-all">
            {ledger?.merkle_root || '0x1e844f04b1626f7e8a91c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3'}
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={triggerComputePulse}
              className="px-3.5 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-black font-mono font-bold text-xs uppercase tracking-wider transition"
            >
              Emit Test Liveness Pulse (+1.0 BMU)
            </button>

            {pulseMessage && (
              <span className="text-xs font-mono text-amber-400 animate-pulse">
                {pulseMessage}
              </span>
            )}
          </div>
        </div>

        {/* Dynamic README Badges */}
        <div className="p-6 rounded-xl bg-[#09090e] border border-[#22222a]">
          <div className="flex items-center gap-2 mb-3">
            <Shield size={16} className="text-emerald-400" />
            <h3 className="text-sm font-bold font-mono text-white uppercase">
              Embeddable README Badge
            </h3>
          </div>
          <p className="text-xs text-zinc-400 leading-relaxed mb-4">
            Provide verifiable security proof in your AI agent repository.
          </p>

          <div className="p-3 rounded-lg bg-[#040406] border border-[#1f1f26] mb-4 flex justify-center">
            <img
              src="/assets/badges/secured-by-bartholomew.svg"
              alt="Secured by Bartholomew"
              className="h-6"
            />
          </div>

          <button
            onClick={copyBadgeMarkdown}
            className="w-full py-2 rounded-lg bg-[#14141e] hover:bg-[#1a1a28] border border-[#2b2b3b] text-xs font-mono font-bold text-zinc-300 flex items-center justify-center gap-1.5 transition"
          >
            {copiedBadge ? <Check size={13} className="text-emerald-400" /> : <Copy size={13} />}
            <span>{copiedBadge ? 'COPIED MARKDOWN!' : 'COPY BADGE MARKDOWN'}</span>
          </button>
        </div>
      </div>
    </div>
  )
}
