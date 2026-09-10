import React, { useState, useEffect } from 'react';
import { Send, CheckCircle2, AlertTriangle, Clock, RefreshCw, Filter } from 'lucide-react';
import { getApiBase } from '../apiConfig';

export default function NotificationCenterView() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [channelFilter, setChannelFilter] = useState('all');

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${getApiBase()}/api/v2/notifications`);
      if (res.ok) {
        const data = await res.json();
        setNotifications(data);
      }
    } catch (e) {
      console.error("Fetch notifications error:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 8000);
    return () => clearInterval(interval);
  }, []);

  const filtered = channelFilter === 'all' 
    ? notifications 
    : notifications.filter(n => n.channel.toLowerCase() === channelFilter);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="glass-card p-6 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-3">
            <Send className="w-6 h-6 text-indigo-400" />
            <h2 className="text-xl md:text-2xl font-extrabold text-white">Multi-Channel Notification Center</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Live dispatch audit logs for Telegram Bot API, WhatsApp Business Cloud API, Email SMTP, and Web Dashboard.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select 
            value={channelFilter} 
            onChange={(e) => setChannelFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs font-semibold rounded-xl px-3 py-2 outline-none focus:border-cyan-500 font-mono"
          >
            <option value="all">All Channels (Telegram, WA, Email)</option>
            <option value="telegram">Telegram Bot</option>
            <option value="whatsapp">WhatsApp Cloud API</option>
            <option value="email">Email (SMTP)</option>
          </select>

          <button 
            onClick={fetchNotifications}
            className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-slate-700 rounded-xl text-xs font-bold transition flex items-center gap-2"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </button>
        </div>
      </div>

      {/* Notification Table List */}
      <div className="glass-card p-6 rounded-2xl space-y-4">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800 uppercase tracking-wider">
              <tr>
                <th className="p-3">Timestamp</th>
                <th className="p-3">Channel</th>
                <th className="p-3">Recipient</th>
                <th className="p-3">Alert ID</th>
                <th className="p-3">Status</th>
                <th className="p-3">Payload Summary</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map((n) => (
                <tr key={n.id} className="hover:bg-slate-800/40 transition">
                  <td className="p-3 font-bold text-cyan-400">{n.sent_at || "Just now"}</td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded font-bold uppercase ${
                      n.channel === 'telegram' ? 'bg-sky-500/20 text-sky-400 border border-sky-500/30' :
                      n.channel === 'whatsapp' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                      'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                    }`}>
                      {n.channel}
                    </span>
                  </td>
                  <td className="p-3 text-slate-200">{n.recipient}</td>
                  <td className="p-3 text-indigo-400 font-bold">{n.alert_id || "SYS-EVENT"}</td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded font-bold flex items-center w-fit gap-1 ${
                      n.status === 'Sent' || n.status === 'Delivered' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                    }`}>
                      <CheckCircle2 className="w-3 h-3" /> {n.status}
                    </span>
                  </td>
                  <td className="p-3 text-slate-400 max-w-xs truncate" title={n.content}>
                    {n.content?.substring(0, 70)}...
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan="6" className="p-8 text-center text-slate-500 font-mono">
                    No notification dispatch logs recorded.
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
