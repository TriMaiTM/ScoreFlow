import React, { useEffect, useState } from 'react';
import { Search, ChevronLeft, ChevronRight, Shield } from 'lucide-react';
import { AdminService } from '../services/api';

const Teams = () => {
    const [teams, setTeams] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(0);
    const LIMIT = 10;

    const fetchTeams = async () => {
        setLoading(true);
        try {
            // Create admin specific endpoint or reuse public search if needed
            // We added /admin/teams endpoint which supports pagination
            const response = await AdminService.getTeams(page * LIMIT, LIMIT);
            if (response.data.success) {
                setTeams(response.data.data);
            }
        } catch (error) {
            console.error("Failed to fetch teams", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTeams();
    }, [page]);

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white">Team Management</h1>

            <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
                <div className="p-4 border-b border-slate-700">
                    <div className="relative max-w-md">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={20} />
                        <input
                            type="text"
                            placeholder="Search teams... (Coming Soon)"
                            disabled
                            className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 pl-10 pr-4 text-slate-500 focus:outline-none cursor-not-allowed"
                        />
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="bg-slate-750 text-slate-400 text-sm uppercase">
                                <th className="px-6 py-4 font-medium">Identity</th>
                                <th className="px-6 py-4 font-medium">Name</th>
                                <th className="px-6 py-4 font-medium">Code</th>
                                <th className="px-6 py-4 font-medium">Country</th>
                                <th className="px-6 py-4 font-medium text-right">ID</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-700">
                            {loading ? (
                                <tr><td colSpan={5} className="px-6 py-8 text-center text-slate-500">Loading...</td></tr>
                            ) : teams.length === 0 ? (
                                <tr><td colSpan={5} className="px-6 py-8 text-center text-slate-500">No teams found</td></tr>
                            ) : (
                                teams.map((team) => (
                                    <tr key={team.id} className="hover:bg-slate-700/50 transition-colors">
                                        <td className="px-6 py-4">
                                            {team.logo ? (
                                                <img src={team.logo} alt={team.name} className="w-10 h-10 object-contain bg-white/5 rounded-lg p-1" />
                                            ) : (
                                                <div className="w-10 h-10 bg-slate-700 rounded-lg flex items-center justify-center text-xs text-slate-400">
                                                    N/A
                                                </div>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 text-white font-medium">
                                            {team.name}
                                            {team.is_national && (
                                                <span className="ml-2 px-1.5 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-400 uppercase">
                                                    National
                                                </span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 text-slate-400 font-mono text-sm">
                                            {team.code || team.short_name || '-'}
                                        </td>
                                        <td className="px-6 py-4 text-slate-300">
                                            {team.country || 'Unknown'}
                                        </td>
                                        <td className="px-6 py-4 text-slate-500 text-sm text-right font-mono">
                                            #{team.id}
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

export default Teams;
