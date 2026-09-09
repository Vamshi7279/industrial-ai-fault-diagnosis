import React from 'react';
import { 
  Users, 
  ShieldCheck, 
  Check, 
  X, 
  Lock 
} from 'lucide-react';

export default function RbacView({ currentRole, onRoleChange, rolesMap }) {
  const permissionsList = [
    { key: 'view_dashboard', label: 'View Plant Dashboard & KPIs' },
    { key: 'view_telemetry', label: 'Access 24/7 Live Sound Streams' },
    { key: 'view_alerts', label: 'Inspect Real-Time Alerts' },
    { key: 'ack_alerts', label: 'Acknowledge Active Alerts' },
    { key: 'manage_tickets', label: 'Create & Edit Maintenance Work Orders' },
    { key: 'assign_techs', label: 'Assign Technicians to Work Orders' },
    { key: 'verify_repairs', label: 'Execute Post-Repair Acoustic Verification' },
    { key: 'generate_rfp', label: 'Compile Manufacturer Service Requests (RFPs)' },
    { key: 'parts_inventory', label: 'Access & Reorder Spare Parts' },
    { key: 'chat_ai', label: 'Use AI Maintenance Assistant' },
    { key: 'view_reports', label: 'View Plant Reliability Reports & MTBF Analytics' }
  ];

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="glass-card p-6 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Users className="w-6 h-6 text-cyan-400" />
            <h2 className="text-xl md:text-2xl font-extrabold text-white">Role-Based Access Control (RBAC) Management</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 font-mono">Manage operational permissions and switch active roles across Admin, Floor Manager, Maintenance Manager, and Technician.</p>
        </div>
      </div>

      {/* Role Switcher Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Object.keys(rolesMap).map((roleKey) => {
          const r = rolesMap[roleKey];
          const isCurrent = currentRole === roleKey;
          return (
            <div
              key={roleKey}
              onClick={() => onRoleChange(roleKey)}
              className={`glass-card p-5 rounded-2xl border cursor-pointer transition-all duration-200 ${
                isCurrent 
                  ? 'border-cyan-500 bg-cyan-500/10 shadow-lg shadow-cyan-500/20' 
                  : 'border-slate-800 hover:border-slate-700 bg-slate-900/60'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider">{roleKey.replace('_', ' ')}</span>
                {isCurrent && <ShieldCheck className="w-5 h-5 text-cyan-400" />}
              </div>
              <h3 className="font-bold text-sm text-slate-200 mt-2">{r.title}</h3>
              <p className="text-[11px] text-slate-400 mt-1">{r.desc}</p>

              <button className={`w-full mt-4 py-1.5 rounded-lg text-xs font-bold transition ${
                isCurrent ? 'bg-cyan-500 text-dark-900' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}>
                {isCurrent ? 'Active Operating Role' : 'Switch to Role'}
              </button>
            </div>
          );
        })}
      </div>

      {/* Permissions Comparison Matrix Table */}
      <div className="glass-card p-6 rounded-2xl space-y-4">
        <h3 className="font-bold text-base text-slate-100">Role Permission Matrix</h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800 uppercase tracking-wider">
              <tr>
                <th className="p-3">Permission Description</th>
                <th className="p-3 text-center">Admin</th>
                <th className="p-3 text-center">Floor Manager</th>
                <th className="p-3 text-center">Maintenance Manager</th>
                <th className="p-3 text-center">Technician</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {permissionsList.map((perm) => (
                <tr key={perm.key} className="hover:bg-slate-800/40 transition">
                  <td className="p-3 font-semibold text-slate-200">{perm.label}</td>
                  <td className="p-3 text-center text-emerald-400"><Check className="w-4 h-4 mx-auto" /></td>
                  <td className="p-3 text-center">
                    {['view_dashboard', 'view_telemetry', 'view_alerts', 'chat_ai', 'view_reports'].includes(perm.key) ? (
                      <Check className="w-4 h-4 mx-auto text-emerald-400" />
                    ) : (
                      <X className="w-4 h-4 mx-auto text-slate-600" />
                    )}
                  </td>
                  <td className="p-3 text-center">
                    {['view_dashboard', 'view_alerts', 'ack_alerts', 'manage_tickets', 'assign_techs', 'generate_rfp', 'parts_inventory', 'chat_ai'].includes(perm.key) ? (
                      <Check className="w-4 h-4 mx-auto text-emerald-400" />
                    ) : (
                      <X className="w-4 h-4 mx-auto text-slate-600" />
                    )}
                  </td>
                  <td className="p-3 text-center">
                    {['view_alerts', 'verify_repairs', 'parts_inventory', 'chat_ai'].includes(perm.key) ? (
                      <Check className="w-4 h-4 mx-auto text-emerald-400" />
                    ) : (
                      <X className="w-4 h-4 mx-auto text-slate-600" />
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
