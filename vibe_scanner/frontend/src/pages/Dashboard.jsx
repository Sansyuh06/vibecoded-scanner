import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Scan, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

// Improved Dot Matrix Text Component
const DotMatrixText = ({ text }) => {
    const canvasRef = useRef(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const dotRadius = 3;
        const spacing = 8;
        const fontSize = 140;
        const padding = 20;

        // Setup for text measurement
        ctx.font = `900 ${fontSize}px "Arial Black", "Helvetica Neue", sans-serif`;
        const metrics = ctx.measureText(text);

        canvas.width = metrics.width + padding * 2;
        canvas.height = fontSize + padding;

        // Draw text offscreen to sample
        const offscreen = document.createElement('canvas');
        offscreen.width = canvas.width;
        offscreen.height = canvas.height;
        const offCtx = offscreen.getContext('2d');

        offCtx.font = `900 ${fontSize}px "Arial Black", "Helvetica Neue", sans-serif`;
        offCtx.fillStyle = '#fff';
        offCtx.textBaseline = 'top';
        offCtx.fillText(text, padding, 5);

        const imageData = offCtx.getImageData(0, 0, offscreen.width, offscreen.height);
        const pixels = imageData.data;

        // Clear main canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw dots in a grid pattern
        for (let y = 0; y < canvas.height; y += spacing) {
            for (let x = 0; x < canvas.width; x += spacing) {
                const i = (y * canvas.width + x) * 4;
                const alpha = pixels[i + 3];

                if (alpha > 100) {
                    const intensity = alpha / 255;
                    const radius = dotRadius * (0.6 + intensity * 0.4);

                    ctx.beginPath();
                    ctx.arc(x + spacing / 2, y + spacing / 2, radius, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(255, 255, 255, ${0.7 + intensity * 0.3})`;
                    ctx.fill();
                }
            }
        }
    }, [text]);

    return <canvas ref={canvasRef} className="max-w-full h-auto" />;
};

// Animated Background
const ShaderBackground = () => {
    const canvasRef = useRef(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        let animationId;
        let time = 0;

        const resize = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        };

        const draw = () => {
            time += 0.002;
            const { width, height } = canvas;

            ctx.fillStyle = '#08080c';
            ctx.fillRect(0, 0, width, height);

            // Subtle purple glow
            const gradient = ctx.createRadialGradient(
                width / 2 + Math.sin(time) * 100,
                height / 2 + Math.cos(time * 0.5) * 100,
                0, width / 2, height / 2, Math.max(width, height) * 0.6
            );
            gradient.addColorStop(0, 'rgba(139, 92, 246, 0.06)');
            gradient.addColorStop(0.5, 'rgba(88, 28, 135, 0.03)');
            gradient.addColorStop(1, 'transparent');

            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, width, height);

            animationId = requestAnimationFrame(draw);
        };

        resize();
        window.addEventListener('resize', resize);
        draw();

        return () => {
            window.removeEventListener('resize', resize);
            cancelAnimationFrame(animationId);
        };
    }, []);

    return <canvas ref={canvasRef} className="fixed inset-0 pointer-events-none" />;
};

const Dashboard = () => {
    const [url, setUrl] = useState('');
    const [isScanning, setIsScanning] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleScan = async (e) => {
        e.preventDefault();
        if (!url.trim()) return;

        let targetUrl = url.trim();
        if (!targetUrl.startsWith('http://') && !targetUrl.startsWith('https://')) {
            targetUrl = 'https://' + targetUrl;
        }

        setIsScanning(true);
        setError('');

        try {
            const res = await axios.post('/api/v1/scans/', { target_url: targetUrl });
            navigate(`/scans/${res.data.id}`);
        } catch (err) {
            if (err.response) {
                setError(`${err.response.data?.detail || 'Server error'}`);
            } else if (err.request) {
                setError('Cannot connect to server');
            } else {
                setError('Failed to start scan');
            }
            setIsScanning(false);
        }
    };

    return (
        <div className="relative min-h-screen w-full overflow-hidden bg-[#08080c]">
            <ShaderBackground />

            <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4">

                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="mb-8 text-center"
                >
                    <DotMatrixText text="ONYX" />
                    <p className="text-white/25 text-sm mt-6 tracking-wide" style={{ fontFamily: 'system-ui' }}>
                        Vibecoding won't save you from vulnerabilities.
                    </p>
                </motion.div>

                <motion.form
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.15 }}
                    onSubmit={handleScan}
                    className="w-full max-w-md"
                >
                    <div className="relative bg-white/[0.04] backdrop-blur-xl rounded-xl border border-white/[0.08] overflow-hidden">
                        <input
                            type="text"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            placeholder="Enter target URL..."
                            className="w-full bg-transparent text-white placeholder-white/25 px-5 py-4 text-sm focus:outline-none"
                            style={{ fontFamily: 'system-ui' }}
                            disabled={isScanning}
                        />
                        <div className="flex justify-end px-3 pb-3">
                            <button
                                type="submit"
                                disabled={!url.trim() || isScanning}
                                className={`flex items-center justify-center w-8 h-8 rounded-full transition-all ${url.trim() && !isScanning
                                    ? 'bg-white text-black hover:bg-white/90'
                                    : 'bg-white/10 text-white/30 cursor-not-allowed'
                                    }`}
                            >
                                {isScanning ? <Loader2 size={14} className="animate-spin" /> : <Scan size={14} />}
                            </button>
                        </div>
                    </div>

                    {error && (
                        <p className="mt-3 text-center text-red-400/70 text-xs">{error}</p>
                    )}
                </motion.form>
            </div>
        </div>
    );
};

export default Dashboard;
