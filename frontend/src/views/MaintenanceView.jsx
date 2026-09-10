import React, { useState, useEffect } from 'react';
import { getApiBase } from '../apiConfig';
import { 
  Wrench, 
  CheckCircle2, 
  Clock, 
  UserCheck, 
  ShieldCheck, 
  Plus 
} from 'lucide-react';

export default function MaintenanceView() {
  const [tickets, setTickets] = useState([]);
  const [technicians, setTechnicians] = useState([]);
  const [showVerifyModal, setShowVerifyModal] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [feedbackNotes, setFeedbackNotes] = useState('Replaced worn bearing housing. Lapped seat faces. Post-repair acoustic check verified normal baseline.');
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [tRes, techRes] = await Promise.all([
        fetch(`${getApiBase()}/api/maintenance/tickets`),
        fetch(`${getApiBase()}/api/technicians`)
      ]);
      if (tRes.ok) setTickets(await tRes.json());
      if (techRes.ok) setTechnicians(await techRes.json());
    } catch (e) {
      console.error("Maintenance fetch error:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleVerifySubmit = async () => {
    if (!selectedTicket) return;
    try {
      const res = await fetch(`${getApiBase()}/api/maintenance/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticket_id: selectedTicket.id,
          feedback: feedbackNotes
        })
      });
      if (res.ok) {
        setShowVerifyModal(false);
        fetchData();
      }
    } catch (e) {
      console.error("Verify ticket error:", e);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="glass-card p-6 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Wrench className="w-6 h-6 text-purple-400" />
            <h2 className="text-xl md:text-2xl font-extrabold text-white">Maintenance Work Orders & Technician Roster</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 font-mono">Manage technician assignments, schedule calendar slots, and perform post-repair acoustic verification.</p>
        </div>
      </div>

      {/* Grid: Tickets List & Technicians Directory */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Work Order Tickets */}
        <div className="lg:col-span-2 glass-card p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-base text-slate-100">Active Work Order Tickets</h3>
            <span className="text-xs font-mono text-cyan-400">{tickets.length} Total Tickets</span>
          </div>

          {loading ? (
            <div className="p-8 text-center text-slate-400 font-mono animate-pulse">Loading work order tickets...</div>
          ) : (
            <div className="space-y-3">
              {tickets.map((t) => (
                <div key={t.id} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-extrabold text-cyan-400">#{t.id}</span>
                      <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full ${
                        t.status === 'Verified' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                        t.status === 'In Progress' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' :
                        'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                      }`}>
                        {t.status.toUpperCase()}
                      </span>
                    </div>

                    <span className="text-[10px] text-slate-400 font-mono">Scheduled: {t.scheduled_date}</span>
                  </div>

                  <div>
                    <h4 className="font-bold text-sm text-slate-200">{t.machine_name} ({t.machine_id})</h4>
                    <p className="text-xs text-slate-400 mt-0.5">{t.issue_description}</p>
                  </div>

                  <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono">
                    <span className="text-slate-400 flex items-center gap-1">
                      <UserCheck className="w-3.5 h-3.5 text-cyan-400" /> Assigned: <b className="text-slate-200">{t.tech_name || 'Unassigned'}</b>
                    </span>

                    {t.status !== 'Verified' && (
                      <button
                        onClick={() => {
                          setSelectedTicket(t);
                          setShowVerifyModal(true);
                        }}
                        className="px-3 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-dark-900 font-bold text-xs transition flex items-center gap-1.5"
                      >
                        <ShieldCheck className="w-3.5 h-3.5" /> Post-Repair Verify
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Technicians Roster */}
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <h3 className="font-bold text-base text-slate-100">Certified Technician Directory</h3>

          <div className="space-y-3">
            {technicians.map((tech) => (
              <div key={tech.id} className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-slate-200">{tech.name}</span>
                  <span className="text-[10px] font-mono text-emerald-400 font-bold px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                    {tech.status}
                  </span>
                </div>
                <div className="text-[11px] text-slate-400">{tech.specialty}</div>
                <div className="text-[10px] text-slate-500 font-mono flex items-center justify-between">
                  <span>{tech.shift}</span>
                  <span>{tech.phone}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Modal: Closed-Loop Post-Repair Acoustic Verification */}
      {showVerifyModal && selectedTicket && (
        <div className="fixed inset-0 bg-dark-900/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-card max-w-lg w-full p-6 rounded-2xl border border-slate-700 space-y-4 bg-dark-800 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="font-extrabold text-base text-white">Closed-Loop Post-Repair Verification #{selectedTicket.id}</h3>
              <button onClick={() => setShowVerifyModal(false)} className="text-slate-400 hover:text-white font-bold">✕</button>
            </div>

            <div className="space-y-3 text-xs text-slate-300">
              <div><b className="text-slate-400">Machine Asset:</b> {selectedTicket.machine_name}</div>
              <div><b className="text-slate-400">Issue:</b> {selectedTicket.issue_description}</div>

              <div>
                <label className="block text-slate-400 font-mono mb-1">Technician Repair Notes & Feedback:</label>
                <textarea
                  value={feedbackNotes}
                  onChange={(e) => setFeedbackNotes(e.target.value)}
                  rows={3}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-xs text-slate-200 font-mono outline-none focus:border-cyan-500"
                />
              </div>

              <div className="p-3 bg-emerald-950/20 border border-emerald-500/30 rounded-xl text-emerald-300 font-mono text-[11px]">
                ℹ️ Confirming verification evaluates a clean sound stream, clears active alerts, and marks the machine state to <b>98.5% Operating Health</b>.
              </div>
            </div>

            <div className="pt-3 border-t border-slate-800 flex justify-end gap-3">
              <button
                onClick={handleVerifySubmit}
                className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-dark-900 font-bold text-xs transition"
              >
                Confirm Acoustic Verification
              </button>
              <button
                onClick={() => setShowVerifyModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
