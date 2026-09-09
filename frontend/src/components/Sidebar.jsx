import React from 'react';
import { 
  LayoutDashboard, 
  Radio, 
  Cpu, 
  AlertTriangle, 
  Wrench, 
  Package, 
  Building2, 
  Bot, 
  BarChart3, 
  Users, 
  ChevronLeft, 
  ChevronRight,
  Bell,
  FileText,
  Activity,
  Settings
} from 'lucide-react';

export default function Sidebar({ 
  currentTab, 
  onSelectTab, 
  isCollapsed, 
  toggleCollapse, 
  isOpenMobile, 
  closeMobile 
}) {
  const menuItems = [
    { id: 'dashboard', label: 'Overview Dashboard', icon: LayoutDashboard, badge: null },
    { id: 'monitoring', label: 'Live Machine Monitoring', icon: Radio, badge: 'LIVE' },
    { id: 'machine-detail', label: 'Machine Details Page', icon: Cpu, badge: null },
    { id: 'alerts', label: 'Real-Time Alerts Center', icon: AlertTriangle, badge: 'ALERT' },
    { id: 'notifications', label: 'Notification Center', icon: Bell, badge: 'NOTIF' },
    { id: 'maintenance', label: 'Maintenance Management', icon: Wrench, badge: null },
    { id: 'inventory', label: 'Spare Parts Inventory', icon: Package, badge: null },
    { id: 'manufacturers', label: 'Manufacturer Support', icon: Building2, badge: null },
    { id: 'audit-log', label: 'Audit Log Inspector', icon: FileText, badge: null },
    { id: 'system-health', label: 'System Health Observability', icon: Activity, badge: 'SYS' },
    { id: 'ai-assistant', label: 'AI Maintenance Assistant', icon: Bot, badge: 'AI' },
    { id: 'analytics', label: 'Reports & Visual Analytics', icon: BarChart3, badge: null },
    { id: 'settings', label: 'System Settings', icon: Settings, badge: null },
    { id: 'rbac', label: 'Role Access Manager', icon: Users, badge: null }
  ];

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {isOpenMobile && (
        <div 
          onClick={closeMobile} 
          className="fixed inset-0 bg-dark-900/80 backdrop-blur-sm z-40 md:hidden"
        />
      )}

      <aside className={`
        fixed md:static top-16 bottom-0 left-0 z-40
        bg-dark-800/95 border-r border-slate-800/80
        flex flex-col justify-between transition-all duration-300 ease-in-out
        ${isCollapsed ? 'w-20' : 'w-64'}
        ${isOpenMobile ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        {/* Main Navigation List */}
        <div className="p-3 space-y-1 overflow-y-auto">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => {
                  onSelectTab(item.id);
                  closeMobile();
                }}
                className={`
                  w-full flex items-center gap-3 px-3 py-2.5 rounded-xl font-medium text-xs transition-all duration-200 group relative
                  ${isActive 
                    ? 'bg-gradient-to-r from-cyan-500/20 to-indigo-500/10 text-cyan-400 font-semibold border border-cyan-500/30 shadow-lg shadow-cyan-500/10' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'}
                `}
                title={isCollapsed ? item.label : undefined}
              >
                <Icon className={`w-5 h-5 flex-shrink-0 transition-transform duration-200 ${isActive ? 'text-cyan-400 scale-110' : 'text-slate-400 group-hover:text-slate-200'}`} />
                
                {!isCollapsed && (
                  <span className="truncate flex-1 text-left">{item.label}</span>
                )}

                {!isCollapsed && item.badge && (
                  <span className={`
                    text-[9px] font-mono font-bold px-1.5 py-0.5 rounded-md uppercase tracking-wider
                    ${item.badge === 'LIVE' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 animate-pulse' : ''}
                    ${item.badge === 'ALERT' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' : ''}
                    ${item.badge === 'AI' ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30' : ''}
                  `}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Desktop Collapse Toggle */}
        <div className="p-3 border-t border-slate-800/80 hidden md:block">
          <button
            onClick={toggleCollapse}
            className="w-full flex items-center justify-center p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/60 transition"
          >
            {isCollapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
          </button>
        </div>
      </aside>
    </>
  );
}
