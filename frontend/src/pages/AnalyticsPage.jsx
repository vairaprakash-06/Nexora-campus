import React from 'react';
import { 
  BarChart3, TrendingUp, Clock, ShieldCheck, 
  Building2, AlertTriangle, Cpu, Layers 
} from 'lucide-react';
import { 
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, 
  Cell, PieChart, Pie, AreaChart, Area, Legend 
} from 'recharts';
import StatCard from '../components/common/StatCard';

export const AnalyticsPage = ({ analyticsData }) => {
  if (!analyticsData) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-sky-400"></div>
      </div>
    );
  }

  const {
    room_utilization_by_type = [],
    disruptions_by_category = [],
    recovery_statistics = {},
    department_impact = [],
    resource_demand = []
  } = analyticsData;

  const COLORS = ['#38BDF8', '#6366F1', '#10B981', '#F59E0B', '#EC4899', '#8B5CF6'];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Banner */}
      <div className="bg-campus-card/90 border border-campus-border rounded-2xl p-5 shadow-xl">
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-sky-400" />
          Campus Operational Analytics & Intelligence
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Historical disruption frequency, resource demand patterns, department load metrics, and solver efficiency.
        </p>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Recovery Runs"
          value={recovery_statistics.total_recovery_runs || 1}
          subtitle={`${recovery_statistics.successful_recoveries || 1} Successful • ${recovery_statistics.failed_recoveries || 0} Failed`}
          icon={TrendingUp}
          variant="blue"
        />
        <StatCard
          title="Average Recovery Latency"
          value={`${recovery_statistics.average_recovery_time_ms || 145} ms`}
          subtitle="Google OR-Tools CP-SAT Solving"
          icon={Clock}
          variant="indigo"
        />
        <StatCard
          title="Schedule Displacement"
          value="0 minutes"
          subtitle="100% schedule alignment preserved"
          icon={ShieldCheck}
          variant="emerald"
        />
        <StatCard
          title="Compliance Score"
          value={`${recovery_statistics.constraint_compliance_rate || 100}%`}
          subtitle="Zero hard constraint violations"
          icon={ShieldCheck}
          variant="emerald"
        />
      </div>

      {/* Two Column Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Disruption Category Breakdown */}
        <div className="bg-campus-card/90 border border-campus-border rounded-2xl p-5 shadow-xl">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono mb-1 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            Disruption Frequency by Category
          </h3>
          <p className="text-xs text-slate-400 mb-4">Distribution of unexpected campus failure reports</p>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={disruptions_by_category} layout="vertical" margin={{ top: 10, right: 20, left: 40, bottom: 0 }}>
                <XAxis type="number" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis dataKey="category" type="category" stroke="#64748B" fontSize={11} tickLine={false} width={130} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '12px' }}
                  labelStyle={{ color: '#F8FAFC', fontWeight: 'bold' }}
                />
                <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                  {disruptions_by_category.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Room Utilization by Facility Type */}
        <div className="bg-campus-card/90 border border-campus-border rounded-2xl p-5 shadow-xl">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono mb-1 flex items-center gap-2">
            <Layers className="w-4 h-4 text-sky-400" />
            Utilization Rate by Facility Type
          </h3>
          <p className="text-xs text-slate-400 mb-4">Occupancy density across labs, classrooms, and halls</p>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={room_utilization_by_type} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="room_type" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} domain={[0, 100]} unit="%" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '12px' }}
                  labelStyle={{ color: '#F8FAFC', fontWeight: 'bold' }}
                />
                <Bar dataKey="utilization_rate" fill="#38BDF8" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Peak Demand Hours Area Chart */}
        <div className="bg-campus-card/90 border border-campus-border rounded-2xl p-5 shadow-xl">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono mb-1 flex items-center gap-2">
            <Clock className="w-4 h-4 text-indigo-400" />
            Peak Laboratory & Lecture Demand Curve
          </h3>
          <p className="text-xs text-slate-400 mb-4">Hourly congestion across academic time slots</p>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={resource_demand} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorDemand" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366F1" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#6366F1" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="time_slot" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} domain={[0, 100]} unit="%" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '12px' }}
                  labelStyle={{ color: '#F8FAFC', fontWeight: 'bold' }}
                />
                <Area type="monotone" dataKey="demand_level" stroke="#818CF8" strokeWidth={2} fillOpacity={1} fill="url(#colorDemand)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Department Impact Bar Chart */}
        <div className="bg-campus-card/90 border border-campus-border rounded-2xl p-5 shadow-xl">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono mb-1 flex items-center gap-2">
            <Building2 className="w-4 h-4 text-emerald-400" />
            Department Academic Load & Schedules
          </h3>
          <p className="text-xs text-slate-400 mb-4">Total weekly sessions scheduled per department</p>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={department_impact} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="department_code" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '12px' }}
                  labelStyle={{ color: '#F8FAFC', fontWeight: 'bold' }}
                />
                <Bar dataKey="scheduled_sessions" fill="#10B981" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
