import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadSpendData = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload/spend', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const uploadSubscriptions = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload/subscriptions', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const uploadContracts = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload/contracts', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const getDashboardSummary = () => api.get('/dashboard/summary');
export const getVendorRedundancy = () => api.get('/vendors/redundancy');
export const getTopRecommendations = () => api.get('/recommendations/top');
export const getUpcomingRenewals = () => api.get('/contracts/upcoming-renewals');
export const getShadowIT = () => api.get('/shadow-it/detect');
export const queryCopilot = (question) => api.post('/copilot/query', { question });
export const getCopilotHistory = () => api.get('/copilot/history');
export const exportReport = () => api.get('/reports/export');
export const getDataStats = () => api.get('/data/stats');
export const clearData = (dataType) => api.delete(`/data/clear/${dataType}`);

export default api;
