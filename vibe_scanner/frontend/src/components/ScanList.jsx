import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Link as ExternalLink, Clock, AlertOctagon } from 'lucide-react';

const ScanList = ({ keyTrigger }) => {
    const [scans, setScans] = useState([]);

    useEffect(() => {
        fetchScans();
    }, [keyTrigger]);

    const fetchScans = async () => {
        try {
            const res = await axios.get('/api/v1/scans/');
            setScans(res.data);
        } catch (err) {
            console.error("Failed to fetch scans", err);
        }
    };

    const getStatusStyle = (status) => {
        switch (status) {
            case 'completed': return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
            case 'running': return 'bg-vibe-accent/10 text-vibe-accent border-vibe-accent/20';
            case 'failed': return 'bg-red-500/10 text-red-400 border-red-500/20';
            default: return 'bg-gray-800 text-gray-400 border-gray-700';
        }
    };

    return (
        <div className="bg-vibe-card rounded-3xl border border-white/10 shadow-2xl overflow-hidden h-full flex flex-col">
            <div className="p-6 border-b border-white/5 flex justify-between items-center bg-black/20">
                <h2 className="text-xl font-bold text-white">Recent Activity</h2>
                <span className="text-xs text-gray-500 font-mono">LIVE FEED</span>
            </div>

            <div className="flex-1 overflow-auto">
                {scans.length === 0 ? (
                    <div className="p-12 text-center text-gray-500 flex flex-col items-center">
                        <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mb-4">
                            <Clock size={24} opacity={0.5} />
                        </div>
                        <p>No scans yet. Launch one to see results.</p>
                    </div>
                ) : (
                    <div className="divide-y divide-white/5">
                        {scans.map((scan) => (
                            <div key={scan.id} className="p-4 hover:bg-white/5 transition-colors group">
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center gap-3">
                                        <div className={`w-2 h-2 rounded-full ${scan.status === 'running' ? 'bg-vibe-accent animate-pulse' : scan.status === 'completed' ? 'bg-emerald-500' : 'bg-red-500'}`}></div>
                                        <h3 className="text-white font-medium truncate max-w-[200px] sm:max-w-xs" title={scan.target_url}>
                                            {scan.target_url.replace(/^https?:\/\//, '')}
                                        </h3>
                                    </div>
                                    <span className={`text-xs px-2 py-0.5 rounded-full border border-opacity-20 font-mono uppercase ${getStatusStyle(scan.status)}`}>
                                        {scan.status}
                                    </span>
                                </div>

                                <div className="flex items-center justify-between">
                                    <div className="flex gap-2">
                                        {scan.critical_count > 0 && (
                                            <span className="flex items-center text-xs text-red-400 bg-red-500/10 px-1.5 py-0.5 rounded border border-red-500/10">
                                                {scan.critical_count} Critic
                                            </span>
                                        )}
                                        {scan.high_count > 0 && (
                                            <span className="flex items-center text-xs text-orange-400 bg-orange-500/10 px-1.5 py-0.5 rounded border border-orange-500/10">
                                                {scan.high_count} High
                                            </span>
                                        )}
                                        {(scan.critical_count === 0 && scan.high_count === 0 && scan.status === 'completed') && (
                                            <span className="text-xs text-emerald-500 flex items-center gap-1">
                                                Clean
                                            </span>
                                        )}
                                    </div>

                                    <Link
                                        to={`/scans/${scan.id}`}
                                        className="text-xs text-gray-400 group-hover:text-white flex items-center gap-1 transition-colors"
                                    >
                                        Details <ExternalLink size={12} />
                                    </Link>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ScanList;
