import axios from 'axios';

const api = axios.create({
    baseURL: 'https://scoreflow-backend-5wu8.onrender.com/api/v1/admin',
    headers: {
        'Content-Type': 'application/json',
    },
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('adminToken');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default api;
