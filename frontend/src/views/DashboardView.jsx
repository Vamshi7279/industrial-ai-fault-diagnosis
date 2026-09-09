import React from 'react';
import { 
  Cpu, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Activity, 
  Wrench, 
  ArrowUpRight, 
  Clock 
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid 
} from 'recharts';

export default function DashboardView({ stats, onSelectMachine, onNavigate }) {
  if (!stats) {
    return (
      <div className="p-8 text-center text-slate-400 font-mono animate-pulse">
        Loading plant operational telemetry...
      </div>
    );
  }

  const kpis = [
    { label: 'Total Machines', value: stats.total_machines, icon: Cpu, color: 'text-cyan-400', bg: 'bg-cyan-500/10 border-cyan-500/20' },
    { label: 'Healthy Assets', value: stats.healthy_machines, icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20' },
    { label: 'Warning State', value: stats.warning_machines, icon: AlertTriangle, color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20' },
    { label: 'Critical Faults', value: stats.critical_machines, icon: XCircle, color: 'text-rose-400', bg: 'bg-rose-500/10 border-rose-500/20' },
    { label: 'Plant Health Index', value: `${stats.overall_plant_health}%`, icon: Activity, color: 'text-indigo-400', bg: 'bg-indigo-500/10 border-indigo-500/20' },
    { label: 'Upcoming Service', value: stats.upcoming_maintenance, icon: Wrench, color: 'text-purple-400', bg: 'bg-purple-500/10 border-purple-500/20' },
  ];

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="glass-card p-6 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-gradient-to-r from-slate-900/90 via-dark-800 to-indigo-950/40">
        <div>
          <h2 className="text-xl md:text-2xl font-extrabold text-white">Plant Operational Overview</h2>
          <p className="text-xs text-slate-400 mt-1 font-mono">Real-time acoustic telemetry & automated maintenance dispatch active across 4 primary assembly lines.</p>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={() => onNavigate('monitoring')}
            className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-dark-900 font-bold text-xs transition shadow-lg shadow-cyan-500/20 flex items-center gap-2"
          >
            Open Live Telemetry <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        {kpis.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div key={idx} className={`glass-card glass-card-hover p-4 rounded-2xl border ${kpi.bg}`}>
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">{kpi.label}</span>
                <Icon className={`w-5 h-5 ${kpi.color}`} />
              </div>
              <div className={`text-2xl font-extrabold mt-2 ${kpi.color}`}>{kpi.value}</div>
            </div>
          );
        })}
      </div>

      {/* Health Trend Chart & Recent Activity Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recharts Line Chart */}
        <div className="lg:col-span-2 glass-card p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-base text-slate-100">Machine Health Score History</h3>
              <p className="text-xs text-slate-400 font-mono">5-day historical stability curve per machine line</p>
            </div>
            <span className="text-xs font-mono text-cyan-400 bg-cyan-500/10 px-2.5 py-1 rounded-full border border-cyan-500/20">
              Mean Plant Health: {stats.overall_plant_health}%
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={stats.health_trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="day" stroke="#64748b" fontSize={11} />
                <YAxis domain={[80, 100]} stroke="#64748b" fontSize={11} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }} 
                />
                <Line type="monotone" dataKey="fan" stroke="#38bdf8" strokeWidth={2.5} name="Exhaust Fan" />
                <Line type="monotone" dataKey="gearbox" stroke="#fbbf24" strokeWidth={2.5} name="Conveyor Gearbox" />
                <Line type="monotone" dataKey="pump" stroke="#34d399" strokeWidth={2.5} name="Hydraulic Pump" />
                <Line type="monotone" dataKey="valve" stroke="#818cf8" strokeWidth={2.5} name="Steam Valve" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Work Orders / Alerts Stream */}
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-base text-slate-100">Recent Work Orders</h3>
            <button onClick={() => onNavigate('maintenance')} className="text-xs text-cyan-400 hover:underline">View All</button>
          </div>

          <div className="space-y-3">
            {stats.recent_tickets?.slice(0, 4).map((ticket) => (
              <div key={ticket.id} className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-cyan-400">#{ticket.id}</span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    ticket.severity === 'High' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                  }`}>
                    {ticket.severity} Severity
                  </span>
                </div>
                <div className="text-xs font-semibold text-slate-200">{ticket.machine_name}</div>
                <div className="text-[11px] text-slate-400 truncate">{ticket.issue_description}</div>
                <div className="text-[10px] text-slate-500 flex items-center gap-1 font-mono pt-1">
                  <Clock className="w-3 h-3" /> Assigned: {ticket.tech_name || 'Pending'}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Machine Status Cards Summary Table */}
      <div className="glass-card p-6 rounded-2xl space-y-4">
        <h3 className="font-bold text-base text-slate-100">Plant Asset Directory</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.machines_summary?.map((m) => (
            <div 
              key={m.id} 
              onClick={() => onSelectMachine(m.type)}
              className="glass-card glass-card-hover p-4 rounded-xl border border-slate-800 cursor-pointer space-y-3"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-cyan-400">{m.id}</span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                  m.health_score >= 85 ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                }`}>
                  {m.health_score}% Health
                </span>
              </div>
              <div>
                <h4 className="font-bold text-sm text-slate-200">{m.name}</h4>
                <p className="text-[11px] text-slate-400">{m.location}</p>
              </div>
              <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[11px]">
                <span className="text-slate-400 font-mono">{m.operating_hours} hrs operating</span>
                <span className="text-cyan-400 hover:underline">Inspect →</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
