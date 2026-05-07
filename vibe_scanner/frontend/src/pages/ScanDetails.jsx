import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, Download, Shield, ShieldAlert, AlertTriangle, CheckCircle, ExternalLink } from 'lucide-react';
import { motion } from 'framer-motion';

// Large Radial Progress Ring
const RadialProgress = ({ value, max, size = 200, strokeWidth = 8, color, label, sublabel }) => {
    const radius = (size - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;
    const percentage = Math.min((value / max) * 100, 100);
    const offset = circumference - (circumference * percentage) / 100;

    return (
        <div className="relative flex flex-col items-center justify-center">
            <svg width={size} height={size} className="-rotate-90">
                {/* Background ring */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke="rgba(255,255,255,0.05)"
                    strokeWidth={strokeWidth}
                />
                {/* Progress ring */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke={color}
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    className="transition-all duration-1000 ease-out"
                />
                {/* Glow effect */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke={color}
                    strokeWidth={strokeWidth + 10}
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    className="transition-all duration-1000 ease-out opacity-20 blur-sm"
                />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                <span className="text-5xl font-bold text-white">{value}</span>
                <span className="text-sm text-white/40 uppercase tracking-widest mt-1">{label}</span>
                {sublabel && <span className="text-xs text-white/20 mt-1">{sublabel}</span>}
            </div>
        </div>
    );
};

// Orbital Ring with nodes
const OrbitalRing = ({ findings, onSelectFinding }) => {
    const [rotation, setRotation] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setRotation(prev => (prev + 0.1) % 360);
        }, 50);
        return () => clearInterval(interval);
    }, []);

    if (!findings.length) return null;

    const severityColors = {
        CRITICAL: '#ef4444',
        HIGH: '#f97316',
        MEDIUM: '#eab308',
        LOW: '#3b82f6',
        INFO: '#6b7280'
    };

    return (
        <div className="relative w-[400px] h-[400px]">
            {/* Orbital rings */}
            <div className="absolute inset-0 rounded-full border border-white/5" />
            <div className="absolute inset-8 rounded-full border border-white/5" />
            <div className="absolute inset-16 rounded-full border border-white/5" />

            {/* Center */}
            <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center shadow-2xl shadow-purple-500/30">
                    <span className="text-2xl font-bold text-white">{findings.length}</span>
                </div>
            </div>

            {/* Nodes */}
            {findings.slice(0, 12).map((finding, i) => {
                const angle = (i / Math.min(findings.length, 12)) * 360 + rotation;
                const rad = (angle * Math.PI) / 180;
                const radius = 160;
                const x = Math.cos(rad) * radius;
                const y = Math.sin(rad) * radius;

                return (
                    <motion.div
                        key={i}
                        className="absolute w-10 h-10 rounded-full flex items-center justify-center cursor-pointer transition-transform hover:scale-125"
                        style={{
                            left: `calc(50% + ${x}px - 20px)`,
                            top: `calc(50% + ${y}px - 20px)`,
                            backgroundColor: severityColors[finding.severity] || '#6b7280',
                            boxShadow: `0 0 20px ${severityColors[finding.severity]}50`
                        }}
                        onClick={() => onSelectFinding(finding)}
                        whileHover={{ scale: 1.3 }}
                    >
                        {finding.severity === 'CRITICAL' ? (
                            <ShieldAlert size={16} className="text-white" />
                        ) : (
                            <Shield size={16} className="text-white" />
                        )}
                    </motion.div>
                );
            })}
        </div>
    );
};

