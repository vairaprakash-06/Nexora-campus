import React, { useState } from 'react';
import { Search, Bell, Shield, Sparkles, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';

export const Topbar = ({ aiMode = 'Deterministic Agent Mode', onRefresh, refreshing = false }) => {
  const [showNotifications, setShowNotifications] = useState(false);

  const notifications = [
    {
      id: 1,
      title: 'Disruption Incident Reported',
      desc: 'AI Lab 01 equipment failure on Monday 09:00 AM.',
      time: '10m ago',
      type: 'warning'
    },
    {
      id: 2,
      title: 'OR-Tools Optimization Solved',
      desc: 'Optimal recovery proposal formulated: Reassign to AI-LAB-02.',
      time: '9m ago',
      type: 'success'
    },
    {
      id: 3,
      title: 'Independent Validation Passed',
      desc: 'All 7 hard constraints verified with 100% compliance.',
      time: '8m ago',
      type: 'success'
    }
  ];

  return (
    <header className="h-16 bg-[#0D131F]/90 backdrop-blur-md border-b border-slate-800 sticky top-0 z-30 flex items-center justify-between px-6">
      {/* Search Bar */}
      <div className="flex items-center gap-3 w-96">
        <div className="relative w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search campus rooms, courses, faculty, cohorts..."
            className="w-full bg-slate-900/90 border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500/50 transition"
          />
        </div>
      </div>

      {/* Center status */}
      <div className="hidden md:flex items-center gap-3">
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs text-slate-300">
          <span className="w-2 h-2 rounded-full bg-sky-400"></span>
          <span className="font-mono text-[11px] text-slate-400">CAMPUS TERM:</span>
          <span className="font-semibold text-white">Fall 2026</span>
          <span className="text-slate-600">|</span>
          <span className="text-sky-300">Mon 09:00 AM</span>
        </div>

        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-950/60 border border-indigo-800/40 text-xs text-indigo-300">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span className="font-mono text-[11px] text-indigo-400">AI MODE:</span>
          <span className="font-semibold">{aiMode}</span>
        </div>
      </div>

      {/* Right controls */}
      <div className="flex items-center gap-3">
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={refreshing}
            title="Refresh Campus Data"
            className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800/80 border border-transparent hover:border-slate-700 transition"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin text-sky-400' : ''}`} />
          </button>
        )}

        {/* Notification Bell */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800/80 border border-transparent hover:border-slate-700 transition relative"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-sky-400"></span>
          </button>

          {/* Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-3 z-50 animate-fade-in">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800 px-2">
                <span className="text-xs font-bold text-white uppercase tracking-wider">System Alerts</span>
                <span className="text-[10px] text-sky-400 font-mono">3 New</span>
              </div>
              <div className="mt-2 space-y-1.5 max-h-64 overflow-y-auto">
                {notifications.map((n) => (
                  <div key={n.id} className="p-2.5 rounded-xl bg-slate-950/50 hover:bg-slate-800/50 border border-slate-800/60 text-xs transition">
                    <div className="flex items-center gap-1.5 font-semibold text-slate-200">
                      {n.type === 'warning' ? (
                        <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                      ) : (
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      )}
                      <span>{n.title}</span>
                    </div>
                    <p className="text-[11px] text-slate-400 mt-1">{n.desc}</p>
                    <span className="text-[10px] text-slate-500 font-mono mt-1 block">{n.time}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Admin Profile */}
        <div className="flex items-center gap-2.5 pl-2 border-l border-slate-800">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center text-xs font-bold text-white shadow-md">
            AD
          </div>
          <div className="hidden sm:block text-left">
            <p className="text-xs font-semibold text-white leading-tight">Admin Console</p>
            <p className="text-[10px] text-slate-400 font-mono">Academic Registrar</p>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Topbar;
