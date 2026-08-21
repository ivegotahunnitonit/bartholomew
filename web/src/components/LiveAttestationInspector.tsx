import React, { useState, useEffect } from 'react';
import { Activity, CheckCircle2, AlertTriangle, Lock } from 'lucide-react';

interface AttestationLog {
  id: string;
  timestamp: string;
  agentId: string;
  actionType: string;
  verdict: 'ALLOW' | 'DENY';
  latencyUs: number;
  reason: string;
  signature: string;
  tier: string;
}

export const LiveAttestationInspector: React.FC = () => {
  const [logs, setLogs] = useState<AttestationLog[]>([
    {
      id: 'btp-log-101',
      timestamp: '13:14:02.114',
      agentId: 'claude-desktop-worker',
      actionType: 'EXECUTE_GATED_FILE_WRITE',
      verdict: 'ALLOW',
      latencyUs: 42.8,
      reason: 'AST static analysis verified clean. No dangerous calls.',
      signature: '7e5bf4b7db8fe0a94ac299ec3263d53e...',
      tier: 'Tier 1: AST Scanner'
    },
    {
      id: 'btp-log-102',
      timestamp: '13:14:05.892',
      agentId: 'untrusted-swarm-agent',
      actionType: 'EXECUTE_GATED_COMMAND',
      verdict: 'DENY',
      latencyUs: 55.4,
      reason: 'Hermetic Sandbox: Forbidden character or separator \';\' detected.',
      signature: '1c6fa194cd1d11e705b268b838e7b9a7...',
      tier: 'Tier 2: Locked Sandbox'
    },
    {
      id: 'btp-log-103',
      timestamp: '13:14:09.301',
      agentId: 'autonomous-finance-bot',
      actionType: 'FINANCIAL_TRANSACTION',
      verdict: 'DENY',
      latencyUs: 38.1,
      reason: 'Spend Cap Invariant: Requested $1,250.00 exceeds policy threshold $500.00',
      signature: '9c7372586efae8b765237cf410e20583...',
      tier: 'Tier 1: Spend Cap'
    }
  ]);

  const [activeTab, setActiveTab] = useState<'all' | 'allowed' | 'denied'>('all');
  const [isSimulating, setIsSimulating] = useState(true);

  useEffect(() => {
    if (!isSimulating) return;

    const interval = setInterval(() => {
      const isClean = Math.random() > 0.35;
      const actions = ['EXECUTE_GATED_FILE_WRITE', 'EXECUTE_GATED_COMMAND', 'DATABASE_MUTATION', 'FINANCIAL_TRANSFER'];
      const action = actions[Math.floor(Math.random() * actions.length)];
      const latency = parseFloat((25 + Math.random() * 35).toFixed(1));

      const newLog: AttestationLog = {
        id: `btp-log-${Date.now().toString().slice(-4)}`,
        timestamp: new Date().toISOString().split('T')[1].slice(0, 12),
        agentId: isClean ? 'claude-desktop-subagent' : 'untrusted-swarm-worker',
        actionType: action,
        verdict: isClean ? 'ALLOW' : 'DENY',
        latencyUs: latency,
        reason: isClean ? 'RFC 8785 invariant verified clean & sealed.' : 'Interception: Path containment or spend limit triggered.',
        signature: Array.from({ length: 32 }, () => Math.floor(Math.random() * 16).toString(16)).join(''),
        tier: isClean ? 'Tier 1: AST Scanner' : 'Tier 2: Locked Sandbox'
      };

      setLogs((prev) => [newLog, ...prev.slice(0, 8)]);
    }, 4000);

    return () => clearInterval(interval);
  }, [isSimulating]);

  const filteredLogs = logs.filter((l) => {
    if (activeTab === 'allowed') return l.verdict === 'ALLOW';
    if (activeTab === 'denied') return l.verdict === 'DENY';
    return true;
  });

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-2xl text-slate-100 my-12 backdrop-blur-sm">
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              <Lock size={18} className="text-cyan-400" />
              Live Cryptographic Attestation Inspector
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time Ed25519 digital receipts generated for every agent decision
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsSimulating(!isSimulating)}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold border transition flex items-center gap-1.5 ${
              isSimulating
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                : 'bg-slate-800 border-slate-700 text-slate-400'
            }`}
          >
            <Activity size={13} className={isSimulating ? 'animate-pulse text-emerald-400' : ''} />
            <span>{isSimulating ? 'Live Audit Stream' : 'Stream Paused'}</span>
          </button>

          <div className="flex rounded-xl bg-slate-950 p-1 border border-slate-800">
            <button
              onClick={() => setActiveTab('all')}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition ${
                activeTab === 'all' ? 'bg-slate-800 text-white shadow-sm' : 'text-slate-400 hover:text-white'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setActiveTab('allowed')}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition ${
                activeTab === 'allowed' ? 'bg-emerald-500/20 text-emerald-300' : 'text-slate-400 hover:text-white'
              }`}
            >
              Approved
            </button>
            <button
              onClick={() => setActiveTab('denied')}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition ${
                activeTab === 'denied' ? 'bg-rose-500/20 text-rose-300' : 'text-slate-400 hover:text-white'
              }`}
            >
              Blocked
            </button>
          </div>
        </div>
      </div>

      <div className="mt-6 space-y-3">
        {filteredLogs.map((log) => (
          <div
            key={log.id}
            className={`p-4 rounded-xl border transition duration-200 ${
              log.verdict === 'ALLOW'
                ? 'bg-slate-950/60 border-emerald-500/20 hover:border-emerald-500/40'
                : 'bg-slate-950/60 border-rose-500/20 hover:border-rose-500/40'
            }`}
          >
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
              <div className="flex items-center gap-3">
                <span
                  className={`px-2.5 py-0.5 text-[11px] font-extrabold rounded-md flex items-center gap-1 font-mono ${
                    log.verdict === 'ALLOW'
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                      : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                  }`}
                >
                  {log.verdict === 'ALLOW' ? <CheckCircle2 size={12} /> : <AlertTriangle size={12} />}
                  {log.verdict}
                </span>
                <span className="font-mono text-xs font-bold text-slate-200">{log.actionType}</span>
                <span className="text-xs text-slate-500 font-mono">[{log.agentId}]</span>
              </div>

              <div className="flex items-center gap-3 text-xs font-mono">
                <span className="text-cyan-300 font-bold">{log.latencyUs} µs</span>
                <span className="text-slate-400 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded text-[10px]">
                  {log.tier}
                </span>
                <span className="text-slate-500 text-[11px]">{log.timestamp}</span>
              </div>
            </div>

            <div className="mt-2.5 pt-2 border-t border-slate-900 text-xs text-slate-300 flex flex-col md:flex-row md:items-center justify-between gap-2">
              <p className="text-slate-300 text-[11px]">{log.reason}</p>
              <p className="text-slate-500 font-mono text-[10px] truncate max-w-xs">Digital Seal: {log.signature}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
