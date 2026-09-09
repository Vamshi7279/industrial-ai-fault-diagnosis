import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Clock, 
  DollarSign, 
  PieChart as PieIcon, 
  Zap 
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  Legend 
} from 'recharts';

export default function AnalyticsView() {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const res = await fetch('/api/reports/analytics');
        if (res.ok) setAnalyticsData(await res.json());
      } catch (e) {
        console.error("Fetch analytics error:", e);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading || !analyticsData) {
    return (
      <div className="p-8 text-center text-slate-400 font-mono animate-pulse">
        Compiling visual analytics & plant reliability report...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="glass-card p-6 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-emerald-400" />
            <h2 className="text-xl md:text-2xl font-extrabold text-white">Plant Reliability & Performance Analytics</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 font-mono">Visual charts for MTBF (Mean Time Between Failures), severity distribution, downtime saved, and spare part costs.</p>
        </div>
      </div>

      {/* Metric Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="glass-card p-5 rounded-2xl border border-emerald-500/20 bg-emerald-950/10 flex items-center justify-between">
          <div>
            <div className="text-xs font-mono text-slate-400">UNPLANNED DOWNTIME SAVED</div>
            <div className="text-3xl font-extrabold text-emerald-400 mt-1">{analyticsData.downtime_saved_hours} Hours</div>
            <div className="text-[11px] text-slate-500 mt-1">Prevented catastrophic machine lockup through acoustic early detection</div>
          </div>
          <Clock className="w-10 h-10 text-emerald-400 opacity-80" />
        </div>

        <div className="glass-card p-5 rounded-2xl border border-cyan-500/20 bg-cyan-950/10 flex items-center justify-between">
          <div>
            <div className="text-xs font-mono text-slate-400">ESTIMATED MAINTENANCE EXPENSE SAVINGS</div>
            <div className="text-3xl font-extrabold text-cyan-400 mt-1">${analyticsData.parts_cost_saved_usd?.toLocaleString()} USD</div>
            <div className="text-[11px] text-slate-500 mt-1">Saved on emergency secondary damage & expedited freight charges</div>
          </div>
          <DollarSign className="w-10 h-10 text-cyan-400 opacity-80" />
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Severity Distribution Pie Chart */}
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <h3 className="font-bold text-base text-slate-100 flex items-center gap-2">
            <PieIcon className="w-5 h-5 text-indigo-400" /> Fault Severity Frequency Distribution
          </h3>

          <div className="h-64 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={analyticsData.severity_distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {analyticsData.severity_distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }} />
                <Legend formatter={(value) => <span className="text-xs text-slate-300 font-mono">{value}</span>} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* MTBF Bar Chart */}
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <h3 className="font-bold text-base text-slate-100 flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-400" /> Mean Time Between Failures (MTBF in Hours)
          </h3>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analyticsData.mtbf_metrics}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="machine" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }} />
                <Bar dataKey="mtbf_hours" fill="#38bdf8" name="Actual MTBF (Hours)" radius={[6, 6, 0, 0]} />
                <Bar dataKey="target_mtbf" fill="#818cf8" name="Target Benchmark" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
