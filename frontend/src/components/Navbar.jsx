import React from 'react';
import { 
  Activity, 
  Bell, 
  ShieldCheck, 
  Wifi, 
  WifiOff, 
  User, 
  ChevronDown, 
  Menu 
} from 'lucide-react';

export default function Navbar({ 
  currentRole, 
  onRoleChange, 
  wsConnected, 
  alertCount, 
  toggleSidebar, 
  rolesMap 
}) {
  return (
    <header className="h-16 bg-dark-800/80 backdrop-blur-md border-b border-slate-800/80 px-4 md:px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <button 
          onClick={toggleSidebar} 
          className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition md:hidden"
        >
          <Menu className="w-5 h-5" />
        </button>
        
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-indigo-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Activity className="w-5 h-5 text-dark-900 stroke-[2.5]" />
          </div>
          <div>
            <h1 className="font-extrabold text-base tracking-wide glowing-text">PREDICTIVE MAINTENANCE SaaS</h1>
            <p className="text-[10px] text-slate-400 font-mono hidden sm:block">Agentic AI Plant Operating System v2.0</p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* WebSocket Connection Indicator */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/80 border border-slate-800 text-xs font-mono">
          {wsConnected ? (
            <>
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-emerald-400 flex items-center gap-1">
                <Wifi className="w-3.5 h-3.5" /> LIVE TELEMETRY
              </span>
            </>
          ) : (
            <>
              <span className="w-2 h-2 rounded-full bg-amber-400"></span>
              <span className="text-amber-400 flex items-center gap-1">
                <WifiOff className="w-3.5 h-3.5" /> REST POLL
              </span>
            </>
          )}
        </div>

        {/* Notifications */}
        <button className="relative p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition">
          <Bell className="w-5 h-5" />
          {alertCount > 0 && (
            <span className="absolute top-1 right-1 w-4 h-4 bg-rose-500 text-white font-mono text-[10px] font-bold rounded-full flex items-center justify-center animate-bounce">
              {alertCount}
            </span>
          )}
        </button>

        {/* Role Selector */}
        <div className="relative group">
          <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 cursor-pointer hover:border-slate-700 transition">
            <div className="w-7 h-7 rounded-lg bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center font-bold text-xs">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <div className="text-left hidden md:block">
              <div className="text-xs font-semibold text-slate-200">{rolesMap[currentRole]?.title}</div>
              <div className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">{currentRole.replace('_', ' ')}</div>
            </div>
            <ChevronDown className="w-4 h-4 text-slate-400" />
          </div>

          {/* Role Dropdown */}
          <div className="absolute right-0 top-full mt-2 w-56 bg-dark-800 border border-slate-700/80 rounded-xl shadow-2xl p-1.5 opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto transition-all duration-200 z-50">
            <div className="px-3 py-2 text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              Select Operating Role (RBAC)
            </div>
            {Object.keys(rolesMap).map((roleKey) => (
              <button
                key={roleKey}
                onClick={() => onRoleChange(roleKey)}
                className={`w-full text-left px-3 py-2 rounded-lg text-xs font-medium transition flex items-center justify-between ${
                  currentRole === roleKey 
                    ? 'bg-cyan-500/10 text-cyan-400 font-bold border border-cyan-500/20' 
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`}
              >
                <span>{rolesMap[roleKey].title}</span>
                {currentRole === roleKey && <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>}
              </button>
            ))}
          </div>
        </div>
      </div>
    </header>
  );
}
