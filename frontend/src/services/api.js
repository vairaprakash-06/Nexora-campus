import axios from 'axios';

const API_BASE = '/api';

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

export const campusApi = {
  // Health
  getHealth: () => apiClient.get('/health'),

  // Dashboard
  getDashboard: () => apiClient.get('/dashboard'),

  // Resources
  getResources: (params) => apiClient.get('/resources', { params }),
  getResourceById: (id) => apiClient.get(`/resources/${id}`),
  updateResource: (id, data) => apiClient.put(`/resources/${id}`, data),

  // Schedules
  getSchedules: (params) => apiClient.get('/schedules', { params }),
  getScheduleFilters: () => apiClient.get('/schedules/filters'),

  // Disruptions
  getDisruptions: () => apiClient.get('/disruptions'),
  getDisruptionById: (id) => apiClient.get(`/disruptions/${id}`),
  createDisruption: (data, triggerRecovery = true) => 
    apiClient.post(`/disruptions?trigger_recovery=${triggerRecovery}`, data),

  // Agents
  getAgentsStatus: () => apiClient.get('/agents/status'),
  getAgentExecutions: (runId) => apiClient.get(`/agents/executions/${runId}`),

  // Recovery
  triggerRecoveryRun: (disruptionId) => apiClient.post(`/recovery/run/${disruptionId}`),
  getRecoveryRuns: () => apiClient.get('/recovery/runs'),
  getRecoveryRunById: (runId) => apiClient.get(`/recovery/runs/${runId}`),
  approveRecovery: (runId, comments, approvedBy) => 
    apiClient.post(`/recovery/approve/${runId}`, { comments, approved_by: approvedBy }),
  rejectRecovery: (runId, comments, rejectedBy) => 
    apiClient.post(`/recovery/reject/${runId}`, { comments, approved_by: rejectedBy }),

  // Analytics
  getAnalytics: () => apiClient.get('/analytics'),

  // Audit Logs
  getAuditLogs: (limit = 50) => apiClient.get(`/audit-logs?limit=${limit}`),
};

export default apiClient;
