import React, { useEffect, useState } from 'react';
import { Search, UserX, UserCheck, Shield, ChevronLeft, ChevronRight } from 'lucide-react';
import { AdminService } from '../services/api';

const Users = () => {
    const [users, setUsers] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(0);
    const LIMIT = 10;

    const fetchUsers = async () => {
        setLoading(true);
        try {
            const response = await AdminService.getUsers(page * LIMIT, LIMIT);
            if (response.data.success) {
                setUsers(response.data.data);
            }
        } catch (error) {
            console.error("Failed to fetch users", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, [page]);

    const toggleStatus = async (user: any) => {
        const action = user.is_active ? 'deactivate' : 'activate';
        if (!window.confirm(`Are you sure you want to ${action} ${user.name}?`)) return;

        try {
            await AdminService.updateUserStatus(user.id, { is_active: !user.is_active });
            fetchUsers();
        } catch (error) {
            alert("Failed to update user status");
        }
    };

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white">User Management</h1>

            <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
                <div className="p-4 border-b border-slate-700">
                    <div className="relative max-w-md">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={20} />
                        <input
                            type="text"
                            placeholder="Search users by email..."
                            className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 pl-10 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="bg-slate-750 text-slate-400 text-sm uppercase">
                                <th className="px-6 py-4 font-medium">User</th>
                                <th className="px-6 py-4 font-medium">Role</th>
                                <th className="px-6 py-4 font-medium">Joined</th>
                                <th className="px-6 py-4 font-medium">Status</th>
                                <th className="px-6 py-4 font-medium text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-700">
                            {loading ? (
                                <tr><td colSpan={5} className="px-6 py-8 text-center text-slate-500">Loading...</td></tr>
                            ) : users.length === 0 ? (
                                <tr><td colSpan={5} className="px-6 py-8 text-center text-slate-500">No users found</td></tr>
                            ) : (
                                users.map((user) => (
                                    <tr key={user.id} className="hover:bg-slate-700/50 transition-colors">
                                        <td className="px-6 py-4">
                                            <div className="flex items-center">
                                                <div className="w-8 h-8 rounded-full bg-slate-600 flex items-center justify-center mr-3 text-xs font-bold text-white">
                                                    {user.name ? user.name.charAt(0).toUpperCase() : 'U'}
                                                </div>
                                                <div>
                                                    <p className="text-white font-medium text-sm">{user.name || 'Unknown'}</p>
                                                    <p className="text-slate-400 text-xs">{user.email}</p>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            {user.is_superuser ? (
                                                <span className="flex items-center text-purple-400 text-xs font-bold border border-purple-500/30 bg-purple-500/10 px-2 py-1 rounded w-fit">
                                                    <Shield size={12} className="mr-1" /> ADMIN
                                                </span>
                                            ) : (
                                                <span className="text-slate-400 text-xs font-medium">User</span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 text-slate-400 text-sm">
                                            {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`px-2 py-1 rounded-full text-xs font-bold ${user.is_active
                                                    ? 'bg-emerald-500/20 text-emerald-400'
                                                    : 'bg-red-500/20 text-red-400'
                                                }`}>
                                                {user.is_active ? 'Active' : 'Blocked'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            {!user.is_superuser && (
                                                <button
                                                    onClick={() => toggleStatus(user)}
                                                    className={`p-2 rounded-lg transition ${user.is_active
                                                            ? 'text-slate-400 hover:bg-red-500/10 hover:text-red-400'
                                                            : 'text-slate-400 hover:bg-emerald-500/10 hover:text-emerald-400'
                                                        }`}
                                                    title={user.is_active ? "Block User" : "Activate User"}
                                                >
                                                    {user.is_active ? <UserX size={18} /> : <UserCheck size={18} />}
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Pagination */}
                <div className="px-6 py-4 border-t border-slate-700 flex items-center justify-between">
                    <span className="text-sm text-slate-400">Page {page + 1}</span>
                    <div className="flex gap-2">
                        <button
                            onClick={() => setPage(p => Math.max(0, p - 1))}
                            disabled={page === 0}
                            className="p-2 bg-slate-700 rounded hover:bg-slate-600 disabled:opacity-50"
                        >
                            <ChevronLeft size={16} />
                        </button>
                        <button
                            onClick={() => setPage(p => p + 1)}
                            className="p-2 bg-slate-700 rounded hover:bg-slate-600"
                        >
                            <ChevronRight size={16} />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Users;
