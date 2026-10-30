import React, { useState } from 'react';
import { Bot, Sparkles, Terminal, ShieldCheck, Cpu, RefreshCw, FileText } from 'lucide-react';
import AgentCard from '../components/agents/AgentCard';
import AgentTimeline from '../components/agents/AgentTimeline';
import Modal from '../components/common/Modal';

export const AgentCentrePage = ({ agentsData, executions = [], onRefresh, refreshing = false }) => {
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [inspectModalOpen, setInspectModalOpen] = useState(false);

  const agents = agentsData?.agents || [];
  const llmModel = agentsData?.llm_model || 'llama-3.3-70b-versatile';
  const llmEnabled = agentsData?.llm_enabled || false;

  const handleInspect = (agent) => {
    setSelectedAgent(agent);
    setInspectModalOpen(true);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Banner */}
      <div className="bg-campus-card/90 border border-campus-border rounded-2xl p-5 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              <Bot className="w-5 h-5 text-indigo-400" />
              Specialised Multi-Agent Orchestration Swarm
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              7 specialized agents coordinated via LangGraph StateGraph, combining Groq structured LLMs with deterministic Google OR-Tools CP-SAT.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 font-mono">
              Provider: <strong className="text-sky-400">Groq ({llmModel})</strong>
            </span>
            <span className="text-xs px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 font-mono">
              Status: <strong className={llmEnabled ? "text-emerald-400" : "text-amber-400"}>
                {llmEnabled ? "Online" : "Deterministic Fallback"}
              </strong>
            </span>
          </div>
        </div>
      </div>

      {/* Visual LangGraph Workflow Timeline */}
      <AgentTimeline executions={executions} currentStatus={executions.length > 0 ? 'Active Workflow' : 'Nominal'} />

      {/* Agents Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {agents.map((agent) => (
          <AgentCard
            key={agent.id}
            agent={agent}
            onInspect={handleInspect}
          />
        ))}
      </div>

      {/* Agent Execution Payload Inspection Modal */}
      <Modal
        isOpen={inspectModalOpen}
        onClose={() => setInspectModalOpen(false)}
        title={selectedAgent ? `Execution Record: ${selectedAgent.name}` : 'Agent Inspection'}
        maxWidth="max-w-3xl"
      >
        {selectedAgent && (
          <div className="space-y-4 text-xs">
            <div className="grid grid-cols-3 gap-3 p-3.5 rounded-xl bg-slate-950 border border-slate-800 font-mono">
              <div>
                <span className="text-[10px] uppercase text-slate-500 block">Agent Status</span>
                <span className="text-emerald-400 font-bold">{selectedAgent.current_status}</span>
              </div>
              <div>
                <span className="text-[10px] uppercase text-slate-500 block">Duration</span>
                <span className="text-sky-400 font-bold">{selectedAgent.last_duration_ms} ms</span>
              </div>
              <div>
                <span className="text-[10px] uppercase text-slate-500 block">Engine</span>
                <span className="text-slate-300 font-bold">{selectedAgent.engine}</span>
              </div>
            </div>

            <div>
              <h5 className="font-mono text-[11px] uppercase font-bold text-slate-400 mb-1 flex items-center gap-1.5">
                <Terminal className="w-3.5 h-3.5 text-sky-400" /> Latest Output JSON Payload
              </h5>
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 overflow-x-auto max-h-72">
                <pre className="font-mono text-[11px] text-sky-300 leading-relaxed">
                  {selectedAgent.latest_output ? JSON.stringify(selectedAgent.latest_output, null, 2) : '// No execution record recorded yet for this agent.'}
                </pre>
              </div>
            </div>

            <div>
              <h5 className="font-mono text-[11px] uppercase font-bold text-slate-400 mb-1">
                Tools & Capabilities
              </h5>
              <div className="flex flex-wrap gap-1.5">
                {(selectedAgent.latest_tools_used || selectedAgent.tools).map((t, idx) => (
                  <span key={idx} className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 font-mono text-slate-300">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default AgentCentrePage;
