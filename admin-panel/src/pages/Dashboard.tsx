import React, { useEffect, useState } from 'react';
import { Users, Calendar, Trophy, Activity, RotateCw, Database } from 'lucide-react';
import { AdminService } from '../services/api';

const Dashboard = () => {
    const [stats, setStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const fetchStats = async () => {
        setLoading(true);
        setError('');
        try {
            const response = await AdminService.getStats();
            console.log("Stats Response:", response);
            if (response.data.success) {
                setStats(response.data.data);
            } else {
                setError(response.data.message || 'Failed to fetch stats');
            }
        } catch (err: any) {
            console.error("Fetch Stats Error:", err);
            setError(err.message || 'Network Error');
            if (err.response?.status === 401) {
                setError("Session expired. Please logout and login again.");
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStats();
    }, []);

    const StatCard = ({ title, value, icon: Icon, color, subtext }: any) => (
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-slate-400 text-sm font-medium uppercase tracking-wider">{title}</p>
                    <p className="text-3xl font-bold text-white mt-1">{value?.toLocaleString() || '0'}</p>
                    {subtext && <p className="text-slate-500 text-xs mt-2">{subtext}</p>}
                </div>
                <div className={`p-3 rounded-lg bg-opacity-20 ${color}`}>
                    <Icon size={24} className={color.replace('bg-', 'text-')} />
                </div>
            </div>
        </div>
    );

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white">Dashboard Overview</h1>
                <button
                    onClick={fetchStats}
                    className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-slate-300 transition-colors"
                >
                    <RotateCw size={20} className={loading || loading ? 'animate-spin' : ''} />
                </button>
            </div>

            {error && (
                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400">
                    <strong>Error:</strong> {error}
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    title="Total Users"
                    value={stats?.users}
                    icon={Users}
                    color="bg-blue-500 text-blue-400"
                />
                <StatCard
                    title="Total Matches"
                    value={stats?.matches}
                    subtext={`${stats?.live_matches || 0} Live Now`}
                    icon={Calendar}
                    color="bg-green-500 text-green-400"
                />
                <StatCard
                    title="Active Leagues"
                    value={stats?.leagues}
                    icon={Trophy}
                    color="bg-amber-500 text-amber-400"
                />
                <StatCard
                    title="System Status"
                    value={stats?.system_status === 'healthy' ? 'Online' : 'Issues'}
                    icon={Activity}
                    color={stats?.system_status === 'healthy' ? "bg-emerald-500 text-emerald-400" : "bg-red-500 text-red-400"}
                />
            </div>

            {/* Quick Actions or Recent Activity could go here */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pt-6">
                <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
                    <h3 className="text-lg font-bold text-white mb-4">Quick Shortcuts</h3>
                    <div className="grid grid-cols-2 gap-4">
                        <a href="/matches" className="p-4 bg-slate-700 rounded-lg hover:bg-slate-600 transition text-center cursor-pointer">
                            <Calendar className="mx-auto mb-2 text-blue-400" />
                            <span className="text-sm font-medium">Manage Matches</span>
                        </a>
                        <a href="/system" className="p-4 bg-slate-700 rounded-lg hover:bg-slate-600 transition text-center cursor-pointer">
                            <Database className="mx-auto mb-2 text-purple-400" />
                            <span className="text-sm font-medium">Seed Data</span>
                        </a>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
