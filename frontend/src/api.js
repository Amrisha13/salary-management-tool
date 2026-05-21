import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Employee endpoints
export const employeeAPI = {
  getAll: (page = 1, perPage = 50, filters = {}) => {
    const params = new URLSearchParams({ page, per_page: perPage });
    if (filters.country) params.append('country', filters.country);
    if (filters.jobTitle) params.append('job_title', filters.jobTitle);
    return api.get(`/employees?${params}`);
  },
  
  getById: (id) => api.get(`/employees/${id}`),
  
  create: (data) => api.post('/employees', data),
  
  update: (id, data) => api.put(`/employees/${id}`, data),
  
  delete: (id) => api.delete(`/employees/${id}`),
};

// Insights endpoints
export const insightsAPI = {
  getCountrySummary: () => api.get('/insights/summary'),
  
  getCountryInsights: (country) => api.get(`/insights/country/${country}`),
  
  getJobTitleInsights: (jobTitle, country) => 
    api.get(`/insights/job-title?job_title=${jobTitle}&country=${country}`),
  
  getAllCountries: () => api.get('/insights/countries'),
  
  getAllJobTitles: (country = '') => {
    const url = country ? `/insights/job-titles?country=${country}` : '/insights/job-titles';
    return api.get(url);
  },
};

export default api;
