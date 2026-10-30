import React from 'react';
import { 
  LayoutDashboard, Calendar, Building2, AlertTriangle, 
  Bot, GitMerge, BarChart3, Settings, ShieldCheck, Sparkles
} from 'lucide-react';

export const Sidebar = ({ activeTab, setActiveTab, pendingApprovalsCount = 0, activeDisruptionsCount = 0 }) => {
  const menuItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'timetable', label: 'Timetable', icon: Calendar },
    { id: 'resources', label: 'Resources', icon: Building2 },
    { 
      id: 'disruptions', 
      label: 'Disruptions', 
      icon: AlertTriangle,
      badge: activeDisruptionsCount > 0 ? activeDisruptionsCount : null,
      badgeVariant: 'danger'
    },
    { id: 'agents', label: 'Agent Centre', icon: Bot, isAi: true },
    { 
      id: 'recovery', 
      label: 'Recovery Centre', 
      icon: GitMerge,
      badge: pendingApprovalsCount > 0 ? pendingApprovalsCount : null,
      badgeVariant: 'warning'
    },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-[#0D131F] border-r border-slate-800 flex flex-col h-screen fixed left-0 top-0 z-40 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80 flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
          <ShieldCheck className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <h1 className="text-base font-extrabold tracking-wider text-white">NEXORA</h1>
            <span className="text-xs px-1.5 py-0.5 rounded bg-sky-500/20 text-sky-400 font-mono font-semibold">AI</span>
          </div>
          <p className="text-[11px] text-slate-400 tracking-wider uppercase font-medium">Smart Campus Platform</p>
        </div>
      </div>

      {/* Navigation links */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-slate-500 font-mono">
          Campus Operations
        </div>

        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all-200 group ${
                isActive
                  ? 'bg-gradient-to-r from-sky-500/20 to-indigo-500/10 text-sky-300 border border-sky-500/30 shadow-md shadow-sky-500/5'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 transition ${isActive ? 'text-sky-400' : 'text-slate-500 group-hover:text-slate-300'}`} />
                <span>{item.label}</span>
                {item.isAi && (
                  <Sparkles className="w-3 h-3 text-indigo-400 animate-pulse" />
                )}
              </div>

              {item.badge && (
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold font-mono ${
                  item.badgeVariant === 'danger'
                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                    : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                }`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Campus System Engine Card */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/40">
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-300 mb-1">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
              Orchestrator
            </span>
            <span className="text-[10px] font-mono text-sky-400">v1.0-PROD</span>
          </div>
          <p className="text-[11px] text-slate-400">LangGraph 7-Agent + Google OR-Tools CP-SAT</p>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
