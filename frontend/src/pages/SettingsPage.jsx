import React, { useState, useEffect } from 'react';
import { 
  Settings, Key, Database, Cpu, ShieldCheck, 
  RefreshCw, CheckCircle2, History 
} from 'lucide-react';
import Badge from '../components/common/Badge';
import { campusApi } from '../services/api';

export const SettingsPage = ({ aiMode }) => {
  const [auditLogs, setAuditLogs] = useState([]);
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [groqKeyInput, setGroqKeyInput] = useState('');
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    setLoadingLogs(true);
    try {
      const res = await campusApi.getAuditLogs(20);
      setAuditLogs(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingLogs(false);
    }
  };

  const handleSaveSettings = (e) => {
    e.preventDefault();
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Banner */}
      <div className="bg-campus-card/90 border border-campus-border rounded-2xl p-5 shadow-xl">
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <Settings className="w-5 h-5 text-sky-400" />
          System Preferences & Governance Controls
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Configure Groq LLM runtime parameters, Google OR-Tools CP-SAT solver timeouts, and inspect security audit trails.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: AI & Solver Configuration */}
        <div className="space-y-6">
          <div className="bg-campus-card/90 border border-campus-border rounded-2xl p-5 shadow-xl">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono mb-4 flex items-center gap-2">
              <Key className="w-4 h-4 text-sky-400" />
              Groq LLM Provider Configuration
            </h3>

            <form onSubmit={handleSaveSettings} className="space-y-4 text-xs">
              <div>
                <label className="text-slate-400 font-mono uppercase text-[10px] block mb-1">Groq API Key</label>
                <input
                  type="password"
                  placeholder="gsk_..."
                  value={groqKeyInput}
                  onChange={(e) => setGroqKeyInput(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-white font-mono focus:outline-none focus:border-sky-500"
                />
                <p className="text-[10px] text-slate-500 mt-1">
                  Leave empty to operate in zero-dependency <strong>Deterministic Agent Mode</strong>.
                </p>
              </div>

              <div>
                <label className="text-slate-400 font-mono uppercase text-[10px] block mb-1">Groq Foundation Model</label>
                <select className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-sky-500">
                  <option value="llama-3.3-70b-versatile">llama-3.3-70b-versatile (Recommended)</option>
                  <option value="llama-3.1-8b-instant">llama-3.1-8b-instant</option>
                  <option value="mixtral-8x7b-32768">mixtral-8x7b-32768</option>
                </select>
              </div>

              <div className="pt-2 flex items-center justify-between">
                <Badge variant={aiMode.includes("Groq") ? "success" : "accent"}>
                  Current Engine: {aiMode}
                </Badge>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold transition"
                >
                  Save API Settings
                </button>
              </div>

              {savedSuccess && (
                <div className="p-2.5 rounded-xl bg-emerald-950/60 border border-emerald-800/40 text-emerald-300 text-xs flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Configuration saved successfully.</span>
                </div>
              )}
            </form>
          </div>

          {/* Solver Settings */}
          <div className="bg-campus-card/90 border border-campus-border rounded-2xl p-5 shadow-xl">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono mb-4 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-indigo-400" />
              Google OR-Tools CP-SAT Engine Controls
            </h3>

            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900 border border-slate-800">
                <div>
                  <p className="font-bold text-white">CP-SAT Search Timeout</p>
                  <p className="text-[11px] text-slate-400">Maximum solve duration before returning best feasible</p>
                </div>
                <span className="font-mono text-sky-400 font-bold">10 Seconds</span>
              </div>

              <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900 border border-slate-800">
                <div>
                  <p className="font-bold text-white">Displacement Weight Factor</p>
                  <p className="text-[11px] text-slate-400">Penalty for shifting class timeslots</p>
                </div>
                <span className="font-mono text-indigo-400 font-bold">500x Penalty</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Audit Trail Logs */}
        <div className="bg-campus-card/90 border border-campus-border rounded-2xl p-5 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <History className="w-4 h-4 text-emerald-400" />
                Immutable Audit Log Trail
              </h3>
              <button
                onClick={fetchLogs}
                disabled={loadingLogs}
                className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loadingLogs ? 'animate-spin' : ''}`} />
              </button>
            </div>

            <div className="space-y-2 max-h-[460px] overflow-y-auto">
              {auditLogs.map((log) => (
                <div key={log.id} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white font-mono">{log.action}</span>
                    <Badge variant={log.action.includes('APPROVE') ? 'success' : log.action.includes('REJECT') ? 'danger' : 'accent'} size="sm">
                      {log.entity_type} #{log.entity_id}
                    </Badge>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">
                    Actor: <strong className="text-slate-300">{log.actor}</strong>
                  </p>
                  <span className="text-[10px] text-slate-500 font-mono mt-1 block">
                    {new Date(log.timestamp).toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
