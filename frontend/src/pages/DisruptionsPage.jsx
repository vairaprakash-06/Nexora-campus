import React, { useState } from 'react';
import { 
  AlertTriangle, PlusCircle, Zap, Clock, MapPin, 
  CheckCircle2, ArrowRight, ShieldAlert, Sparkles 
} from 'lucide-react';
import Badge from '../components/common/Badge';

export const DisruptionsPage = ({ 
  disruptions = [], 
  resources = [], 
  onCreateDisruption, 
  onTriggerRecovery, 
  onNavigateToRecovery,
  creating = false 
}) => {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    title: 'AI Lab 01 Equipment Failure',
    description: 'AI Lab 01 is unavailable on Monday from 09:00 AM to 11:00 AM because of equipment failure.',
    category: 'Equipment Failure',
    affected_resource_type: 'Room',
    affected_resource_id: 1, // default AI-LAB-01
    day_of_week: 'Monday',
    date: '2026-11-02',
    start_time: '09:00',
    end_time: '11:00',
    severity: 'High',
    trigger_recovery: true
  });

  const categories = [
    'Equipment Failure', 'Maintenance', 'Faculty Unavailable', 
    'Room Overflow', 'Power Outage', 'Emergency'
  ];

  const handlePreFillMainDemo = () => {
    const aiLab = resources.find(r => r.code === 'AI-LAB-01');
    setFormData({
      title: 'AI Lab 01 Equipment Failure',
      description: 'AI Lab 01 is unavailable on Monday from 09:00 AM to 11:00 AM because of equipment failure.',
      category: 'Equipment Failure',
      affected_resource_type: 'Room',
      affected_resource_id: aiLab ? aiLab.id : 1,
      day_of_week: 'Monday',
      date: '2026-11-02',
      start_time: '09:00',
      end_time: '11:00',
      severity: 'High',
      trigger_recovery: true
    });
    setShowForm(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    await onCreateDisruption(formData, formData.trigger_recovery);
    setShowForm(false);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header & Quick Action */}
      <div className="bg-campus-card/90 border border-campus-border rounded-2xl p-5 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
              Disruption Incident Center
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Report campus infrastructure failures and dispatch the autonomous multi-agent recovery swarm.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={handlePreFillMainDemo}
              className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-sky-500/20 to-indigo-500/20 border border-sky-500/30 text-sky-300 hover:text-white hover:bg-sky-500/30 text-xs font-bold flex items-center gap-1.5 transition"
            >
              <Sparkles className="w-3.5 h-3.5 text-sky-400" />
              <span>Pre-fill AI Lab 01 Scenario</span>
            </button>

            <button
              onClick={() => setShowForm(!showForm)}
              className="px-4 py-2.5 rounded-xl bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 transition"
            >
              <PlusCircle className="w-4 h-4" />
              <span>{showForm ? 'Close Incident Form' : 'Report New Incident'}</span>
            </button>
          </div>
        </div>

        {/* Disruption Submission Form */}
        {showForm && (
          <form onSubmit={handleSubmit} className="mt-6 pt-6 border-t border-slate-800 space-y-4 animate-fade-in">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-bold font-mono uppercase text-slate-400 mb-1 block">Incident Title</label>
                <input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
                />
              </div>

              <div>
                <label className="text-xs font-bold font-mono uppercase text-slate-400 mb-1 block">Category</label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
                >
                  {categories.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="text-xs font-bold font-mono uppercase text-slate-400 mb-1 block">Affected Room</label>
                <select
                  value={formData.affected_resource_id}
                  onChange={(e) => setFormData({ ...formData, affected_resource_id: parseInt(e.target.value) })}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
                >
                  {resources.map((r) => (
                    <option key={r.id} value={r.id}>{r.code} - {r.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-xs font-bold font-mono uppercase text-slate-400 mb-1 block">Day of Week</label>
                <select
                  value={formData.day_of_week}
                  onChange={(e) => setFormData({ ...formData, day_of_week: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
                >
                  {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'].map((d) => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-xs font-bold font-mono uppercase text-slate-400 mb-1 block">Time Window (Start - End)</label>
                <div className="flex items-center gap-2">
                  <input
                    type="time"
                    value={formData.start_time}
                    onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
                    className="w-1/2 bg-slate-900 border border-slate-800 rounded-xl px-2 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
                  />
                  <span className="text-slate-500">-</span>
                  <input
                    type="time"
                    value={formData.end_time}
                    onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                    className="w-1/2 bg-slate-900 border border-slate-800 rounded-xl px-2 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-bold font-mono uppercase text-slate-400 mb-1 block">Severity</label>
                <select
                  value={formData.severity}
                  onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Critical">Critical</option>
                </select>
              </div>
            </div>

            <div>
              <label className="text-xs font-bold font-mono uppercase text-slate-400 mb-1 block">Incident Description</label>
              <textarea
                rows={2}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
              />
            </div>

            <div className="flex items-center justify-between pt-2">
              <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.trigger_recovery}
                  onChange={(e) => setFormData({ ...formData, trigger_recovery: e.target.checked })}
                  className="rounded border-slate-800 text-sky-500 focus:ring-0 w-4 h-4"
                />
                <span className="font-semibold text-white">Immediately dispatch Agentic AI recovery orchestration</span>
              </label>

              <button
                type="submit"
                disabled={creating}
                className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-bold text-xs uppercase tracking-wider shadow-lg shadow-sky-500/20 disabled:opacity-50 transition"
              >
                {creating ? 'Orchestrating Agents...' : 'Submit Incident & Recover'}
              </button>
            </div>
          </form>
        )}
      </div>

      {/* Reported Incidents List */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 font-mono">
          Reported Campus Incidents ({disruptions.length})
        </h3>

        {disruptions.length === 0 ? (
          <div className="py-16 text-center bg-slate-900/40 border border-slate-800 rounded-2xl text-slate-500 text-xs">
            No active or historical disruptions recorded in campus logs.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {disruptions.map((d) => (
              <div
                key={d.id}
                className="bg-campus-card/95 border border-campus-border rounded-2xl p-5 shadow-lg flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div>
                      <span className="text-[10px] font-mono font-bold text-slate-400 uppercase">INCIDENT #{d.id} • {d.category}</span>
                      <h4 className="text-sm font-bold text-white tracking-wide mt-0.5">{d.title}</h4>
                    </div>

                    <Badge variant={
                      d.status === 'Resolved' ? 'success' :
                      d.status === 'Recovery Proposed' ? 'warning' : 'danger'
                    }>
                      {d.status}
                    </Badge>
                  </div>

                  <p className="text-xs text-slate-400 mt-2 line-clamp-2">{d.description}</p>

                  <div className="mt-3 grid grid-cols-2 gap-2 text-xs bg-slate-950/40 p-2.5 rounded-xl border border-slate-800/80">
                    <div>
                      <span className="text-[10px] uppercase font-mono text-slate-500 block">Affected Resource</span>
                      <span className="font-semibold text-white">{d.affected_resource_name}</span>
                    </div>

                    <div>
                      <span className="text-[10px] uppercase font-mono text-slate-500 block">Disruption Window</span>
                      <span className="font-mono text-sky-400">{d.day_of_week} {d.start_time}-{d.end_time}</span>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between">
                  <span className="text-[10px] text-slate-500 font-mono">
                    Reported by: {d.reported_by}
                  </span>

                  <button
                    onClick={() => onNavigateToRecovery(d.id)}
                    className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-sky-400 font-bold text-xs flex items-center gap-1 transition"
                  >
                    <span>Inspect Recovery</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DisruptionsPage;
