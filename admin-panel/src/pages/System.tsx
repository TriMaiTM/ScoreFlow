import React, { useState, useEffect } from 'react';
import { Database, Play, AlertCircle, RefreshCw, CheckCircle } from 'lucide-react';
import { AdminService } from '../services/api';

const System = () => {
    const [status, setStatus] = useState<any>({
        is_running: false,
        progress: 0,
        message: 'Idle'
    });
    const [loading, setLoading] = useState(false);

    // Poll status if running
    useEffect(() => {
        let interval: any;

        const checkStatus = async () => {
            try {
                const response = await AdminService.getSeedStatus();
                if (response.data.success) {
                    const newStatus = response.data.data;
                    setStatus(newStatus);

                    // Stop polling if done
                    if (!newStatus.is_running && interval) {
                        // Keep polling a bit longer or stop? 
                        // Actually if it was running and now isn't, we can stop, 
                        // but we might want to catch the "Success" message.
                    }
                }
            } catch (err) {
                console.error("Failed to check status", err);
            }
        };

        checkStatus(); // Initial check

        interval = setInterval(checkStatus, 2000); // Check every 2s

        return () => clearInterval(interval);
    }, []);

    const handleSeed = async () => {
        if (status.is_running) return;

        if (!window.confirm("This will trigger a heavy data sync process (approx 2-5 mins). Continue?")) return;

        setLoading(true);
        try {
            const response = await AdminService.triggerSeed();
            if (response.data.success) {
                // Status will update via polling
            } else {
                alert(response.data.message);
            }
        } catch (error) {
            alert("Failed to trigger seed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white">System & Maintenance</h1>

            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
                <div className="flex items-start justify-between mb-6">
                    <div>
                        <h2 className="text-xl font-semibold text-white flex items-center">
                            <Database className="mr-2 text-purple-400" />
                            Data Seeding
                        </h2>
                        <p className="text-slate-400 mt-1 max-w-xl">
                            Manually trigger the background data seeding process. This will fetch the latest leagues, matches, and standings from external APIs.
                        </p>
                    </div>
                    <button
                        onClick={handleSeed}
                        disabled={status.is_running || loading}
                        className={`flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${status.is_running
                                ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                                : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-500/30'
                            }`}
                    >
                        {status.is_running ? <RefreshCw className="animate-spin mr-2" size={18} /> : <Play className="mr-2" size={18} />}
                        {status.is_running ? 'Seeding in Progress...' : 'Start Seeding'}
                    </button>
                </div>

                {/* Progress Display */}
                <div className="bg-slate-900 rounded-lg p-6 border border-slate-700 font-mono text-sm">
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-slate-400">Status:</span>
                        <span className={`font-bold ${status.is_running ? 'text-amber-400' : 'text-emerald-400'}`}>
                            {status.is_running ? 'RUNNING' : 'IDLE / COMPLETE'}
                        </span>
                    </div>

                    <div className="w-full bg-slate-700 rounded-full h-4 mb-4 overflow-hidden">
                        <div
                            className="bg-gradient-to-r from-indigo-500 to-purple-500 h-4 rounded-full transition-all duration-500 ease-out"
                            style={{ width: `${status.progress}%` }}
                        />
                    </div>

                    <div className="flex justify-between text-xs text-slate-500 mb-4">
                        <span>0%</span>
                        <span>{status.progress}%</span>
                        <span>100%</span>
                    </div>

                    <div className="p-3 bg-slate-800 rounded border border-slate-700 text-slate-300">
                        <span className="text-indigo-400 mr-2">$</span>
                        {status.message}
                    </div>
                    {status.updated_at && (
                        <div className="text-right text-xs text-slate-600 mt-2">
                            Last updated: {new Date(status.updated_at).toLocaleTimeString()}
                        </div>
                    )}
                </div>

                <div className="mt-4 flex items-center p-4 bg-amber-500/10 border border-amber-500/20 rounded-lg text-amber-200 text-sm">
                    <AlertCircle size={20} className="mr-3 flex-shrink-0" />
                    <p>
                        Running this process frequently may exhaust API rate limits (Free Tier: 10 req/min).
                        The system automatically adds delays between requests.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default System;
