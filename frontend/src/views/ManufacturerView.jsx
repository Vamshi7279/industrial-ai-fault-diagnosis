import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  Mail, 
  Phone, 
  FileText, 
  Send, 
  ShieldCheck, 
  Copy 
} from 'lucide-react';

export default function ManufacturerView() {
  const [manufacturers, setManufacturers] = useState([]);
  const [rfpOutput, setRfpOutput] = useState(null);
  const [selectedMachineId, setSelectedMachineId] = useState('FAN-01');
  const [severityInput, setSeverityInput] = useState('High');
  const [descInput, setDescInput] = useState('Dynamic imbalance & inner race bearing friction detected.');

  useEffect(() => {
    const fetchMfrs = async () => {
      try {
        const res = await fetch('/api/manufacturers');
        if (res.ok) setManufacturers(await res.json());
      } catch (e) {
        console.error("Fetch mfrs error:", e);
      }
    };
    fetchMfrs();
  }, []);

  const handleGenerateRfp = async () => {
    try {
      const res = await fetch('/api/manufacturers/service-request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          machine_id: selectedMachineId,
          component_name: "High-Speed Bearing / Pinion Assembly",
          severity: severityInput,
          issue_desc: descInput
        })
      });
      if (res.ok) {
        const data = await res.json();
        setRfpOutput(data);
      }
    } catch (e) {
      console.error("RFP generation error:", e);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="glass-card p-6 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Building2 className="w-6 h-6 text-cyan-400" />
            <h2 className="text-xl md:text-2xl font-extrabold text-white">Authorized Manufacturers & Technical Service Network</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 font-mono">Direct technical service facilities, specialist contacts, and 1-click manufacturer RFP service request generator.</p>
        </div>
      </div>

      {/* Grid: Manufacturers Cards & RFP Generator */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Manufacturer Cards List */}
        <div className="space-y-4">
          <h3 className="font-bold text-base text-slate-100">Authorized Service Centers</h3>
          {manufacturers.map((mfr) => (
            <div key={mfr.id} className="glass-card p-4 rounded-xl space-y-2 border border-slate-800">
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-slate-200">{mfr.name}</span>
                <span className="text-[10px] font-mono text-cyan-400 font-bold px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">
                  {mfr.id}
                </span>
              </div>
              <div className="text-xs text-slate-400 font-semibold">{mfr.service_center}</div>
              <div className="text-[11px] text-slate-500 font-mono space-y-0.5">
                <div className="flex items-center gap-1.5"><Mail className="w-3.5 h-3.5 text-cyan-400" /> {mfr.contact_email}</div>
                <div className="flex items-center gap-1.5"><Phone className="w-3.5 h-3.5 text-emerald-400" /> {mfr.contact_phone}</div>
              </div>
            </div>
          ))}
        </div>

        {/* 1-Click RFP Generator & RFP Output Inspector */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-card p-6 rounded-2xl space-y-4">
            <h3 className="font-bold text-base text-slate-100 flex items-center gap-2">
              <FileText className="w-5 h-5 text-indigo-400" /> 1-Click Manufacturer Service Request (RFP) Generator
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-mono text-slate-400 mb-1">Target Machine Asset:</label>
                <select
                  value={selectedMachineId}
                  onChange={(e) => setSelectedMachineId(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 text-xs text-slate-200 font-semibold rounded-xl p-2.5 outline-none focus:border-cyan-500"
                >
                  <option value="FAN-01">FAN-01 (Primary Exhaust Cooling Fan)</option>
                  <option value="GEARBOX-01">GEARBOX-01 (Heavy Conveyor Drive Gearbox)</option>
                  <option value="PUMP-01">PUMP-01 (Coolant Circulation Hydraulic Pump)</option>
                  <option value="VALVE-01">VALVE-01 (High-Pressure Steam Control Valve)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-mono text-slate-400 mb-1">Severity Classification:</label>
                <select
                  value={severityInput}
                  onChange={(e) => setSeverityInput(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 text-xs text-slate-200 font-semibold rounded-xl p-2.5 outline-none focus:border-cyan-500"
                >
                  <option value="Critical">Critical (Immediate Seizure Danger)</option>
                  <option value="High">High (Severe Mechanical Friction)</option>
                  <option value="Medium">Medium (Micro-pitting / Wear)</option>
                  <option value="Low">Low (Minor Viscosity Chatter)</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1">Diagnostic Issue Summary:</label>
              <input
                type="text"
                value={descInput}
                onChange={(e) => setDescInput(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 text-xs text-slate-200 font-mono rounded-xl p-2.5 outline-none focus:border-cyan-500"
              />
            </div>

            <button
              onClick={handleGenerateRfp}
              className="px-5 py-2.5 rounded-xl bg-indigo-500 hover:bg-indigo-400 text-white font-bold text-xs transition shadow-lg shadow-indigo-500/20 flex items-center gap-2"
            >
              <Send className="w-4 h-4" /> Compile Official RFP Document
            </button>
          </div>

          {rfpOutput && (
            <div className="glass-card p-6 rounded-2xl space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="font-bold text-sm text-cyan-400 font-mono">Generated RFP Document ID: #{rfpOutput.rfp_id}</h4>
                <button
                  onClick={() => navigator.clipboard.writeText(rfpOutput.rfp_text)}
                  className="px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono flex items-center gap-1.5"
                >
                  <Copy className="w-3.5 h-3.5" /> Copy Document
                </button>
              </div>

              <pre className="p-4 bg-dark-900 rounded-xl border border-slate-800 text-xs font-mono text-emerald-400 whitespace-pre-wrap">
                {rfpOutput.rfp_text}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
