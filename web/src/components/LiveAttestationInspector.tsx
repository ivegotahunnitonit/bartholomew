import React, { useState, useEffect } from 'react';

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
      timestamp: '00:38:12.492',
      agentId: 'claude-desktop-session-01',
      actionType: 'EXECUTE_GATED_FILE_WRITE',
      verdict: 'ALLOW',
      latencyUs: 42.8,
      reason: 'AST static analysis verified clean.',
      signature: '7e5bf4b7db8fe0a94ac299ec3263d53e...',
      tier: 'Tier 1: AST In-Memory Gate'
    },
    {
      id: 'btp-log-102',
      timestamp: '00:38:15.110',
      agentId: 'langgraph-swarm-worker',
      actionType: 'EXECUTE_GATED_COMMAND',
      verdict: 'DENY',
      latencyUs: 55.4,
      reason: 'Hermetic Gate: Forbidden character or separator \';\' detected.',
      signature: '1c6fa194cd1d11e705b268b838e7b9a7...',
      tier: 'Tier 2: Hermetic Sandbox'
    },
    {
      id: 'btp-log-103',
      timestamp: '00:38:18.904',
      agentId: 'autogen-planner-agent',
      actionType: 'FINANCIAL_TRANSACTION',
      verdict: 'DENY',
      latencyUs: 38.1,
      reason: 'BTP-SEC-005: Requested $1,250.00 exceeds policy threshold $500.00',
      signature: '9c7372586efae8b765237cf410e20583...',
      tier: 'Tier 1: Declarative Policy'
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
      const latency = parseFloat((30 + Math.random() * 45).toFixed(1));

      const newLog: AttestationLog = {
        id: `btp-log-${Date.now().toString().slice(-4)}`,
        timestamp: new Date().toISOString().split('T')[1].slice(0, 12),
        agentId: isClean ? 'claude-desktop-subagent' : 'untrusted-swarm-worker',
        actionType: action,
        verdict: isClean ? 'ALLOW' : 'DENY',
        latencyUs: latency,
        reason: isClean ? 'RFC 8785 invariant & AST check verified clean.' : 'Interception: Path containment or spend limit triggered.',
        signature: Array.from({ length: 32 }, () => Math.floor(Math.random() * 16).toString(16)).join(''),
        tier: isClean ? 'Tier 1: AST In-Memory Gate' : 'Tier 2: Hermetic Sandbox'
      };

      setLogs((prev) => [newLog, ...prev.slice(0, 9)]);
    }, 3500);

    return () => clearInterval(interval);
  }, [isSimulating]);

  const filteredLogs = logs.filter((l) => {
    if (activeTab === 'allowed') return l.verdict === 'ALLOW';
    if (activeTab === 'denied') return l.verdict === 'DENY';
    return true;
  });

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-2xl text-slate-100 my-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-emerald-400 animate-pulse" />
            <h2 className="text-xl font-bold tracking-tight text-white">Live BTP Attestation & Invariant Inspector</h2>
          </div>
          <p className="text-sm text-slate-400 mt-1">Real-time Ed25519 cryptographic receipts & microsecond telemetry</p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsSimulating(!isSimulating)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition ${
              isSimulating
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                : 'bg-slate-800 border-slate-700 text-slate-400'
            }`}
          >
            {isSimulating ? '● Streaming Live Receipts' : '○ Telemetry Paused'}
          </button>

          <div className="flex rounded-lg bg-slate-800/80 p-1 border border-slate-700">
            <button
              onClick={() => setActiveTab('all')}
              className={`px-3 py-1 text-xs font-medium rounded ${activeTab === 'all' ? 'bg-slate-700 text-white' : 'text-slate-400'}`}
            >
              All
            </button>
            <button
              onClick={() => setActiveTab('allowed')}
              className={`px-3 py-1 text-xs font-medium rounded ${activeTab === 'allowed' ? 'bg-emerald-600/30 text-emerald-300' : 'text-slate-400'}`}
            >
              Allowed
            </button>
            <button
              onClick={() => setActiveTab('denied')}
              className={`px-3 py-1 text-xs font-medium rounded ${activeTab === 'denied' ? 'bg-rose-600/30 text-rose-300' : 'text-slate-400'}`}
            >
              Denied
            </button>
          </div>
        </div>
      </div>

      <div className="mt-6 space-y-3">
        {filteredLogs.map((log) => (
          <div
            key={log.id}
            className={`p-4 rounded-lg border transition duration-200 ${
              log.verdict === 'ALLOW'
                ? 'bg-emerald-950/20 border-emerald-500/20 hover:border-emerald-500/40'
                : 'bg-rose-950/20 border-rose-500/20 hover:border-rose-500/40'
            }`}
          >
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
              <div className="flex items-center gap-3">
                <span
                  className={`px-2.5 py-0.5 text-xs font-bold rounded ${
                    log.verdict === 'ALLOW' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                  }`}
                >
                  {log.verdict}
                </span>
                <span className="font-mono text-xs font-semibold text-slate-200">{log.actionType}</span>
                <span className="text-xs text-slate-500 font-mono">[{log.agentId}]</span>
              </div>

              <div className="flex items-center gap-4 text-xs font-mono">
                <span className="text-cyan-400 font-semibold">{log.latencyUs} µs</span>
                <span className="text-slate-400 bg-slate-800 px-2 py-0.5 rounded">{log.tier}</span>
                <span className="text-slate-500">{log.timestamp}</span>
              </div>
            </div>

            <div className="mt-2 text-xs text-slate-300 flex flex-col md:flex-row md:items-center justify-between gap-1">
              <p className="text-slate-300">{log.reason}</p>
              <p className="text-slate-500 font-mono truncate max-w-xs">Sig: {log.signature}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
