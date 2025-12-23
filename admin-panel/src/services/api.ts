import axios from 'axios';

const API_URL = 'https://scoreflow-backend-5wu8.onrender.com/api/v1';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add interceptor for auth token if we implement login later
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('admin_token');
    console.log("API Request:", config.url, "Token:", token ? "Present" : "Missing");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const AdminService = {
    // Auth
    login: (data: any) => api.post('/admin/login', data),

    // Dashboard
    getStats: () => api.get('/admin/stats'),

    // Seeding
    triggerSeed: () => api.post('/admin/seed'),
    getSeedStatus: () => api.get('/admin/seed/active'),

    // Users
    getUsers: (skip = 0, limit = 50) => api.get(`/admin/users?skip=${skip}&limit=${limit}`),
    updateUserStatus: (userId: number, data: any) => api.put(`/admin/users/${userId}/status`, data),

    // Matches
    getMatches: (skip = 0, limit = 50) => api.get(`/admin/matches?skip=${skip}&limit=${limit}`),
    getMatch: (id: number) => api.get(`/matches/${id}`),
    createMatch: (data: any) => api.post('/admin/matches', data),
    updateMatch: (id: number, data: any) => api.put(`/admin/matches/${id}`, data),
    deleteMatch: (id: number) => api.delete(`/admin/matches/${id}`),

    // Teams
    getTeams: (skip = 0, limit = 20) => api.get(`/admin/teams?skip=${skip}&limit=${limit}`),

    // Leagues
    getLeagues: () => api.get('/leagues'),
};

export default api;
