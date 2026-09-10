import React, { useState, useEffect } from 'react';
import { getApiBase } from '../apiConfig';
import { 
  Cpu, 
  MapPin, 
  Clock, 
  Calendar, 
  Wrench, 
  Activity, 
  Layers, 
  FileText, 
  Play 
} from 'lucide-react';

export default function MachineDetailView({ selectedMachineId, onSelectMachine }) {
  const [machineData, setMachineData] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${getApiBase()}/api/machines/${selectedMachineId}`);
        if (res.ok) {
          const data = await res.json();
          setMachineData(data);
        }
        
        const analyzeRes = await fetch(`${getApiBase()}/api/machines/${selectedMachineId}/analyze`);
        if (analyzeRes.ok) {
          const aData = await analyzeRes.json();
          setAnalysisData(aData);
        }
      } catch (e) {
        console.error("Machine detail error:", e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [selectedMachineId]);

  if (loading) {
    return (
      <div className="p-8 text-center text-slate-400 font-mono animate-pulse">
        Fetching detailed machine diagnostic telemetry...
      </div>
    );
  }

  const m = machineData?.machine;
  const components = machineData?.components || [];
  const history = machineData?.history || [];
  const mfr = machineData?.manufacturer;

  return (
    <div className="space-y-6">
      {/* Top Banner Card */}
      <div className="glass-card p-6 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 flex items-center justify-center font-extrabold text-lg">
            {m?.id?.substring(0, 3)}
          </div>
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-xl font-extrabold text-white">{m?.name}</h2>
              <span className="font-mono text-xs font-bold text-cyan-400 bg-cyan-500/10 px-2.5 py-0.5 rounded-md border border-cyan-500/20">
                {m?.id}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1 flex items-center gap-3 font-mono">
              <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5 text-slate-500" /> {m?.location}</span>
              <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5 text-slate-500" /> {m?.operating_hours} Hours</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-[10px] text-slate-400 font-mono uppercase">Machine Health Score</div>
            <div className={`text-2xl font-extrabold ${m?.health_score >= 85 ? 'text-emerald-400' : 'text-amber-400'}`}>
              {m?.health_score}%
            </div>
          </div>
        </div>
      </div>

      {/* Grid: Component Breakdown & Spectrogram Canvas */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Component Breakdown List */}
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <h3 className="font-bold text-base text-slate-100 flex items-center gap-2">
            <Layers className="w-5 h-5 text-cyan-400" /> Component Breakdown
          </h3>

          <div className="space-y-3">
            {components.map((c) => (
              <div key={c.id} className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-slate-200">{c.name}</span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    c.health_score >= 90 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'
                  }`}>
                    {c.health_score}%
                  </span>
                </div>
                <div className="text-[11px] text-slate-400 font-mono">
                  Recommended Part: <span className="text-cyan-400 font-bold">{c.recommended_part_no}</span>
                </div>
                <div className="text-[10px] text-slate-500 font-mono">
                  Service Interval: {c.service_interval_hours} operating hours
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Spectrogram & Acoustic Frequency Canvas */}
        <div className="lg:col-span-2 glass-card p-6 rounded-2xl space-y-4">
          <h3 className="font-bold text-base text-slate-100 flex items-center gap-2">
            <Activity className="w-5 h-5 text-indigo-400" /> Log-Mel Spectrogram Acoustic Representation (128 Bins)
          </h3>

          {analysisData?.log_mel_sample ? (
            <div className="p-4 bg-dark-900 rounded-xl border border-slate-800 space-y-2">
              <div className="text-xs text-slate-400 font-mono flex items-center justify-between">
                <span>Sample Matrix: 128 Mel Bands x 309 Temporal Frames</span>
                <span className="text-cyan-400 font-bold">FFT Window: 1024 / Hop: 512</span>
              </div>
              <div className="h-44 w-full bg-gradient-to-r from-indigo-950 via-purple-900 to-rose-950 rounded-lg border border-purple-500/20 flex items-center justify-center text-xs font-mono text-purple-300 shadow-inner">
                [ Log-Mel Spectrogram Density Matrix Display Canvas ]
              </div>
            </div>
          ) : (
            <div className="p-8 text-center text-slate-500 font-mono">Spectrogram feature matrix loading...</div>
          )}

          {/* Diagnostic Agent Output */}
          {analysisData?.agent_res && (
            <div className="p-4 rounded-xl bg-cyan-950/20 border border-cyan-500/30 text-xs font-mono text-cyan-200 space-y-1">
              <div className="font-bold text-cyan-400">🤖 AI DIAGNOSTIC FINDINGS:</div>
              <div>Issue: {analysisData.agent_res.diagnostic.detected_issue}</div>
              <div>Affected Component: {analysisData.agent_res.diagnostic.faulty_component}</div>
            </div>
          )}
        </div>
      </div>

      {/* Maintenance History Table */}
      <div className="glass-card p-6 rounded-2xl space-y-4">
        <h3 className="font-bold text-base text-slate-100 flex items-center gap-2">
          <FileText className="w-5 h-5 text-emerald-400" /> Historical Maintenance Audit Log
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800 uppercase tracking-wider">
              <tr>
                <th className="p-3">Date</th>
                <th className="p-3">Component</th>
                <th className="p-3">Service Type</th>
                <th className="p-3">Technician</th>
                <th className="p-3">Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {history.map((h, i) => (
                <tr key={i} className="hover:bg-slate-800/40 transition">
                  <td className="p-3 font-bold text-cyan-400">{h.service_date}</td>
                  <td className="p-3 text-slate-200">{h.component_name}</td>
                  <td className="p-3"><span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-semibold">{h.service_type}</span></td>
                  <td className="p-3 text-emerald-400">{h.technician_name}</td>
                  <td className="p-3 text-slate-400">{h.notes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
