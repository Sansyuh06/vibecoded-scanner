import React, { useState } from 'react';
import axios from 'axios';
import { Search, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

const ScanForm = ({ onScanStarted }) => {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            let target = url;
            if (!target.startsWith('http')) {
                target = 'https://' + target;
            }

            const res = await axios.post('/api/v1/scans/', { target_url: target });
            onScanStarted(res.data);
            setUrl('');
        } catch (err) {
            setError('Connection to scanner backend failed.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-gradient-to-b from-vibe-card to-black p-8 rounded-3xl border border-white/10 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-vibe-accent to-blue-500"></div>

            <h2 className="text-2xl font-bold mb-2 text-white">Start New Scan</h2>
            <p className="text-gray-400 text-sm mb-6">Enter a target URL to begin a comprehensive security analysis.</p>

            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <div className="relative">
                    <Search className="absolute left-4 top-3.5 text-gray-500" size={20} />
                    <input
                        type="text"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        placeholder="example.com"
                        className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white placeholder-gray-600 focus:outline-none focus:border-vibe-accent focus:ring-1 focus:ring-vibe-accent transition-all"
                    />
                </div>

                <button
                    type="submit"
                    disabled={loading || !url}
                    className="w-full bg-vibe-accent hover:bg-purple-600 text-white font-bold py-3 px-6 rounded-xl transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(124,58,237,0.3)] hover:shadow-[0_0_30px_rgba(124,58,237,0.5)]"
                >
                    {loading ? (
                        <>
                            <motion.div
                                animate={{ rotate: 360 }}
                                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                            >
                                <Loader2 size={20} />
                            </motion.div>
                            Initializing...
                        </>
                    ) : (
                        'Launch Scan'
                    )}
                </button>
            </form>

            {error && (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm text-center"
                >
                    {error}
                </motion.div>
            )}
        </div>
    );
};

export default ScanForm;
