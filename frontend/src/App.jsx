import React, { useState, useEffect } from 'react';
import Sidebar from './components/layout/Sidebar';
import Topbar from './components/layout/Topbar';
import OverviewPage from './pages/OverviewPage';
import TimetablePage from './pages/TimetablePage';
import ResourcesPage from './pages/ResourcesPage';
import DisruptionsPage from './pages/DisruptionsPage';
import AgentCentrePage from './pages/AgentCentrePage';
import RecoveryCentrePage from './pages/RecoveryCentrePage';
import AnalyticsPage from './pages/AnalyticsPage';
import SettingsPage from './pages/SettingsPage';
import { campusApi } from './services/api';

export function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [loadingDemo, setLoadingDemo] = useState(false);
  const [approving, setApproving] = useState(false);

  // Core Data States
  const [dashboardData, setDashboardData] = useState(null);
  const [resources, setResources] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [scheduleFilters, setScheduleFilters] = useState({});
  const [disruptions, setDisruptions] = useState([]);
  const [agentsData, setAgentsData] = useState(null);
  const [recoveryRuns, setRecoveryRuns] = useState([]);
  const [activeRecoveryRunId, setActiveRecoveryRunId] = useState(null);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [latestExecutions, setLatestExecutions] = useState([]);

  // Toast Notification
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  // Initial Data Fetch
  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    setRefreshing(true);
    try {
      const [dashRes, resRes, schRes, filtRes, disRes, agRes, recRes, anaRes] = await Promise.all([
        campusApi.getDashboard().catch(() => ({ data: null })),
        campusApi.getResources().catch(() => ({ data: [] })),
        campusApi.getSchedules().catch(() => ({ data: [] })),
        campusApi.getScheduleFilters().catch(() => ({ data: {} })),
        campusApi.getDisruptions().catch(() => ({ data: [] })),
        campusApi.getAgentsStatus().catch(() => ({ data: null })),
        campusApi.getRecoveryRuns().catch(() => ({ data: [] })),
        campusApi.getAnalytics().catch(() => ({ data: null })),
      ]);

      if (dashRes.data) setDashboardData(dashRes.data);
      if (resRes.data) setResources(resRes.data);
      if (schRes.data) setSchedules(schRes.data);
      if (filtRes.data) setScheduleFilters(filtRes.data);
      if (disRes.data) setDisruptions(disRes.data);
      if (agRes.data) setAgentsData(agRes.data);
      if (recRes.data) {
        setRecoveryRuns(recRes.data);
        if (recRes.data.length > 0 && !activeRecoveryRunId) {
          setActiveRecoveryRunId(recRes.data[0].id);
          if (recRes.data[0].agent_executions) {
            setLatestExecutions(recRes.data[0].agent_executions);
          }
        }
      }
      if (anaRes.data) setAnalyticsData(anaRes.data);
    } catch (err) {
      console.error('Failed to load campus platform data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Main Demo Scenario Trigger: AI Lab 01 unavailable Monday 09:00 - 11:00 AM
  const handleTriggerMainDemo = async () => {
    setLoadingDemo(true);
    try {
      const aiLab = resources.find(r => r.code === 'AI-LAB-01');
      const payload = {
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
        reported_by: 'Campus Administrator'
      };

      const res = await campusApi.createDisruption(payload, true);
      showToast('Disruption created. 7-Agent LangGraph workflow and OR-Tools optimization completed!', 'success');
      
      // Refresh recovery runs and navigate
      await fetchAllData();
      setActiveTab('recovery');
    } catch (err) {
      console.error(err);
      showToast('Failed to trigger demonstration workflow.', 'danger');
    } finally {
      setLoadingDemo(false);
    }
  };

  // Create Custom Disruption
  const handleCreateDisruption = async (formData, triggerRecovery) => {
    try {
      await campusApi.createDisruption(formData, triggerRecovery);
      showToast('Disruption incident logged successfully.', 'success');
      await fetchAllData();
      if (triggerRecovery) {
        setActiveTab('recovery');
      }
    } catch (err) {
      console.error(err);
      showToast('Failed to create disruption incident.', 'danger');
    }
  };

  // Update Room
  const handleUpdateResource = async (roomId, data) => {
    try {
      await campusApi.updateResource(roomId, data);
      showToast('Room resource updated successfully.', 'success');
      await fetchAllData();
    } catch (err) {
      console.error(err);
      showToast('Failed to update room resource.', 'danger');
    }
  };

  // Approve Recovery
  const handleApproveRecovery = async (runId, comments) => {
    setApproving(true);
    try {
      const res = await campusApi.approveRecovery(runId, comments, 'Dr. Administrator');
      showToast('Recovery approved! Database transactionally updated and revalidated.', 'success');
      await fetchAllData();
      setActiveTab('timetable'); // Navigate to timetable to inspect the reallocated room!
    } catch (err) {
      console.error(err);
      showToast(err.response?.data?.detail || 'Approval failed.', 'danger');
    } finally {
      setApproving(false);
    }
  };

  // Reject Recovery
  const handleRejectRecovery = async (runId, comments) => {
    try {
      await campusApi.rejectRecovery(runId, comments, 'Dr. Administrator');
      showToast('Recovery rejected. Timetable preserved unchanged.', 'warning');
      await fetchAllData();
    } catch (err) {
      console.error(err);
      showToast('Failed to reject recovery proposal.', 'danger');
    }
  };

  const handleNavigateToRecovery = (disruptionId) => {
    const run = recoveryRuns.find(r => r.disruption_id === disruptionId);
    if (run) {
      setActiveRecoveryRunId(run.id);
    }
    setActiveTab('recovery');
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-[#0B0F17] text-white">
        <div className="w-12 h-12 rounded-full border-4 border-sky-400 border-t-transparent animate-spin mb-4"></div>
        <h2 className="text-xl font-bold tracking-wider">NEXORA CAMPUS</h2>
        <p className="text-xs text-slate-400 font-mono mt-1">Initializing Autonomous Agentic Platform...</p>
      </div>
    );
  }

  const aiModeText = dashboardData?.ai_mode || 'Hybrid Groq/Deterministic';

  return (
    <div className="min-h-screen bg-[#0B0F17] text-slate-100 flex">
      {/* Toast */}
      {toast && (
        <div className={`fixed bottom-6 right-6 z-50 px-4 py-3 rounded-2xl shadow-2xl border text-xs font-semibold flex items-center gap-2 animate-bounce ${
          toast.type === 'danger' ? 'bg-rose-950 text-rose-200 border-rose-800' :
          toast.type === 'warning' ? 'bg-amber-950 text-amber-200 border-amber-800' :
          'bg-slate-900 text-sky-300 border-sky-500/50'
        }`}>
          <span>{toast.message}</span>
        </div>
      )}

      {/* Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        pendingApprovalsCount={dashboardData?.pending_approvals || 0}
        activeDisruptionsCount={dashboardData?.active_disruptions || 0}
      />

      {/* Main Content Area */}
      <div className="flex-1 ml-64 flex flex-col min-h-screen">
        <Topbar
          aiMode={aiModeText}
          onRefresh={fetchAllData}
          refreshing={refreshing}
        />

        <main className="flex-1 p-6 lg:p-8 max-w-7xl w-full mx-auto">
          {activeTab === 'overview' && (
            <OverviewPage
              dashboardData={dashboardData}
              onNavigate={setActiveTab}
              onTriggerDemo={handleTriggerMainDemo}
              loadingDemo={loadingDemo}
            />
          )}

          {activeTab === 'timetable' && (
            <TimetablePage
              schedules={schedules}
              filters={scheduleFilters}
              onRefresh={fetchAllData}
            />
          )}

          {activeTab === 'resources' && (
            <ResourcesPage
              resources={resources}
              onUpdateResource={handleUpdateResource}
            />
          )}

          {activeTab === 'disruptions' && (
            <DisruptionsPage
              disruptions={disruptions}
              resources={resources}
              onCreateDisruption={handleCreateDisruption}
              onTriggerRecovery={handleTriggerMainDemo}
              onNavigateToRecovery={handleNavigateToRecovery}
              creating={loadingDemo}
            />
          )}

          {activeTab === 'agents' && (
            <AgentCentrePage
              agentsData={agentsData}
              executions={latestExecutions}
              onRefresh={fetchAllData}
              refreshing={refreshing}
            />
          )}

          {activeTab === 'recovery' && (
            <RecoveryCentrePage
              recoveryRuns={recoveryRuns}
              activeRunId={activeRecoveryRunId}
              onSelectRun={setActiveRecoveryRunId}
              onApprove={handleApproveRecovery}
              onReject={handleRejectRecovery}
              approving={approving}
            />
          )}

          {activeTab === 'analytics' && (
            <AnalyticsPage
              analyticsData={analyticsData}
            />
          )}

          {activeTab === 'settings' && (
            <SettingsPage
              aiMode={aiModeText}
            />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
