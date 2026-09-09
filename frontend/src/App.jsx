import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';

import DashboardView from './views/DashboardView';
import LiveMonitoringView from './views/LiveMonitoringView';
import MachineDetailView from './views/MachineDetailView';
import AlertsView from './views/AlertsView';
import MaintenanceView from './views/MaintenanceView';
import InventoryView from './views/InventoryView';
import ManufacturerView from './views/ManufacturerView';
import AIAssistantView from './views/AIAssistantView';
import AnalyticsView from './views/AnalyticsView';
import RbacView from './views/RbacView';
import NotificationCenterView from './views/NotificationCenterView';
import AuditLogView from './views/AuditLogView';
import SystemHealthView from './views/SystemHealthView';
import SettingsView from './views/SettingsView';

export default function App() {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [currentRole, setCurrentRole] = useState('floor_manager');
  const [selectedMachine, setSelectedMachine] = useState('fan');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isOpenMobile, setIsOpenMobile] = useState(false);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);

  const rolesMap = {
    admin: { title: 'System Administrator', desc: 'Full plant configuration, user management & security controls.' },
    floor_manager: { title: 'Plant Floor Manager', desc: 'Real-time telemetry, alert oversight & floor operational safety.' },
    maintenance_manager: { title: 'Maintenance Manager', desc: 'Work order dispatch, technician scheduling & manufacturer RFPs.' },
    technician: { title: 'Certified Tech Specialist', desc: 'Work order execution, repair feedback & post-repair verification.' }
  };

  // Fetch initial dashboard stats
  const fetchDashboardStats = async () => {
    try {
      const res = await fetch('/api/dashboard/stats');
      if (res.ok) {
        const data = await res.json();
        setDashboardStats(data);
      }
    } catch (e) {
      console.error("Fetch dashboard stats error:", e);
    }
  };

  useEffect(() => {
    fetchDashboardStats();
    const interval = setInterval(fetchDashboardStats, 10000);
    return () => clearInterval(interval);
  }, []);

  // WebSocket Connection Hook with robust auto-reconnect
  useEffect(() => {
    let ws = null;
    let reconnectTimeout = null;
    let isSubscribed = true;

    const connectWS = () => {
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsHost = window.location.host || '127.0.0.1:8000';
      const wsUrl = `${wsProtocol}//${wsHost}/ws/telemetry`;

      try {
        ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
          if (isSubscribed) setWsConnected(true);
        };
        
        ws.onclose = () => {
          if (isSubscribed) {
            setWsConnected(false);
            reconnectTimeout = setTimeout(connectWS, 3000);
          }
        };

        ws.onerror = () => {
          if (isSubscribed) {
            setWsConnected(false);
            ws?.close();
          }
        };
      } catch (e) {
        if (isSubscribed) {
          setWsConnected(false);
          reconnectTimeout = setTimeout(connectWS, 5000);
        }
      }
    };

    connectWS();

    return () => {
      isSubscribed = false;
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (ws) ws.close();
    };
  }, []);

  const handleSelectMachine = (mType) => {
    setSelectedMachine(mType.toLowerCase());
    setCurrentTab('machine-detail');
  };

  return (
    <div className="min-h-screen bg-dark-900 flex flex-col selection:bg-cyan-500 selection:text-dark-900">
      {/* Top Header Navbar */}
      <Navbar
        currentRole={currentRole}
        onRoleChange={setCurrentRole}
        wsConnected={wsConnected}
        alertCount={dashboardStats?.active_alerts || 0}
        toggleSidebar={() => setIsOpenMobile(!isOpenMobile)}
        rolesMap={rolesMap}
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Collapsible Sidebar */}
        <Sidebar
          currentTab={currentTab}
          onSelectTab={setCurrentTab}
          isCollapsed={isSidebarCollapsed}
          toggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
          isOpenMobile={isOpenMobile}
          closeMobile={() => setIsOpenMobile(false)}
        />

        {/* Main Content View Area */}
        <main className="flex-1 overflow-y-auto p-4 md:p-8 bg-gradient-to-b from-dark-900 via-dark-800/40 to-dark-900">
          {currentTab === 'dashboard' && (
            <DashboardView
              stats={dashboardStats}
              onSelectMachine={handleSelectMachine}
              onNavigate={setCurrentTab}
            />
          )}

          {currentTab === 'monitoring' && (
            <LiveMonitoringView
              selectedMachine={selectedMachine}
              onSelectMachine={setSelectedMachine}
              wsConnected={wsConnected}
            />
          )}

          {currentTab === 'machine-detail' && (
            <MachineDetailView
              selectedMachineId={selectedMachine}
              onSelectMachine={setSelectedMachine}
            />
          )}

          {currentTab === 'alerts' && (
            <AlertsView />
          )}

          {currentTab === 'notifications' && (
            <NotificationCenterView />
          )}

          {currentTab === 'maintenance' && (
            <MaintenanceView />
          )}

          {currentTab === 'inventory' && (
            <InventoryView />
          )}

          {currentTab === 'manufacturers' && (
            <ManufacturerView />
          )}

          {currentTab === 'audit-log' && (
            <AuditLogView />
          )}

          {currentTab === 'system-health' && (
            <SystemHealthView />
          )}

          {currentTab === 'ai-assistant' && (
            <AIAssistantView
              selectedMachine={selectedMachine}
            />
          )}

          {currentTab === 'analytics' && (
            <AnalyticsView />
          )}

          {currentTab === 'settings' && (
            <SettingsView />
          )}

          {currentTab === 'rbac' && (
            <RbacView
              currentRole={currentRole}
              onRoleChange={setCurrentRole}
              rolesMap={rolesMap}
            />
          )}
        </main>
      </div>
    </div>
  );
}
