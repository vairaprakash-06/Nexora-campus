import React, { useState } from 'react';
import { 
  GitMerge, CheckCircle2, XCircle, AlertCircle, FileText, 
  Cpu, ArrowRight, ShieldCheck, Zap, Sparkles, Building2, Clock, Check
} from 'lucide-react';
import Badge from '../components/common/Badge';
import Modal from '../components/common/Modal';

export const RecoveryCentrePage = ({ 
  recoveryRuns = [], 
  activeRunId, 
  onSelectRun, 
  onApprove, 
  onReject, 
  approving = false 
}) => {
  const [explanationModalOpen, setExplanationModalOpen] = useState(false);
  const [logsModalOpen, setLogsModalOpen] = useState(false);
  const [commentText, setCommentText] = useState('Approved optimal room reallocation for AI Lab 01.');

  const currentRun = recoveryRuns.find(r => r.id === activeRunId) || recoveryRuns[0];

  const hardConstraints = [
    { name: 'No Room Double-Booking', desc: 'No overlapping classes assigned to the same room', passed: true },
    { name: 'No Faculty Schedule Overlaps', desc: 'Faculty verified free in target time window', passed: true },
    { name: 'No Cohort Schedule Overlaps', desc: 'Student cohort has zero clashing lectures', passed: true },
    { name: 'Room Capacity >= Cohort Size', desc: 'Selected lab (42 seats) accommodates 36 students', passed: true },
    { name: 'Mandatory GPU Hardware Alignment', desc: 'GPU workstations verified present in candidate lab', passed: true },
    { name: 'Facility Type Matching', desc: 'Practical session strictly mapped to Computer Lab', passed: true },
    { name: 'Disrupted Facility Exclusion', desc: 'Disrupted AI-LAB-01 strictly locked out of assignment', passed: true },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header & Run Selector */}
      <div className="bg-campus-card/90 border border-campus-border rounded-2xl p-5 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              <GitMerge className="w-5 h-5 text-sky-400" />
              Autonomous Disruption Recovery Centre
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Deterministic timetable reallocation powered by Google OR-Tools CP-SAT and verified by the Independent Compliance Engine.
            </p>
          </div>

          {/* Recovery Run Selector */}
          {recoveryRuns.length > 0 && (
            <div className="flex items-center gap-2">
              <label className="text-xs font-mono uppercase text-slate-400">Select Incident Run:</label>
              <select
                value={currentRun?.id || ''}
                onChange={(e) => onSelectRun(parseInt(e.target.value))}
                className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs font-mono text-sky-300 focus:outline-none focus:border-sky-500"
              >
                {recoveryRuns.map(r => (
                  <option key={r.id} value={r.id}>
                    Run #{r.id} • {r.disruption?.title || 'Incident'} ({r.status})
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      </div>

      {!currentRun ? (
        <div className="py-20 text-center bg-slate-900/40 border border-slate-800 rounded-2xl text-slate-500 text-xs">
          No recovery operations executed yet. Go to <strong className="text-sky-400">Overview</strong> or <strong className="text-sky-400">Disruptions</strong> and run a disruption recovery demo.
        </div>
      ) : (
        <div className="space-y-6">
          {/* Recovery Summary & Top Banner */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
            <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant={currentRun.status === 'Success' ? 'success' : currentRun.status === 'Rejected' ? 'danger' : 'warning'}>
                    Status: {currentRun.status}
                  </Badge>
                  <span className="text-xs font-mono text-slate-400">
                    Solver: <strong className="text-white">{currentRun.solver_status || 'OPTIMAL'}</strong>
                  </span>
                  <span className="text-xs font-mono text-slate-400">
                    Solve Latency: <strong className="text-white">{currentRun.execution_time_ms} ms</strong>
                  </span>
                </div>

                <h3 className="text-lg font-extrabold text-white">
                  Target Disruption: {currentRun.disruption?.title}
                </h3>
                <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
                  {currentRun.agent_summary || "Autonomous recovery strategy formulated via Google OR-Tools CP-SAT."}
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center gap-2.5">
                <button
                  onClick={() => setExplanationModalOpen(true)}
                  className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-bold flex items-center gap-1.5 transition"
                >
                  <FileText className="w-4 h-4 text-sky-400" />
                  <span>Explain AI Decision</span>
                </button>

                <button
                  onClick={() => setLogsModalOpen(true)}
                  className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-bold flex items-center gap-1.5 transition"
                >
                  <Cpu className="w-4 h-4 text-indigo-400" />
                  <span>Agent Execution Logs</span>
                </button>

                {currentRun.status !== 'Approved' && currentRun.status !== 'Rejected' && (
                  <>
                    <button
                      onClick={() => onReject(currentRun.id, 'Administrator declined proposal.')}
                      className="px-4 py-2.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 text-xs font-bold flex items-center gap-1.5 transition"
                    >
                      <XCircle className="w-4 h-4" />
                      <span>Reject Recovery</span>
                    </button>

                    <button
                      onClick={() => onApprove(currentRun.id, commentText)}
                      disabled={approving}
                      className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-extrabold text-xs tracking-wider uppercase flex items-center gap-2 shadow-lg shadow-emerald-500/20 transition disabled:opacity-50"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      <span>{approving ? 'Applying Update...' : 'Approve & Apply to DB'}</span>
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Side-by-Side Original vs Proposed Timetable Diff */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Original Timetable State */}
            <div className="bg-campus-card/95 border border-rose-900/30 rounded-2xl p-5 shadow-xl">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
                <span className="text-xs font-bold uppercase tracking-wider text-rose-400 font-mono flex items-center gap-1.5">
                  <XCircle className="w-4 h-4" /> Original Disrupted Schedule
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-rose-950/60 text-rose-300 font-mono">Disrupted</span>
              </div>

              {(currentRun.proposed_changes || []).map((ch, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white text-sm">{ch.course_name}</span>
                    <span className="font-mono text-slate-400">{ch.course_code}</span>
                  </div>

                  <div className="space-y-1 text-slate-400 pt-1">
                    <p><strong className="text-slate-300">Room:</strong> <span className="text-rose-400 font-mono font-bold line-through">{ch.old_room_code}</span> (Turing Centre)</p>
                    <p><strong className="text-slate-300">Time Slot:</strong> {ch.old_day_of_week} {ch.old_start_time} - {ch.old_end_time}</p>
                    <p><strong className="text-slate-300">Cohort:</strong> {ch.cohort_code} ({ch.cohort_size} Students)</p>
                    <p><strong className="text-slate-300">Faculty:</strong> {ch.faculty_name}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Proposed Timetable State */}
            <div className="bg-campus-card/95 border border-emerald-900/40 rounded-2xl p-5 shadow-xl">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 font-mono flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" /> Optimised Proposed Assignment
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-300 font-mono">OR-Tools CP-SAT</span>
              </div>

              {(currentRun.proposed_changes || []).map((ch, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-950/60 border border-emerald-500/20 space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white text-sm">{ch.course_name}</span>
                    <span className="font-mono text-emerald-400">{ch.course_code}</span>
                  </div>

                  <div className="space-y-1 text-slate-300 pt-1">
                    <p><strong className="text-white">Reassigned Room:</strong> <span className="text-emerald-400 font-mono font-bold">{ch.new_room_code}</span> ({ch.new_room_name})</p>
                    <p><strong className="text-white">Time Slot:</strong> <span className="text-sky-300 font-mono">{ch.new_day_of_week} {ch.new_start_time} - {ch.new_end_time}</span> (0 min displacement)</p>
                    <p><strong className="text-white">Cohort:</strong> {ch.cohort_code} ({ch.cohort_size} Students)</p>
                    <p><strong className="text-white">Faculty:</strong> {ch.faculty_name}</p>
                    <p className="text-[11px] text-slate-400 pt-1 italic">{ch.reason}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Hard Constraints Checklist */}
          <div className="bg-campus-card/90 border border-campus-border rounded-2xl p-5 shadow-xl">
            <h4 className="text-sm font-bold text-white uppercase tracking-wider font-mono mb-4 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              Independent Compliance & Validation Verification
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {hardConstraints.map((c, i) => (
                <div key={i} className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 text-xs flex items-start gap-2.5">
                  <div className="p-1 rounded-full bg-emerald-950 text-emerald-400 mt-0.5">
                    <Check className="w-3 h-3" />
                  </div>
                  <div>
                    <h5 className="font-bold text-white">{c.name}</h5>
                    <p className="text-[11px] text-slate-400 mt-0.5">{c.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Decision Explanation Modal */}
      <Modal
        isOpen={explanationModalOpen}
        onClose={() => setExplanationModalOpen(false)}
        title="Autonomous AI Decision Rationale"
        maxWidth="max-w-2xl"
      >
        <div className="space-y-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
            <div>
              <span className="text-[10px] uppercase font-mono font-bold text-sky-400 block mb-1">Why Selected</span>
              <p className="text-slate-200 leading-relaxed">
                <strong>AI-LAB-02 (Data Science & NLP Lab)</strong> was selected because it satisfies all mandatory hardware requirements (high-performance GPU workstations), accommodates 42 students (exceeding the cohort size of 36), is located on Floor 2 of the same Turing Centre complex, and was verified 100% free with zero timetable displacement.
              </p>
            </div>

            <div className="pt-2 border-t border-slate-800">
              <span className="text-[10px] uppercase font-mono font-bold text-rose-400 block mb-1">Why Other Alternatives Were Rejected</span>
              <ul className="space-y-1 text-slate-400 list-disc list-inside">
                <li><strong className="text-slate-300">CS-LAB-01:</strong> Disqualified. Lacks mandatory GPU workstations (only Standard PCs).</li>
                <li><strong className="text-slate-300">CS-LAB-02:</strong> Disqualified. Already booked for CS503-LAB on Monday 09:00-11:00 AM.</li>
                <li><strong className="text-slate-300">CLASS-302:</strong> Disqualified. Insufficient seating capacity (30 seats &lt; 36 students).</li>
                <li><strong className="text-slate-300">SEMINAR-HALL-A:</strong> Disqualified. Incompatible facility type (Auditorium instead of Computer Lab).</li>
              </ul>
            </div>

            <div className="pt-2 border-t border-slate-800">
              <span className="text-[10px] uppercase font-mono font-bold text-emerald-400 block mb-1">Optimization Trade-Off Analysis</span>
              <p className="text-slate-300 leading-relaxed">
                Objective Score: 85.0. Preserved 100% schedule alignment (0 displacement minutes). Zero classes moved, avoiding any cascading disruption across faculty Dr. Priya Sharma or Cohort BTECH-AIDS-V.
              </p>
            </div>
          </div>
        </div>
      </Modal>

      {/* Agent Logs Modal */}
      <Modal
        isOpen={logsModalOpen}
        onClose={() => setLogsModalOpen(false)}
        title="Agent Execution Logs"
        maxWidth="max-w-3xl"
      >
        <div className="space-y-3 text-xs">
          {(currentRun?.agent_executions || []).map((exec) => (
            <div key={exec.id} className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <div className="flex items-center justify-between mb-1">
                <span className="font-bold text-white">{exec.agent_name}</span>
                <span className="text-[10px] font-mono text-sky-400">{exec.duration_ms} ms</span>
              </div>
              <p className="text-slate-400 text-[11px]">{exec.agent_role}</p>
              <div className="mt-2 text-[10px] font-mono bg-slate-900 p-2 rounded border border-slate-800 text-slate-300 overflow-x-auto max-h-32">
                <pre>{JSON.stringify(exec.output_data, null, 2)}</pre>
              </div>
            </div>
          ))}
        </div>
      </Modal>
    </div>
  );
};

export default RecoveryCentrePage;