const ScanDetails = () => {
    const { id } = useParams();
    const [scan, setScan] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedFinding, setSelectedFinding] = useState(null);

    useEffect(() => {
        const fetchScan = async () => {
            try {
                const res = await axios.get(`/api/v1/scans/${id}`);
                setScan(res.data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchScan();
        const interval = setInterval(fetchScan, 3000);
        return () => clearInterval(interval);
    }, [id]);

    if (loading) {
        return (
            <div className="min-h-screen bg-[#08080c] flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-16 h-16 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
                    <span className="text-white/40 text-sm">Analyzing...</span>
                </div>
            </div>
        );
    }

    if (!scan) {
        return (
            <div className="min-h-screen bg-[#08080c] flex items-center justify-center">
                <span className="text-red-400">Scan not found</span>
            </div>
        );
    }

    const severityCounts = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0, INFO: 0 };
    scan.findings.forEach(f => {
        if (severityCounts[f.severity] !== undefined) severityCounts[f.severity]++;
    });

    const totalFindings = scan.findings.length;
    const riskScore = Math.min(100, severityCounts.CRITICAL * 25 + severityCounts.HIGH * 15 + severityCounts.MEDIUM * 5);

    return (
        <div className="min-h-screen bg-[#08080c] text-white overflow-hidden">
            {/* Gradient background */}
            <div className="fixed inset-0 bg-gradient-to-br from-purple-900/10 via-transparent to-blue-900/10 pointer-events-none" />

            <div className="relative z-10 max-w-7xl mx-auto px-6 py-8">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center justify-between mb-8"
                >
                    <Link to="/" className="flex items-center gap-2 text-white/40 hover:text-white transition-colors">
                        <ArrowLeft size={18} />
                        <span className="text-sm">Back</span>
                    </Link>

                    {scan.status === 'completed' && (
                        <button
                            onClick={() => window.location.href = `/api/v1/scans/${id}/report/pdf`}
                            className="flex items-center gap-2 bg-white/5 hover:bg-white/10 border border-white/10 px-4 py-2 rounded-lg text-sm transition-all"
                        >
                            <Download size={16} />
                            Export
                        </button>
                    )}
                </motion.div>

                {/* Main radial layout */}
                <div className="flex flex-col lg:flex-row items-center justify-center gap-16 py-8">

                    {/* Left - Main radial gauge */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.2 }}
                    >
                        <RadialProgress
                            value={riskScore}
                            max={100}
                            size={280}
                            strokeWidth={12}
                            color={riskScore > 50 ? '#ef4444' : riskScore > 20 ? '#f97316' : '#22c55e'}
                            label="Risk Score"
                            sublabel={scan.target_url}
                        />
                    </motion.div>

                    {/* Center - Orbital visualization */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.3 }}
                        className="relative"
                    >
                        {scan.findings.length > 0 ? (
                            <OrbitalRing
                                findings={scan.findings}
                                onSelectFinding={setSelectedFinding}
                            />
                        ) : (
                            <div className="w-[400px] h-[400px] flex items-center justify-center">
                                <div className="text-center">
                                    <CheckCircle size={80} className="text-emerald-400 mx-auto mb-4" />
                                    <p className="text-white/60 text-lg">No vulnerabilities detected</p>
                                    <p className="text-white/30 text-sm mt-2">Your target appears secure</p>
                                </div>
                            </div>
                        )}
                    </motion.div>

                    {/* Right - Stats */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.4 }}
                        className="flex flex-col gap-4"
                    >
                        {[
                            { label: 'Critical', count: severityCounts.CRITICAL, color: '#ef4444' },
                            { label: 'High', count: severityCounts.HIGH, color: '#f97316' },
                            { label: 'Medium', count: severityCounts.MEDIUM, color: '#eab308' },
                            { label: 'Low', count: severityCounts.LOW, color: '#3b82f6' },
                            { label: 'Info', count: severityCounts.INFO, color: '#6b7280' },
                        ].map(item => (
                            <div key={item.label} className="flex items-center gap-4 bg-white/[0.02] border border-white/5 rounded-xl px-5 py-3 min-w-[180px]">
                                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                                <span className="text-white/40 text-sm flex-1">{item.label}</span>
                                <span className="text-xl font-bold" style={{ color: item.color }}>{item.count}</span>
                            </div>
                        ))}
                    </motion.div>
                </div>

                {/* Selected Finding Detail */}
                {selectedFinding && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mt-8 max-w-2xl mx-auto bg-white/[0.03] border border-white/10 rounded-2xl p-6"
                    >
                        <div className="flex items-start justify-between mb-4">
                            <div className="flex items-center gap-3">
                                <ShieldAlert className="text-red-400" size={24} />
                                <h3 className="text-lg font-semibold">{selectedFinding.name}</h3>
                            </div>
                            <button
                                onClick={() => setSelectedFinding(null)}
                                className="text-white/40 hover:text-white"
                            >
                                ✕
                            </button>
                        </div>
                        <p className="text-white/50 text-sm mb-4">{selectedFinding.description || 'No description available'}</p>
                        <div className="flex gap-4 text-xs text-white/30">
                            <span>Severity: <span className="text-red-400">{selectedFinding.severity}</span></span>
                            <span>Category: {selectedFinding.category}</span>
                        </div>
                    </motion.div>
                )}

                {/* Status badge */}
                <div className="fixed bottom-6 left-1/2 -translate-x-1/2">
                    <div className={`px-4 py-2 rounded-full text-xs font-mono uppercase tracking-wider ${scan.status === 'completed' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                            scan.status === 'running' ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20 animate-pulse' :
                                'bg-red-500/10 text-red-400 border border-red-500/20'
                        }`}>
                        {scan.status}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ScanDetails;
