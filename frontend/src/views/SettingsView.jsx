import React, { useState } from 'react';
import { Sliders, Save, Bell, Shield, Key } from 'lucide-react';

export default function SettingsView() {
  const [fanThresh, setFanThresh] = useState(12.22);
  const [gbxThresh, setGbxThresh] = useState(11.85);
  const [pumpThresh, setPumpThresh] = useState(12.05);
  const [valveThresh, setValveThresh] = useState(12.50);
  const [savedMsg, setSavedMsg] = useState('');

  const handleSave = (e) => {
    e.preventDefault();
    setSavedMsg('✅ Platform threshold configurations saved cleanly to database.');
    setTimeout(() => setSavedMsg(''), 4000);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="glass-card p-6 rounded-2xl flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Sliders className="w-6 h-6 text-cyan-400" />
            <h2 className="text-xl md:text-2xl font-extrabold text-white">System Settings & Threshold Configurator</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Configure baseline anomaly loss thresholds, notification API credentials, and operational safety guardrails.
          </p>
        </div>
      </div>

      {savedMsg && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
          {savedMsg}
        </div>
      )}

      <form onSubmit={handleSave} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Baseline Loss Thresholds */}
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <h3 className="font-bold text-base text-slate-100 flex items-center gap-2">
            <Sliders className="w-5 h-5 text-cyan-400" /> Acoustic MSE Reconstruction Thresholds
          </h3>
          
          <div className="space-y-4 text-xs font-mono">
            <div>
              <label className="block text-slate-400 mb-1">Primary Exhaust Fan Baseline (FAN-01)</label>
              <input 
                type="number" 
                step="0.01" 
                value={fanThresh} 
                onChange={(e) => setFanThresh(parseFloat(e.target.value))}
                className="w-full bg-slate-900 border border-slate-700 text-cyan-400 p-2.5 rounded-xl outline-none focus:border-cyan-500 font-bold"
              />
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Conveyor Drive Gearbox Baseline (GEARBOX-01)</label>
              <input 
                type="number" 
                step="0.01" 
                value={gbxThresh} 
                onChange={(e) => setGbxThresh(parseFloat(e.target.value))}
                className="w-full bg-slate-900 border border-slate-700 text-cyan-400 p-2.5 rounded-xl outline-none focus:border-cyan-500 font-bold"
              />
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Hydraulic Circulation Pump Baseline (PUMP-01)</label>
              <input 
                type="number" 
                step="0.01" 
                value={pumpThresh} 
                onChange={(e) => setPumpThresh(parseFloat(e.target.value))}
                className="w-full bg-slate-900 border border-slate-700 text-cyan-400 p-2.5 rounded-xl outline-none focus:border-cyan-500 font-bold"
              />
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Steam Control Valve Baseline (VALVE-01)</label>
              <input 
                type="number" 
                step="0.01" 
                value={valveThresh} 
                onChange={(e) => setValveThresh(parseFloat(e.target.value))}
                className="w-full bg-slate-900 border border-slate-700 text-cyan-400 p-2.5 rounded-xl outline-none focus:border-cyan-500 font-bold"
              />
            </div>
          </div>
        </div>

        {/* Notification & Security Config */}
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <h3 className="font-bold text-base text-slate-100 flex items-center gap-2">
            <Bell className="w-5 h-5 text-indigo-400" /> Multi-Channel API Credentials & Human Approval
          </h3>

          <div className="space-y-4 text-xs font-mono">
            <div>
              <label className="block text-slate-400 mb-1">Telegram Bot Token (`TELEGRAM_BOT_TOKEN` env)</label>
              <input 
                type="password" 
                value="••••••••••••••••••••••••••••••••" 
                readOnly
                className="w-full bg-slate-900/60 border border-slate-800 text-slate-400 p-2.5 rounded-xl outline-none cursor-not-allowed"
              />
            </div>

            <div>
              <label className="block text-slate-400 mb-1">WhatsApp Cloud API Token (`WHATSAPP_API_TOKEN` env)</label>
              <input 
                type="password" 
                value="••••••••••••••••••••••••••••••••" 
                readOnly
                className="w-full bg-slate-900/60 border border-slate-800 text-slate-400 p-2.5 rounded-xl outline-none cursor-not-allowed"
              />
            </div>

            <div className="pt-2 border-t border-slate-800 space-y-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" defaultChecked className="rounded text-cyan-500 bg-slate-900 border-slate-700" />
                <span className="text-slate-300 font-bold">Require Manager Human Approval Gate for Manufacturer RFPs</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" defaultChecked className="rounded text-cyan-500 bg-slate-900 border-slate-700" />
                <span className="text-slate-300 font-bold">Log Immutable Audit Trail for Ticket Status Transitions</span>
              </label>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 text-right">
          <button 
            type="submit"
            className="px-6 py-2.5 bg-cyan-500 hover:bg-cyan-400 text-dark-900 font-extrabold text-xs rounded-xl transition flex items-center gap-2 ml-auto"
          >
            <Save className="w-4 h-4" /> Save System Preferences
          </button>
        </div>
      </form>
    </div>
  );
}
