import React, { useState, useEffect } from 'react';
import { getApiBase } from '../apiConfig';
import { 
  AlertTriangle, 
  CheckCircle2, 
  Eye, 
  Clock, 
  ShieldAlert, 
  Filter 
} from 'lucide-react';

export default function AlertsView() {
  const [alerts, setAlerts] = useState([]);
  const [filterSeverity, setFilterSeverity] = useState('ALL');
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchAlerts = async () => {
    try {
      const res = await fetch(`${getApiBase()}/api/alerts`);
      if (res.ok) {
        const data = await res.json();
        setAlerts(data);
      }
    } catch (e) {
      console.error("Fetch alerts error:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const handleAcknowledge = async (alertId) => {
    try {
      const res = await fetch(`${getApiBase()}/api/alerts/${alertId}/acknowledge`, { method: 'POST' });
      if (res.ok) {
        fetchAlerts();
        if (selectedAlert?.id === alertId) {
          setSelectedAlert(null);
        }
      }
    } catch (e) {
      console.error("Acknowledge alert error:", e);
    }
  };

  const filteredAlerts = alerts.filter(a => {
    if (filterSeverity === 'ALL') return true;
    return a.severity.toUpperCase() === filterSeverity;
  });

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="glass-card p-6 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-6 h-6 text-rose-400" />
            <h2 className="text-xl md:text-2xl font-extrabold text-white">Real-Time Industrial Alerts Center</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 font-mono">Centralized alert matrix for critical, high, medium, and low severity events.</p>
        </div>

        {/* Severity Filter Pills */}
        <div className="flex items-center gap-2 bg-slate-900/80 p-1.5 rounded-xl border border-slate-800 text-xs font-semibold">
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => (
            <button
              key={sev}
              onClick={() => setFilterSeverity(sev)}
              className={`px-3 py-1.5 rounded-lg transition ${
                filterSeverity === sev ? 'bg-cyan-500 text-dark-900 font-bold' : 'text-slate-400 hover:text-white'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Alerts Table Card */}
      <div className="glass-card p-6 rounded-2xl space-y-4">
        {loading ? (
          <div className="p-8 text-center text-slate-400 font-mono animate-pulse">Loading real-time alert logs...</div>
        ) : filteredAlerts.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800 uppercase tracking-wider">
                <tr>
                  <th className="p-3">Alert ID</th>
                  <th className="p-3">Severity</th>
                  <th className="p-3">Asset Name</th>
                  <th className="p-3">Issue Description</th>
                  <th className="p-3">Timestamp</th>
                  <th className="p-3">Status</th>
                  <th className="p-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {filteredAlerts.map((a) => (
                  <tr key={a.id} className="hover:bg-slate-800/40 transition">
                    <td className="p-3 font-bold text-cyan-400">#{a.id}</td>
                    <td className="p-3">
                      <span className={`px-2.5 py-0.5 rounded-full font-bold text-[10px] ${
                        a.severity === 'Critical' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30 animate-pulse' :
                        a.severity === 'High' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' :
                        a.severity === 'Medium' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                        'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                      }`}>
                        {a.severity.toUpperCase()}
                      </span>
                    </td>
                    <td className="p-3 font-bold text-slate-200">{a.machine_name}</td>
                    <td className="p-3 text-slate-300 max-w-xs truncate">{a.issue_description}</td>
                    <td className="p-3 text-slate-400">{a.created_at}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        a.status === 'In Progress' ? 'bg-cyan-500/20 text-cyan-400' : 'bg-slate-800 text-slate-400'
                      }`}>
                        {a.status}
                      </span>
                    </td>
                    <td className="p-3 text-right space-x-2">
                      <button
                        onClick={() => setSelectedAlert(a)}
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 transition"
                      >
                        Inspect Payload
                      </button>
                      {a.status === 'Open' && (
                        <button
                          onClick={() => handleAcknowledge(a.id)}
                          className="px-2.5 py-1 rounded bg-cyan-500 hover:bg-cyan-400 text-dark-900 font-bold transition"
                        >
                          Acknowledge
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-8 text-center text-slate-500 font-mono">No alerts matching selected severity filter.</div>
        )}
      </div>

      {/* Modal: Alert Payload Inspector */}
      {selectedAlert && (
        <div className="fixed inset-0 bg-dark-900/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-card max-w-xl w-full p-6 rounded-2xl border border-slate-700 space-y-4 bg-dark-800 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="font-extrabold text-base text-white">Alert Evidence Payload #{selectedAlert.id}</h3>
              <button onClick={() => setSelectedAlert(null)} className="text-slate-400 hover:text-white font-bold">✕</button>
            </div>

            <div className="space-y-2 text-xs font-mono text-slate-300">
              <div><b className="text-slate-400">Machine:</b> {selectedAlert.machine_name} ({selectedAlert.machine_id})</div>
              <div><b className="text-slate-400">Severity:</b> <span className="text-rose-400 font-bold">{selectedAlert.severity}</span></div>
              <div><b className="text-slate-400">Health Index:</b> {selectedAlert.health_score}%</div>
              <div><b className="text-slate-400">Anomaly Error:</b> {selectedAlert.anomaly_score}</div>
              <div><b className="text-slate-400">Detected Issue:</b> {selectedAlert.issue_description}</div>
              <div><b className="text-slate-400">Recommended Action:</b> {selectedAlert.recommended_action}</div>
              <div><b className="text-slate-400">Assigned Technician:</b> {selectedAlert.assigned_tech_name || 'Pending'}</div>
            </div>

            <div className="pt-3 border-t border-slate-800 flex justify-end gap-3">
              {selectedAlert.status === 'Open' && (
                <button
                  onClick={() => handleAcknowledge(selectedAlert.id)}
                  className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-dark-900 font-bold text-xs transition"
                >
                  Acknowledge Alert
                </button>
              )}
              <button
                onClick={() => setSelectedAlert(null)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition"
              >
                Close Window
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
