import React from 'react';
import { 
  Building2, CheckCircle2, AlertTriangle, GitMerge, 
  Calendar, ShieldCheck, Zap, ArrowUpRight, Clock, Bot, Sparkles
} from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';
import StatCard from '../components/common/StatCard';
import Badge from '../components/common/Badge';

export const OverviewPage = ({ 
  dashboardData, 
  onNavigate, 
  onTriggerDemo, 
  loadingDemo 
}) => {
  if (!dashboardData) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-sky-400"></div>
      </div>
    );
  }

  const {
    total_rooms,
    available_rooms,
    occupied_rooms,
    active_disruptions,
    pending_approvals,
    scheduled_classes_today,
    recovery_success_rate,
    system_health,
    ai_mode,
    recent_incidents = [],
    recent_agent_activities = [],
    room_utilization = []
  } = dashboardData;

  const chartData = [
    { name: 'Turing Centre', count: 3, occupancy: 85 },
    { name: 'Ramanujan Block', count: 4, occupancy: 75 },
    { name: 'Aryabhata Block', count: 3, occupancy: 60 },
    { name: 'Sarabhai Tower', count: 1, occupancy: 50 },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Hero Banner with Demo Trigger */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950/70 to-slate-900 border border-slate-800 p-7 shadow-2xl">
        <div className="absolute right-0 top-0 -mt-10 -mr-10 w-80 h-80 rounded-full bg-sky-500/10 blur-3xl pointer-events-none"></div>
        <div className="relative z-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs font-semibold mb-3">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Autonomous Disruption Recovery Active</span>
            </div>
            <h2 className="text-2xl lg:text-3xl font-extrabold text-white tracking-tight leading-tight">
              Nexora Campus Intelligence Hub
            </h2>
            <p className="text-sm text-slate-300 mt-2 leading-relaxed">
              Coordinates seven specialised AI agents and the Google OR-Tools CP-SAT solver to autonomously 
              recover from unexpected laboratory breakdowns, classroom maintenance, and timetable conflicts.
            </p>
          </div>

          {/* Quick Main Demo Trigger Button */}
          <div className="flex flex-col sm:flex-row gap-3 w-full lg:w-auto">
            <button
              onClick={onTriggerDemo}
              disabled={loadingDemo}
              className="px-5 py-3 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-semibold text-xs tracking-wide uppercase flex items-center justify-center gap-2 shadow-lg shadow-sky-500/25 transition disabled:opacity-50"
            >
              <Zap className={`w-4 h-4 ${loadingDemo ? 'animate-bounce' : ''}`} />
              <span>{loadingDemo ? 'Orchestrating Agents...' : 'Run Main Demo: AI Lab 01 Disruption'}</span>
            </button>
            <button
              onClick={() => onNavigate('recovery')}
              className="px-4 py-3 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-200 font-semibold text-xs flex items-center justify-center gap-1.5 transition"
            >
              <span>Recovery Centre</span>
              <ArrowUpRight className="w-4 h-4 text-slate-400" />
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Campus Rooms"
          value={total_rooms}
          subtitle={`${available_rooms} Available • ${occupied_rooms} Occupied`}
          icon={Building2}
          variant="blue"
        />
        <StatCard
          title="Active Disruptions"
          value={active_disruptions}
          subtitle={active_disruptions > 0 ? "Recovery proposed & awaiting review" : "All facilities nominal"}
          icon={AlertTriangle}
          variant={active_disruptions > 0 ? "rose" : "emerald"}
        />
        <StatCard
          title="Pending Approvals"
          value={pending_approvals}
          subtitle="Validated recovery proposals"
          icon={GitMerge}
          variant={pending_approvals > 0 ? "amber" : "default"}
        />
        <StatCard
          title="Recovery Success Rate"
          value={`${recovery_success_rate}%`}
          subtitle="OR-Tools CP-SAT Optimised"
          icon={ShieldCheck}
          variant="emerald"
        />
      </div>

      {/* Two-Column Activity & Utilization */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Recent Disruptions & Quick Actions */}
        <div className="lg:col-span-2 space-y-6">
          {/* Recent Disruptions Table */}
          <div className="bg-campus-card/90 border border-campus-border rounded-2xl p-5 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  Recent Disruption Incidents
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">Campus operational alerts and recovery status</p>
              </div>
              <button
                onClick={() => onNavigate('disruptions')}
                className="text-xs font-semibold text-sky-400 hover:text-sky-300 flex items-center gap-1"
              >
                <span>View All</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>

            {recent_incidents.length === 0 ? (
              <div className="text-center py-8 text-slate-500 text-xs">
                No active disruption incidents reported. Click "Run Main Demo" to trigger a simulated equipment failure.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-900/60 text-slate-400 uppercase text-[10px] font-mono border-b border-slate-800">
                    <tr>
                      <th className="py-2.5 px-3">Incident</th>
                      <th className="py-2.5 px-3">Resource</th>
                      <th className="py-2.5 px-3">Time Window</th>
                      <th className="py-2.5 px-3">Severity</th>
                      <th className="py-2.5 px-3">Status</th>
                      <th className="py-2.5 px-3 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {recent_incidents.map((inc) => (
                      <tr key={inc.id} className="hover:bg-slate-800/40 transition">
                        <td className="py-3 px-3 font-semibold text-white">
                          {inc.title}
                        </td>
                        <td className="py-3 px-3 text-slate-300 font-mono">
                          {inc.affected_resource_name}
                        </td>
                        <td className="py-3 px-3 text-slate-400">
                          {inc.day_of_week} {inc.start_time}-{inc.end_time}
                        </td>
                        <td className="py-3 px-3">
                          <Badge variant={inc.severity === 'High' ? 'danger' : 'warning'}>
                            {inc.severity}
                          </Badge>
                        </td>
                        <td className="py-3 px-3">
                          <Badge variant={
                            inc.status === 'Resolved' ? 'success' :
                            inc.status === 'Recovery Proposed' ? 'warning' : 'accent'
                          }>
                            {inc.status}
                          </Badge>
                        </td>
                        <td className="py-3 px-3 text-right">
                          <button
                            onClick={() => onNavigate('recovery')}
                            className="px-2.5 py-1 rounded-lg bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 font-semibold text-[11px] transition"
                          >
                            Inspect
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Room Utilization Bar Chart */}
          <div className="bg-campus-card/90 border border-campus-border rounded-2xl p-5 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-sky-400" />
                  Building Capacity Utilization
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">Estimated peak occupancy rate across campus complexes</p>
              </div>
            </div>

            <div className="h-60 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <XAxis dataKey="name" stroke="#64748B" fontSize={11} tickLine={false} />
                  <YAxis stroke="#64748B" fontSize={11} tickLine={false} domain={[0, 100]} unit="%" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '12px' }}
                    labelStyle={{ color: '#F8FAFC', fontWeight: 'bold' }}
                  />
                  <Bar dataKey="occupancy" radius={[6, 6, 0, 0]}>
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={index === 0 ? '#38BDF8' : '#6366F1'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Right Column: Recent Multi-Agent Activities */}
        <div className="space-y-6">
          <div className="bg-campus-card/90 border border-campus-border rounded-2xl p-5 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                  <Bot className="w-4 h-4 text-indigo-400" />
                  Live Agent Operations
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">Recent agent workflow records</p>
              </div>
              <button
                onClick={() => onNavigate('agents')}
                className="text-xs font-semibold text-sky-400 hover:text-sky-300"
              >
                Agent Centre →
              </button>
            </div>

            <div className="space-y-3">
              {recent_agent_activities.slice(0, 5).map((act) => (
                <div key={act.id} className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-white">{act.agent_name}</span>
                    <Badge variant={act.status === 'Completed' ? 'success' : 'accent'} size="sm">
                      {act.status}
                    </Badge>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">
                    {act.output_data?.recommendation || act.output_data?.analysis_narrative || act.output_data?.triage_assessment || act.agent_role}
                  </p>
                  <div className="mt-2 flex items-center justify-between text-[10px] text-slate-500 font-mono">
                    <span>Duration: {act.duration_ms}ms</span>
                    <span>Tools: {(act.tools_used || []).length}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OverviewPage;
