import React, { useState, useEffect } from 'react';
import { Shield, RefreshCw, FileText, UserCheck, Calendar } from 'lucide-react';

export default function AuditLogView() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchAuditLogs = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v2/audit/logs');
      if (res.ok) {
        const data = await res.json();
        setLogs(data);
      }
    } catch (e) {
      console.error("Fetch audit logs error:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAuditLogs();
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="glass-card p-6 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-3">
            <Shield className="w-6 h-6 text-amber-400" />
            <h2 className="text-xl md:text-2xl font-extrabold text-white">System Audit Log & Security Inspection</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Immutable tracking of user actions, work order transitions, RFP approvals, and system state modifications.
          </p>
        </div>

        <button 
          onClick={fetchAuditLogs}
          className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-slate-700 rounded-xl text-xs font-bold transition flex items-center gap-2"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Refresh Audit Trail
        </button>
      </div>

      {/* Audit Log Table */}
      <div className="glass-card p-6 rounded-2xl space-y-4">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800 uppercase tracking-wider">
              <tr>
                <th className="p-3">Timestamp</th>
                <th className="p-3">User ID</th>
                <th className="p-3">Action Event</th>
                <th className="p-3">Entity Type</th>
                <th className="p-3">Entity ID</th>
                <th className="p-3">State Transition / Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {logs.map((l) => (
                <tr key={l.id} className="hover:bg-slate-800/40 transition">
                  <td className="p-3 font-bold text-cyan-400">{l.timestamp}</td>
                  <td className="p-3 text-slate-200">{l.user_id}</td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 font-bold border border-amber-500/20">
                      {l.action}
                    </span>
                  </td>
                  <td className="p-3 text-indigo-300">{l.entity_type}</td>
                  <td className="p-3 font-bold text-slate-200">{l.entity_id}</td>
                  <td className="p-3 text-slate-400 max-w-sm truncate" title={l.new_state || ""}>
                    {l.new_state || "Executed cleanly."}
                  </td>
                </tr>
              ))}
              {logs.length === 0 && (
                <tr>
                  <td colSpan="6" className="p-8 text-center text-slate-500 font-mono">
                    No system audit logs recorded yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
