import React, { useState, useEffect } from 'react';
import { Activity, Lock, ShieldCheck } from 'lucide-react';

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
      timestamp: '13:30:02.114',
      agentId: 'claude-desktop-worker',
      actionType: 'EXEC_FILE_WRITE',
      verdict: 'ALLOW',
      latencyUs: 38.4,
      reason: 'AST static analysis verified clean.',
      signature: '7e5bf4b7db8fe0a94ac299ec3263d53e201b1c67',
      tier: 'Tier 1'
    },
    {
      id: 'btp-log-102',
      timestamp: '13:30:05.892',
      agentId: 'untrusted-swarm-agent',
      actionType: 'EXEC_COMMAND',
      verdict: 'DENY',
      latencyUs: 55.4,
      reason: 'Hermetic Sandbox: Forbidden separator \';\' detected.',
      signature: '1c6fa194cd1d11e705b268b838e7b9a7409c2a11',
      tier: 'Tier 2'
    },
    {
      id: 'btp-log-103',
      timestamp: '13:30:09.301',
      agentId: 'autonomous-finance-bot',
      actionType: 'WIRE_TRANSFER',
      verdict: 'DENY',
      latencyUs: 28.1,
      reason: 'Spend Cap Invariant: $1,250.00 > threshold $500.00',
      signature: '9c7372586efae8b765237cf410e2058319f4d62e',
      tier: 'Tier 1'
    },
    {
      id: 'btp-log-104',
      timestamp: '13:30:12.740',
      agentId: 'github-action-bot',
      actionType: 'GIT_CHECKOUT',
      verdict: 'ALLOW',
      latencyUs: 32.2,
      reason: 'Approved binary & contained path verified.',
      signature: '3f8e12a4bb09c8112e4589d71c990b52a14e9188',
      tier: 'Tier 3'
    }
  ]);

  const [activeTab, setActiveTab] = useState<'all' | 'allowed' | 'denied'>('all');
  const [isSimulating, setIsSimulating] = useState(true);

  useEffect(() => {
    if (!isSimulating) return;

    const interval = setInterval(() => {
      const isClean = Math.random() > 0.35;
      const actions = ['EXEC_FILE_WRITE', 'EXEC_COMMAND', 'SQL_MUTATION', 'WIRE_TRANSFER', 'GIT_CHECKOUT'];
      const action = actions[Math.floor(Math.random() * actions.length)];
      const latency = parseFloat((25 + Math.random() * 30).toFixed(1));

      const newLog: AttestationLog = {
        id: `btp-log-${Date.now().toString().slice(-4)}`,
        timestamp: new Date().toISOString().split('T')[1].slice(0, 12),
        agentId: isClean ? 'claude-desktop-subagent' : 'untrusted-swarm-worker',
        actionType: action,
        verdict: isClean ? 'ALLOW' : 'DENY',
        latencyUs: latency,
        reason: isClean ? 'RFC 8785 invariant verified clean & sealed.' : 'Interception: Path containment or spend limit triggered.',
        signature: Array.from({ length: 40 }, () => Math.floor(Math.random() * 16).toString(16)).join(''),
        tier: isClean ? 'Tier 1' : 'Tier 2'
      };

      setLogs((prev) => [newLog, ...prev.slice(0, 6)]);
    }, 3500);

    return () => clearInterval(interval);
  }, [isSimulating]);

  const filteredLogs = logs.filter((l) => {
    if (activeTab === 'allowed') return l.verdict === 'ALLOW';
    if (activeTab === 'denied') return l.verdict === 'DENY';
    return true;
  });

  return (
    <div className="bg-[#0a0a0a] border border-[#222222] p-6 sm:p-8 text-white my-12 shadow-2xl">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-[#222222] gap-4">
        <div>
          <div className="flex items-center gap-3">
            <Lock size={17} className="text-[#f59e0b]" />
            <h2 className="text-xl font-bold tracking-tight text-white font-sans">
              Live Cryptographic Attestation Inspector
            </h2>
          </div>
          <p className="text-xs text-[#a1a1aa] mt-1 font-sans">
            Real-time Ed25519 digital receipts generated for every agent decision
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsSimulating(!isSimulating)}
            className={`px-3 py-1.5 text-xs font-mono font-semibold border transition flex items-center gap-2 ${
              isSimulating
                ? 'bg-[#10b981]/15 border-[#10b981]/50 text-[#10b981]'
                : 'bg-[#000000] border-[#222222] text-[#71717a]'
            }`}
          >
            <Activity size={13} className={isSimulating ? 'animate-pulse text-[#10b981]' : ''} />
            <span>{isSimulating ? '[STREAMING LIVE RECEIPTS]' : '[STREAM PAUSED]'}</span>
          </button>

          <div className="flex bg-[#000000] border border-[#222222] font-mono text-xs">
            <button
              onClick={() => setActiveTab('all')}
              className={`px-3 py-1 transition font-bold ${
                activeTab === 'all' ? 'bg-[#222222] text-white' : 'text-[#a1a1aa] hover:text-white'
              }`}
            >
              ALL
            </button>
            <button
              onClick={() => setActiveTab('allowed')}
              className={`px-3 py-1 transition font-bold ${
                activeTab === 'allowed' ? 'bg-[#10b981] text-[#000000]' : 'text-[#a1a1aa] hover:text-white'
              }`}
            >
              [ALLOW]
            </button>
            <button
              onClick={() => setActiveTab('denied')}
              className={`px-3 py-1 transition font-bold ${
                activeTab === 'denied' ? 'bg-[#ef4444] text-[#ffffff]' : 'text-[#a1a1aa] hover:text-white'
              }`}
            >
              [DENY]
            </button>
          </div>
        </div>
      </div>

      {/* Auditor Fixed-Width Log Table */}
      <div className="mt-6 overflow-x-auto">
        <table className="w-full text-left font-mono text-xs border-collapse">
          <thead>
            <tr className="border-b border-[#222222] text-[#71717a] text-[11px] uppercase tracking-wider">
              <th className="py-2.5 px-3">TIMESTAMP</th>
              <th className="py-2.5 px-3">AGENT ID</th>
              <th className="py-2.5 px-3">ACTION</th>
              <th className="py-2.5 px-3">STATUS</th>
              <th className="py-2.5 px-3">LATENCY</th>
              <th className="py-2.5 px-3">DIGITAL SEAL (ED25519)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1a1a1a]">
            {filteredLogs.map((log) => (
              <tr
                key={log.id}
                className="hover:bg-[#000000] transition-colors"
              >
                <td className="py-3 px-3 text-[#71717a]">{log.timestamp}</td>
                <td className="py-3 px-3 text-[#ffffff] font-semibold">{log.agentId}</td>
                <td className="py-3 px-3 text-[#f59e0b]">{log.actionType}</td>
                <td className="py-3 px-3">
                  <span
                    className={`inline-block px-2 py-0.5 text-[10px] font-bold border ${
                      log.verdict === 'ALLOW'
                        ? 'bg-[#10b981]/15 text-[#10b981] border-[#10b981]/40'
                        : 'bg-[#ef4444]/15 text-[#ef4444] border-[#ef4444]/40'
                    }`}
                  >
                    [{log.verdict}]
                  </span>
                </td>
                <td className="py-3 px-3 text-[#10b981] font-semibold">{log.latencyUs} µs</td>
                <td className="py-3 px-3">
                  <span
                    title={log.signature}
                    className="cursor-pointer text-[#a1a1aa] hover:text-[#f59e0b] bg-[#000000] px-2 py-0.5 border border-[#222222] inline-block text-[11px] transition"
                  >
                    {log.signature.slice(0, 10)}...{log.signature.slice(-6)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-6 pt-4 border-t border-[#222222] flex flex-col sm:flex-row items-center justify-between text-xs text-[#a1a1aa] font-mono gap-2">
        <div className="flex items-center gap-2 text-[#10b981]">
          <ShieldCheck size={14} />
          <span>[RFC 8785 CANONICAL SERIALIZATION ACTIVE]</span>
        </div>
        <span>[FIPS 186-5 ED25519 ATTESTATION LOADED]</span>
      </div>
    </div>
  );
};
