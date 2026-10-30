import React, { useState } from 'react';
import { 
  Bot, Clock, CheckCircle2, AlertCircle, RefreshCw, 
  ChevronRight, Wrench, Sparkles, Terminal, FileText 
} from 'lucide-react';
import Badge from '../common/Badge';

export const AgentCard = ({ agent, onInspect }) => {
  const statusVariants = {
    Completed: 'success',
    Running: 'accent',
    Waiting: 'default',
    Failed: 'danger',
    Retrying: 'warning',
    Escalated: 'danger',
    Idle: 'default'
  };

  const statusIcons = {
    Completed: CheckCircle2,
    Running: RefreshCw,
    Waiting: Clock,
    Failed: AlertCircle,
    Retrying: RefreshCw,
    Escalated: AlertCircle,
    Idle: Clock
  };

  const StatusIcon = statusIcons[agent.current_status] || Clock;

  return (
    <div className="bg-campus-card/95 border border-campus-border hover:border-slate-700/80 rounded-2xl p-5 shadow-lg transition-all-200 flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-slate-800/90 border border-slate-700/60 flex items-center justify-center text-sky-400">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-white tracking-wide">{agent.name}</h4>
              <p className="text-[11px] text-slate-400 mt-0.5">{agent.role}</p>
            </div>
          </div>

          <Badge variant={statusVariants[agent.current_status] || 'default'}>
            <StatusIcon className={`w-3 h-3 ${agent.current_status === 'Running' ? 'animate-spin' : ''}`} />
            <span>{agent.current_status}</span>
          </Badge>
        </div>

        {/* Engine and Latency Tag */}
        <div className="flex items-center gap-2 mb-3">
          <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 border border-slate-700/70 text-slate-300 font-mono">
            {agent.engine}
          </span>
          {agent.last_duration_ms > 0 && (
            <span className="text-[10px] text-slate-400 font-mono flex items-center gap-1">
              <Clock className="w-3 h-3 text-slate-500" />
              {agent.last_duration_ms} ms
            </span>
          )}
        </div>

        {/* Responsibilities list */}
        <div className="space-y-1 mb-4 text-xs text-slate-400">
          {agent.responsibilities.slice(0, 3).map((r, i) => (
            <div key={i} className="flex items-start gap-1.5">
              <span className="text-sky-500 font-bold">•</span>
              <span>{r}</span>
            </div>
          ))}
        </div>

        {/* Tools Used */}
        <div className="mb-4">
          <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500 font-mono mb-1.5 flex items-center gap-1">
            <Wrench className="w-3 h-3" /> Tools Invoked
          </p>
          <div className="flex flex-wrap gap-1">
            {(agent.latest_tools_used || agent.tools).map((t, idx) => (
              <span key={idx} className="text-[10px] px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-slate-300 font-mono">
                {t}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Action / Inspect Button */}
      <button
        onClick={() => onInspect(agent)}
        className="w-full mt-2 py-2 px-3 rounded-xl bg-slate-800/80 hover:bg-slate-700 border border-slate-700/70 text-xs font-semibold text-slate-200 flex items-center justify-center gap-1.5 transition"
      >
        <Terminal className="w-3.5 h-3.5 text-sky-400" />
        <span>Inspect Execution Payload</span>
        <ChevronRight className="w-3.5 h-3.5 ml-auto text-slate-400" />
      </button>
    </div>
  );
};

export default AgentCard;
