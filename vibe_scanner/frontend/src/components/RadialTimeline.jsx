
import React, { useState, useEffect, useRef } from "react";
import { ShieldAlert, Shield, Info, AlertTriangle, CheckCircle } from "lucide-react";

// Map severity to icons
const severityIcons = {
    CRITICAL: ShieldAlert,
    HIGH: AlertTriangle,
    MEDIUM: Shield,
    LOW: Info,
    INFO: CheckCircle
};

const severityColors = {
    CRITICAL: { bg: "bg-red-500", border: "border-red-500", text: "text-red-500" },
    HIGH: { bg: "bg-orange-500", border: "border-orange-500", text: "text-orange-500" },
    MEDIUM: { bg: "bg-yellow-500", border: "border-yellow-500", text: "text-yellow-500" },
    LOW: { bg: "bg-blue-500", border: "border-blue-500", text: "text-blue-500" },
    INFO: { bg: "bg-gray-500", border: "border-gray-500", text: "text-gray-500" }
};

export default function RadialTimeline({ findings }) {
    const [selectedId, setSelectedId] = useState(null);
    const [rotationOffset, setRotationOffset] = useState(0);
    const [isAutoRotating, setIsAutoRotating] = useState(true);
    const containerRef = useRef(null);

    // Convert findings to timeline data
    const timelineData = findings.map((finding, index) => ({
        id: index,
        title: finding.name,
        severity: finding.severity,
        description: finding.description,
        category: finding.category,
        icon: severityIcons[finding.severity] || Shield
    }));

    useEffect(() => {
        let interval;
        if (isAutoRotating && timelineData.length > 0) {
            interval = setInterval(() => {
                setRotationOffset(prev => (prev + 0.2) % 360);
            }, 50);
        }
        return () => clearInterval(interval);
    }, [isAutoRotating, timelineData.length]);

    const handleContainerClick = (e) => {
        if (e.target === containerRef.current) {
            setSelectedId(null);
            setIsAutoRotating(true);
        }
    };

    const handleNodeClick = (id) => {
        if (selectedId === id) {
            setSelectedId(null);
            setIsAutoRotating(true);
        } else {
            setSelectedId(id);
            setIsAutoRotating(false);
            // Rotate to node
            const index = id;
            const total = timelineData.length;
            const angle = (index / total) * 360;
            setRotationOffset(270 - angle);
        }
    };

    const calculatePosition = (index, total) => {
        const angle = ((index / total) * 360 + rotationOffset) % 360;
        const radius = 180;
        const rad = (angle * Math.PI) / 180;
        const x = radius * Math.cos(rad);
        const y = radius * Math.sin(rad);
        const scale = Math.max(0.5, Math.min(1, 0.5 + 0.5 * ((1 + Math.sin(rad)) / 2)));
        const zIndex = Math.round(100 + 50 * Math.cos(rad));
        return { x, y, angle, zIndex, scale, opacity: scale };
    };

    if (timelineData.length === 0) {
        return (
            <div className="w-full h-[400px] flex items-center justify-center text-gray-500">
                No findings to display
            </div>
        );
    }

    return (
        <div
            className="relative w-full h-[500px] flex items-center justify-center overflow-hidden"
            ref={containerRef}
            onClick={handleContainerClick}
        >
            {/* Center Core */}
            <div className="absolute w-20 h-20 rounded-full bg-gradient-to-br from-purple-500 via-blue-500 to-teal-500 animate-pulse flex items-center justify-center z-10">
                <div className="absolute w-24 h-24 rounded-full border border-white/20 animate-ping opacity-70" />
                <div className="absolute w-28 h-28 rounded-full border border-white/10 animate-ping opacity-50" style={{ animationDelay: "0.5s" }} />
                <div className="w-10 h-10 rounded-full bg-white/80 backdrop-blur-md flex items-center justify-center">
                    <span className="text-black font-bold text-sm">{timelineData.length}</span>
                </div>
            </div>

            {/* Orbit Ring */}
            <div className="absolute w-[380px] h-[380px] rounded-full border border-white/10 pointer-events-none" />

            {/* Nodes */}
            {timelineData.map((item, index) => {
                const pos = calculatePosition(index, timelineData.length);
                const isActive = selectedId === item.id;
                const Icon = item.icon;
                const colors = severityColors[item.severity] || severityColors.INFO;

                const style = {
                    transform: `translate(${pos.x}px, ${pos.y}px)`,
                    zIndex: isActive ? 200 : pos.zIndex,
                    opacity: isActive ? 1 : pos.opacity
                };

                return (
                    <div
                        key={item.id}
                        className="absolute transition-all duration-500 cursor-pointer flex flex-col items-center justify-center"
                        style={style}
                        onClick={(e) => { e.stopPropagation(); handleNodeClick(item.id); }}
                    >
                        {/* Node Circle */}
                        <div className={`
              w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all duration-300 transform
              ${isActive ? `${colors.bg} text-white border-white shadow-lg shadow-white/30 scale-150` : `bg-black/60 ${colors.text} ${colors.border}`}
            `}>
                            <Icon size={isActive ? 20 : 16} />
                        </div>

                        {/* Label */}
                        <div className={`
              absolute top-14 whitespace-nowrap text-xs font-medium tracking-wide transition-all duration-300 max-w-[100px] truncate text-center
              ${isActive ? "text-white scale-110" : "text-white/60"}
            `}>
                            {item.title}
                        </div>

                        {/* Detail Card */}
                        {isActive && (
                            <div className="absolute top-20 left-1/2 -translate-x-1/2 w-72 bg-black/95 backdrop-blur-lg border border-white/20 shadow-2xl rounded-xl p-4 z-50 text-left">
                                <div className="absolute -top-3 left-1/2 -translate-x-1/2 w-px h-3 bg-white/50" />
                                <div className="flex justify-between items-center mb-3">
                                    <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase ${colors.bg} text-white`}>
                                        {item.severity}
                                    </span>
                                    <span className="text-xs font-mono text-white/40 uppercase">{item.category}</span>
                                </div>
                                <h3 className="text-sm font-bold text-white mb-2">{item.title}</h3>
                                <p className="text-xs text-white/70 leading-relaxed">{item.description}</p>
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
}
