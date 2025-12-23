import React, { useEffect, useState } from 'react';
import { Plus, Edit2, Trash2, Search, ChevronLeft, ChevronRight } from 'lucide-react';
import { AdminService } from '../services/api';

const Matches = () => {
    const [matches, setMatches] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(0);
    const LIMIT = 10;

    const fetchMatches = async () => {
        setLoading(true);
        try {
            // Create admin specific endpoint in api.ts or use the public one properly
            // We updated api.ts to use /matches, but we just added /admin/matches endpoint
            // So let's update api.ts to use /admin/matches for getMatches
            const response = await AdminService.getMatches(page * LIMIT, LIMIT);
            if (response.data.success) {
                setMatches(response.data.data);
            }
        } catch (error) {
            console.error("Failed to fetch matches", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchMatches();
    }, [page]);

    const handleDelete = async (id: number) => {
        if (!window.confirm("Are you sure you want to delete this match?")) return;
        try {
            await AdminService.deleteMatch(id);
            fetchMatches();
        } catch (error) {
            alert("Failed to delete match");
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-white">Match Management</h1>
                <button className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
                    <Plus size={20} className="mr-2" />
                    Add Match
                </button>
            </div>

            <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
                <div className="p-4 border-b border-slate-700 flex gap-4">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={20} />
                        <input
                            type="text"
                            placeholder="Search matches..."
                            className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 pl-10 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="bg-slate-750 text-slate-400 text-sm uppercase">
                                <th className="px-6 py-4 font-medium">Date</th>
                                <th className="px-6 py-4 font-medium">League</th>
                                <th className="px-6 py-4 font-medium text-right">Home</th>
                                <th className="px-6 py-4 font-medium text-center">Score</th>
                                <th className="px-6 py-4 font-medium">Away</th>
                                <th className="px-6 py-4 font-medium">Status</th>
                                <th className="px-6 py-4 font-medium text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-700">
                            {loading ? (
                                <tr><td colSpan={7} className="px-6 py-8 text-center text-slate-500">Loading...</td></tr>
                            ) : matches.length === 0 ? (
                                <tr><td colSpan={7} className="px-6 py-8 text-center text-slate-500">No matches found</td></tr>
                            ) : (
                                matches.map((match) => (
                                    <tr key={match.id} className="hover:bg-slate-700/50 transition-colors">
                                        <td className="px-6 py-4 text-slate-300 text-sm">
                                            {new Date(match.date).toLocaleDateString()}
                                        </td>
                                        <td className="px-6 py-4 text-slate-300 text-sm">
                                            {match.league}
                                        </td>
                                        <td className="px-6 py-4 text-white font-medium text-right">
                                            {match.home_team}
                                        </td>
                                        <td className="px-6 py-4 text-white font-bold text-center bg-slate-700/30">
                                            {match.home_score} - {match.away_score}
                                        </td>
                                        <td className="px-6 py-4 text-white font-medium">
                                            {match.away_team}
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`px-2 py-1 rounded-full text-xs font-bold uppercase ${match.status === 'live' ? 'bg-red-500/20 text-red-400 animate-pulse' :
                                                    match.status === 'finished' ? 'bg-slate-600/20 text-slate-400' :
                                                        'bg-blue-500/20 text-blue-400'
                                                }`}>
                                                {match.status}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <div className="flex items-center justify-end space-x-2">
                                                <button className="p-2 hover:bg-slate-600 rounded-lg text-slate-400 hover:text-blue-400 transition">
                                                    <Edit2 size={16} />
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(match.id)}
                                                    className="p-2 hover:bg-slate-600 rounded-lg text-slate-400 hover:text-red-400 transition"
                                                >
                                                    <Trash2 size={16} />
                                                </button>
                                            </div>
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

export default Matches;
