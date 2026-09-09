import React, { useState, useEffect } from 'react';
import { 
  Radio, 
  Wifi, 
  WifiOff, 
  Volume2, 
  AlertOctagon, 
  ShieldCheck, 
  Clock, 
  Layers, 
  Wrench, 
  Send 
} from 'lucide-react';

export default function LiveMonitoringView({ selectedMachine, onSelectMachine, wsConnected }) {
  const [telemetryState, setTelemetryState] = useState(null);
  const [activeTabPayload, setActiveTabPayload] = useState('telegram');
  const [telemetryHistory, setTelemetryHistory] = useState([]);
  const [isStreaming, setIsStreaming] = useState(true);
  const [availableClips, setAvailableClips] = useState([]);
  const [selectedClip, setSelectedClip] = useState('auto');

  // Fetch clip options for selected machine
  useEffect(() => {
    const fetchClips = async () => {
      try {
        const res = await fetch(`/api/machines/${selectedMachine}/clips`);
        if (res.ok) {
          const clips = await res.json();
          setAvailableClips(clips);
        }
      } catch (e) {
        console.error("Fetch clips error:", e);
      }
    };
    fetchClips();
  }, [selectedMachine]);

  // Fetch telemetry analysis and cycle clips
  const fetchAnalysis = async (clipParam = selectedClip) => {
    try {
      const param = clipParam === 'auto' ? 'random' : clipParam;
      const res = await fetch(`/api/machines/${selectedMachine}/analyze?file_name=${encodeURIComponent(param)}`);
      if (res.ok) {
        const data = await res.json();
        setTelemetryState(data);
        setTelemetryHistory(prev => [...prev.slice(-15), data.anomaly_score]);
      }
    } catch (e) {
      console.error("Telemetry fetch error:", e);
    }
  };

  useEffect(() => {
    let interval = null;
    fetchAnalysis(selectedClip);
    if (isStreaming && selectedClip === 'auto') {
      interval = setInterval(() => {
        fetchAnalysis('auto');
      }, 3500);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [selectedMachine, isStreaming, selectedClip]);

  const agentRes = telemetryState?.agent_res;
  const diag = agentRes?.diagnostic;
  const health = agentRes?.health;
  const notifs = agentRes?.notifications;

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="glass-card p-6 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Radio className="w-6 h-6 text-emerald-400 animate-pulse" />
            <h2 className="text-xl md:text-2xl font-extrabold text-white">24/7 Live Machine Sound Telemetry</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 font-mono">Real-time Log-Mel acoustic feature stream & multi-agent AI fault evaluation.</p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <select 
            value={selectedMachine} 
            onChange={(e) => {
              onSelectMachine(e.target.value);
              setSelectedClip('auto');
            }}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs font-semibold rounded-xl px-3 py-2 outline-none focus:border-cyan-500"
          >
            <option value="fan">Primary Exhaust Fan (FAN-01)</option>
            <option value="gearbox">Conveyor Drive Gearbox (GEARBOX-01)</option>
            <option value="pump">Hydraulic Circulation Pump (PUMP-01)</option>
            <option value="valve">Steam Control Valve (VALVE-01)</option>
          </select>

          <select
            value={selectedClip}
            onChange={(e) => setSelectedClip(e.target.value)}
            className="bg-slate-900 border border-cyan-500/40 text-cyan-300 text-xs font-mono font-semibold rounded-xl px-3 py-2 outline-none focus:border-cyan-400 max-w-[200px] truncate"
            title="Select audio clip to analyze"
          >
            <option value="auto">⚡ Auto-Cycle Stream (24/7)</option>
            {availableClips.map((clip) => (
              <option key={clip} value={clip}>
                {clip}
              </option>
            ))}
          </select>

          <button
            onClick={() => fetchAnalysis('auto')}
            className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-slate-700 rounded-xl text-xs font-bold transition flex items-center gap-1"
            title="Skip to next acoustic test clip"
          >
            Next Clip ⏭️
          </button>

          <button
            onClick={() => setIsStreaming(!isStreaming)}
            className={`px-4 py-2 rounded-xl font-bold text-xs transition flex items-center gap-2 ${
              isStreaming 
                ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30 hover:bg-rose-500/30' 
                : 'bg-emerald-500 text-dark-900 hover:bg-emerald-400'
            }`}
          >
            {isStreaming ? 'Stop Sound Stream' : 'Resume 24/7 Stream'}
          </button>
        </div>
      </div>

      {/* Main Monitoring Metrics Display */}
      {telemetryState ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Health & Diagnostic Status */}
          <div className="lg:col-span-2 space-y-6">
            {/* Status Banner Card */}
            <div className={`glass-card p-6 rounded-2xl border ${
              diag?.severity === 'Normal' ? 'border-emerald-500/30 bg-emerald-950/10' : 'border-rose-500/40 bg-rose-950/20'
            }`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {diag?.severity === 'Normal' ? (
                    <ShieldCheck className="w-8 h-8 text-emerald-400" />
                  ) : (
                    <AlertOctagon className="w-8 h-8 text-rose-400 animate-bounce" />
                  )}
                  <div>
                    <h3 className="font-extrabold text-lg text-white">
                      {diag?.severity === 'Normal' ? '✅ SYSTEM FUNCTIONING NORMAL' : `🚨 ANOMALY EVENT: ${diag?.severity.toUpperCase()} SEVERITY`}
                    </h3>
                    <p className="text-xs text-slate-400 font-mono">
                      Clip ID: {telemetryState.file_name} | Section: 0{telemetryState.section}
                    </p>
                  </div>
                </div>

                <div className="text-right font-mono">
                  <div className="text-xs text-slate-400">ANOMALY SCORE</div>
                  <div className="text-2xl font-extrabold text-cyan-400">{telemetryState.anomaly_score}</div>
                  <div className="text-[10px] text-slate-500">Threshold: {telemetryState.threshold}</div>
                </div>
              </div>

              {/* Multi-Component Simultaneous Scan Grid */}
              <div className="mt-4 pt-4 border-t border-slate-800">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono">
                    🔍 Simultaneous Multi-Component Scan Results
                  </span>
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 uppercase">
                    All Components Scanned
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {diag?.all_components_scan ? (
                    diag.all_components_scan.map((comp) => {
                      const isAnomaly = comp.is_anomaly;
                      return (
                        <div key={comp.section} className={`p-3 rounded-xl border transition-all ${
                          comp.is_active_target
                            ? (isAnomaly ? 'bg-rose-950/40 border-rose-500/60 shadow-lg shadow-rose-500/10' : 'bg-slate-900/90 border-cyan-500/50 shadow-lg shadow-cyan-500/10')
                            : 'bg-slate-900/50 border-slate-800'
                        }`}>
                          <div className="flex justify-between items-start mb-1.5">
                            <span className="text-[10px] font-mono text-slate-400 font-bold uppercase tracking-wider">
                              Section 0{comp.section}
                            </span>
                            <span className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded uppercase ${
                              comp.severity === 'Normal' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                              comp.severity === 'Low' ? 'bg-sky-500/20 text-sky-400 border border-sky-500/30' :
                              comp.severity === 'Medium' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                              'bg-rose-500/20 text-rose-400 border border-rose-500/30 animate-pulse'
                            }`}>
                              {comp.severity}
                            </span>
                          </div>

                          <div className="font-bold text-xs text-slate-200 truncate" title={comp.component_name}>
                            {comp.component_name}
                          </div>

                          <div className="mt-2 pt-2 border-t border-slate-800/80 flex items-center justify-between font-mono">
                            <div>
                              <div className="text-[9px] text-slate-400">SCORE / THRESHOLD</div>
                              <div className={`text-xs font-extrabold ${isAnomaly ? 'text-rose-400' : 'text-cyan-400'}`}>
                                {comp.anomaly_score} <span className="text-[9px] text-slate-500">/ {comp.threshold}</span>
                              </div>
                            </div>

                            <div className="text-right">
                              <div className="text-[9px] text-slate-400">HEALTH INDEX</div>
                              <div className={`text-xs font-bold ${comp.health_index > 80 ? 'text-emerald-400' : 'text-amber-400'}`}>
                                {comp.health_index}% ({comp.risk_pct}% Risk)
                              </div>
                            </div>
                          </div>

                          <div className="mt-1.5 text-[10px] text-slate-400 truncate" title={comp.issue}>
                            Action: <span className="text-cyan-300 font-semibold">{comp.recommendation}</span>
                          </div>
                        </div>
                      );
                    })
                  ) : (
                    <div className="col-span-3 text-xs text-slate-400 font-mono text-center p-2">
                      Scanning components...
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Frame-level Deviation Chart */}
            <div className="glass-card p-6 rounded-2xl space-y-4">
              <h3 className="font-bold text-base text-slate-100 flex items-center gap-2">
                <Volume2 className="w-5 h-5 text-cyan-400" /> Time-Domain Acoustic Reconstruction Loss Profile
              </h3>

              <div className="h-44 flex items-end gap-1.5 pt-6 pb-2 px-2 bg-dark-900/80 rounded-xl border border-slate-800">
                {telemetryState.frame_errors?.map((err, idx) => {
                  const heightPct = Math.min(100, Math.max(15, (err / (telemetryState.threshold * 1.5)) * 100));
                  const isHigh = err > telemetryState.threshold;
                  return (
                    <div key={idx} className="flex-1 flex flex-col items-center gap-1 group relative">
                      <div 
                        style={{ height: `${heightPct}%` }}
                        className={`w-full rounded-t-sm transition-all duration-300 ${
                          isHigh ? 'bg-rose-500 shadow-lg shadow-rose-500/50' : 'bg-cyan-500/60 group-hover:bg-cyan-400'
                        }`}
                      />
                      <div className="absolute -top-7 opacity-0 group-hover:opacity-100 transition bg-slate-800 text-[10px] text-slate-200 px-1.5 py-0.5 rounded font-mono z-10 pointer-events-none">
                        {err}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Right Column: Multi-Channel Alert Payload Simulator */}
          <div className="space-y-6">
            <div className="glass-card p-6 rounded-2xl space-y-4">
              <h3 className="font-bold text-base text-slate-100 flex items-center gap-2">
                <Send className="w-5 h-5 text-indigo-400" /> Instant Multi-Channel Alert Dispatch
              </h3>
              <p className="text-xs text-slate-400">Real-time alert payload compiled by the Notification Agent:</p>

              <div className="flex border-b border-slate-800 text-xs font-semibold">
                <button
                  onClick={() => setActiveTabPayload('telegram')}
                  className={`px-3 py-2 border-b-2 transition ${activeTabPayload === 'telegram' ? 'border-cyan-400 text-cyan-400' : 'border-transparent text-slate-400'}`}
                >
                  Telegram
                </button>
                <button
                  onClick={() => setActiveTabPayload('whatsapp')}
                  className={`px-3 py-2 border-b-2 transition ${activeTabPayload === 'whatsapp' ? 'border-cyan-400 text-cyan-400' : 'border-transparent text-slate-400'}`}
                >
                  WhatsApp
                </button>
                <button
                  onClick={() => setActiveTabPayload('email')}
                  className={`px-3 py-2 border-b-2 transition ${activeTabPayload === 'email' ? 'border-cyan-400 text-cyan-400' : 'border-transparent text-slate-400'}`}
                >
                  Email HTML
                </button>
              </div>

              <div className="p-3 bg-dark-900 rounded-xl border border-slate-800 text-xs font-mono overflow-x-auto max-h-72">
                {activeTabPayload === 'telegram' && <pre className="text-emerald-400 whitespace-pre-wrap">{notifs?.telegram}</pre>}
                {activeTabPayload === 'whatsapp' && <pre className="text-cyan-400 whitespace-pre-wrap">{notifs?.whatsapp}</pre>}
                {activeTabPayload === 'email' && <pre className="text-slate-300 whitespace-pre-wrap">{notifs?.email}</pre>}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="glass-card p-12 text-center text-slate-400 font-mono">
          Connecting to acoustic sensor telemetry stream...
        </div>
      )}
    </div>
  );
}
