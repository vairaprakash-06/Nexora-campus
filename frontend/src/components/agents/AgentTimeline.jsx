import React from 'react';
import { 
  ArrowRight, CheckCircle2, Clock, AlertCircle, RefreshCw, 
  Sparkles, ShieldCheck, Cpu, Database, Calendar, FileText, CheckCheck
} from 'lucide-react';

export const AgentTimeline = ({ executions = [], currentStatus = 'Idle' }) => {
  const steps = [
    { key: 'supervisor', name: '1. Supervisor', role: 'Triage & Delegation', icon: Sparkles },
    { key: 'disruption', name: '2. Disruption Analysis', role: 'Impact Blast Radius', icon: AlertCircle },
    { key: 'resource', name: '3. Resource Intel', role: 'Hardware & Cap Filter', icon: Database },
    { key: 'timetable', name: '4. Timetable Coord', role: 'Calendar Sync', icon: Calendar },
    { key: 'optimisation', name: '5. OR-Tools Solver', role: 'CP-SAT Optimization', icon: Cpu },
    { key: 'validation', name: '6. Validation Gate', role: 'Constraint Compliance', icon: ShieldCheck },
    { key: 'explanation', name: '7. Explanation', role: 'Rationale Synthesis', icon: FileText },
    { key: 'approval', name: '8. Admin Approval', role: 'Database Commit', icon: CheckCheck }
  ];

  // Helper to match executions by step
  const getExecForStep = (stepKey) => {
    return executions.find(e => 
      e.agent_name.toLowerCase().includes(stepKey) ||
      (stepKey === 'optimisation' && e.agent_name.toLowerCase().includes('optimisation')) ||
      (stepKey === 'resource' && e.agent_name.toLowerCase().includes('resource')) ||
      (stepKey === 'disruption' && e.agent_name.toLowerCase().includes('disruption')) ||
      (stepKey === 'timetable' && e.agent_name.toLowerCase().includes('timetable'))
    );
  };

  return (
    <div className="bg-campus-card/90 border border-campus-border rounded-2xl p-5 shadow-xl mb-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-white tracking-wide uppercase flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-sky-400"></span>
            LangGraph Multi-Agent Orchestration Workflow
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time agent progression graph across autonomous planning, deterministic CP-SAT solving, and independent validation.
          </p>
        </div>

        <span className="text-xs font-mono px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-sky-300">
          State: {currentStatus}
        </span>
      </div>

      {/* Horizontal timeline */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-2">
        {steps.map((step, idx) => {
          const exec = getExecForStep(step.key);
          const isDone = exec?.status === 'Completed' || (step.key === 'approval' && executions.length >= 7);
          const isRunning = exec?.status === 'Running';
          const isFailed = exec?.status === 'Failed';
          const Icon = step.icon;

          let cardColor = 'bg-slate-900/60 border-slate-800 text-slate-500';
          if (isDone) {
            cardColor = 'bg-slate-900 border-emerald-500/40 text-emerald-300';
          } else if (isRunning) {
            cardColor = 'bg-sky-950/60 border-sky-500 text-sky-300 animate-pulse';
          } else if (isFailed) {
            cardColor = 'bg-rose-950/60 border-rose-500 text-rose-300';
          }

          return (
            <div
              key={step.key}
              className={`border rounded-xl p-3 flex flex-col justify-between transition-all ${cardColor}`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className={`p-1.5 rounded-lg ${isDone ? 'bg-emerald-950/80 text-emerald-400' : 'bg-slate-800 text-slate-400'}`}>
                    <Icon className="w-3.5 h-3.5" />
                  </div>
                  {isDone ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : isRunning ? (
                    <RefreshCw className="w-4 h-4 text-sky-400 animate-spin" />
                  ) : isFailed ? (
                    <AlertCircle className="w-4 h-4 text-rose-400" />
                  ) : (
                    <Clock className="w-3.5 h-3.5 text-slate-600" />
                  )}
                </div>

                <p className="text-xs font-bold truncate leading-tight text-white">{step.name}</p>
                <p className="text-[10px] text-slate-400 truncate mt-0.5">{step.role}</p>
              </div>

              {exec?.duration_ms > 0 && (
                <div className="mt-2 pt-1.5 border-t border-slate-800 text-[10px] font-mono text-slate-400">
                  {exec.duration_ms}ms
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default AgentTimeline;
