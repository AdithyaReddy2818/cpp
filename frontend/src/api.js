import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const register = (data) => api.post('/auth/register', data);
export const login = (data) => api.post('/auth/login', data);

export const getIncidents = (params) => api.get('/incidents', { params });
export const createIncident = (data) => api.post('/incidents', data);
export const getIncident = (id) => api.get(`/incidents/${id}`);
export const updateIncident = (id, data) => api.put(`/incidents/${id}`, data);
export const deleteIncident = (id) => api.delete(`/incidents/${id}`);

export const uploadImage = (id, data) => api.post(`/incidents/${id}/image`, data);
export const updateStatus = (id, data) => api.put(`/incidents/${id}/status`, data);

export const getDashboard = () => api.get('/dashboard');
export const subscribe = (data) => api.post('/subscribe', data);
export const getSubscriberCount = () => api.get('/subscribe/count');

export default api;
