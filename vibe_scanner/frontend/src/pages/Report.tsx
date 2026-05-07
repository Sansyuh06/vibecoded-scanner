
import React, { useState, useEffect, useRef } from "react";
import { Calendar, Palette, Code, Bug, Rocket, Circle, CheckCircle, Clock, ArrowUp } from "lucide-react";
import { cn } from "../lib/utils";

// Data
const timelineData = [
    { id: 1, title: "Planning", date: "Jan 2024", content: "Project planning and requirements gathering phase.", category: "Planning", icon: Calendar, relatedIds: [2], status: "completed", energy: 100 },
    { id: 2, title: "Design", date: "Feb 2024", content: "UI/UX design and system architecture.", category: "Design", icon: Palette, relatedIds: [1, 3], status: "completed", energy: 90 },
    { id: 3, title: "Development", date: "Mar 2024", content: "Core features implementation and testing.", category: "Development", icon: Code, relatedIds: [2, 4], status: "in-progress", energy: 60 },
    { id: 4, title: "Testing", date: "Apr 2024", content: "User testing and bug fixes.", category: "Testing", icon: Bug, relatedIds: [3, 5], status: "pending", energy: 30 },
    { id: 5, title: "Release", date: "May 2024", content: "Final deployment and release.", category: "Release", icon: Rocket, relatedIds: [4], status: "pending", energy: 10 }
];

export default function Report() {
    const [hoveredId, setHoveredId] = useState<number | null>(null);
    const [layoutMode, setLayoutMode] = useState("orbital"); // 'orbital' or 'grid' (grid logic omitted as unused in original snippet logic?)
    const [rotationOffset, setRotationOffset] = useState(0);
    const [isAutoRotating, setIsAutoRotating] = useState(true);
    const [activeNodes, setActiveNodes] = useState<Record<number, boolean>>({});
    const [pan, setPan] = useState({ x: 0, y: 0 });
    const [selectedId, setSelectedId] = useState<number | null>(null);

    const containerRef = useRef<HTMLDivElement>(null);
    const contentRef = useRef<HTMLDivElement>(null);
    const nodeRefs = useRef<Record<number, HTMLDivElement | null>>({});

    const handleContainerClick = (e: React.MouseEvent) => {
        if(e.target === containerRef.current || e.target === contentRef.current) {
            setHoveredId(null);
            setSelectedId(null);
            setIsAutoRotating(true);
            setActiveNodes({});
        }
    };

    const handleNodeClick = (id: number) => {
        if(activeNodes[id]) {
            setSelectedId(null);
            setIsAutoRotating(true);
            setActiveNodes({});
        } else {
            setSelectedId(id);
            setIsAutoRotating(false);
            const related = getRelatedIds(id);
            const newActive: Record<number, boolean> = { [id]: true };
            related.forEach(rid => newActive[rid] = true);
            setActiveNodes(newActive);
            rotateToNode(id);
        }
    };

    useEffect(() => {
        let interval: any;
        if(isAutoRotating && layoutMode === "orbital") {
            interval = setInterval(() => {
                setRotationOffset(prev => (prev + 0.3) % 360);
            }, 50);
        }
        return () => clearInterval(interval);
    }, [isAutoRotating, layoutMode]);

    const rotateToNode = (id: number) => {
        if(layoutMode !== 'orbital' || !nodeRefs.current[id]) return;
        const index = timelineData.findIndex(item => item.id === id);
        const total = timelineData.length;
        const angle = (index / total) * 360;
        setRotationOffset(270 - angle); // Rotate so node is at top (270deg)
    };

    const calculatePosition = (index: number, total: number) => {
        const angle = ((index / total) * 360 + rotationOffset) % 360;
        const radius = 200;
        const rad = (angle * Math.PI) / 180;
        const x = radius * Math.cos(rad) + pan.x;
        const y = radius * Math.sin(rad) + pan.y;

        // Scale and Z-index effect
        const scale = Math.max(0.4, Math.min(1, 0.4 + 0.6 * ((1 + Math.sin(rad)) / 2))); // Perspective approximation
        const zIndex = Math.round(100 + 50 * Math.cos(rad)); // 3D z-index approximation ?? Actually simple sin usage
        // Original used `Math.sin(rad)` for Y, so items at bottom are 'closer'? 
        // Wait, original: `Math.max(.4, Math.min(1, .4 + .6*((1 + Math.sin(de))/2)))`.
        // If sin(de) is 1 (90deg, bottom), scale is 1. If -1 (top), scale 0.4.
        // So items at BOTTOM are closest.

        return { x, y, angle, zIndex, scale, opacity: scale };
    };

    const getRelatedIds = (id: number | null) => {
        if(!id) return [];
        const item = timelineData.find(i => i.id === id);
        return item ? item.relatedIds : [];
    };

    const isRelated = (id: number) => {
        if(!selectedId) return false;
        return getRelatedIds(selectedId).includes(id);
    };

    const getStatusColor = (status: string) => {
        switch(status) {
            case "completed": return "text-white bg-black border-white";
            case "in-progress": return "text-black bg-white border-black";
            case "pending": return "text-white bg-black/40 border-white/50";
            default: return "text-white bg-black/40 border-white/50";
        }
    };

    return (
        <div
            className="w-full h-full min-h-screen flex flex-col items-center justify-center bg-transparent overflow-hidden"
            ref={containerRef}
            onClick={handleContainerClick}
        >
            <div className="relative w-full max-w-4xl h-[600px] flex items-center justify-center">
                <div
                    className="absolute w-full h-full flex items-center justify-center"
                    ref={contentRef}
                    style={{ perspective: "1000px", transform: `translate(${pan.x}px, ${pan.y}px)` }}
                >
                    {/* Center Core */}
                    <div className="absolute w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 via-blue-500 to-teal-500 animate-pulse flex items-center justify-center z-10">
                        <div className="absolute w-20 h-20 rounded-full border border-white/20 animate-ping opacity-70" />
                        <div className="absolute w-24 h-24 rounded-full border border-white/10 animate-ping opacity-50" style={{ animationDelay: "0.5s" }} />
                        <div className="w-8 h-8 rounded-full bg-white/80 backdrop-blur-md" />
                    </div>

                    {/* Orbit Ring */}
                    <div className="absolute w-96 h-96 rounded-full border border-white/10 pointer-events-none" />

                    {/* Nodes */}
                    {timelineData.map((item, index) => {
                        const pos = calculatePosition(index, timelineData.length);
                        const isActive = activeNodes[item.id];
                        const isRel = isRelated(item.id);
                        const isHovered = hoveredId === item.id;
                        const Icon = item.icon;

                        // Styles
                        const style: React.CSSProperties = {
                            transform: `translate(${pos.x}px, ${pos.y}px)`,
                            zIndex: isActive ? 200 : pos.zIndex,
                            opacity: isActive ? 1 : pos.opacity
                        };

                        return (
                            <div
                                key={item.id}
                                ref={el => { nodeRefs.current[item.id] = el; }}
                                className="absolute transition-all duration-700 cursor-pointer flex flex-col items-center justify-center"
                                style={style}
                                onClick={(e) => { e.stopPropagation(); handleNodeClick(item.id); }}
                                onMouseEnter={() => setHoveredId(item.id)}
                                onMouseLeave={() => setHoveredId(null)}
                            >
                                {/* Ripple Effect if Selected */}
                                <div
                                    className={cn(
                                        "absolute rounded-full -inset-1",
                                        isHovered ? "animate-pulse duration-1000" : ""
                                    )}
                                    style={{
                                        background: "radial-gradient(circle, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0) 70%)",
                                        width: `${item.energy * 0.5 + 40}px`,
                                        height: `${item.energy * 0.5 + 40}px`
                                    }}
                                />

                                {/* Node Circle */}
                                <div className={cn(
                                    "w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-300 transform",
                                    isActive ? "bg-white text-black border-white shadow-lg shadow-white/30 scale-150" :
                                        isRel ? "bg-white/50 text-black border-white animate-pulse" :
                                            "bg-black text-white border-white/40"
                                )}>
                                    <Icon size={16} />
                                </div>

                                {/* Label */}
                                <div className={cn(
                                    "absolute top-12 whitespace-nowrap text-xs font-semibold tracking-wider transition-all duration-300",
                                    isActive ? "text-white scale-125" : "text-white/70"
                                )}>
                                    {item.title}
                                </div>

                                {/* Detail Card (Visible when Active) */}
                                {isActive && (
                                    <div className="absolute top-20 left-1/2 -translate-x-1/2 w-64 bg-black/90 backdrop-blur-lg border border-white/30 shadow-xl shadow-white/10 rounded-lg p-4 z-50 text-left">
                                        <div className="absolute -top-3 left-1/2 -translate-x-1/2 w-px h-3 bg-white/50" />
                                        <div className="pb-2 border-b border-white/10 mb-2">
                                            <div className="flex justify-between items-center">
                                                <span className={cn("px-2 py-0.5 rounded text-[10px] font-bold uppercase", getStatusColor(item.status))}>
                                                    {item.status === 'completed' ? 'COMPLETE' : item.status === 'in-progress' ? 'IN PROGRESS' : 'PENDING'}
                                                </span>
                                                <span className="text-xs font-mono text-white/50">{item.date}</span>
                                            </div>
                                            <div className="text-sm font-bold mt-2 text-white">{item.title}</div>
                                        </div>

                                        <div className="text-xs text-white/80 space-y-3">
                                            <p>{item.content}</p>

                                            <div>
                                                <div className="flex justify-between items-center text-xs mb-1 text-white/60">
                                                    <span className="flex items-center"><CheckCircle size={10} className="mr-1" /> Energy Level</span>
                                                    <span className="font-mono text-white">{item.energy}%</span>
                                                </div>
                                                <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden">
                                                    <div className="h-full bg-gradient-to-r from-blue-500 to-purple-500" style={{ width: `${item.energy}%` }} />
                                                </div>
                                            </div>

                                            {item.relatedIds.length > 0 && (
                                                <div>
                                                    <div className="flex items-center mb-2 text-white/60">
                                                        <Circle size={10} className="mr-1" />
                                                        <h4 className="text-[10px] uppercase tracking-wider font-medium">Connected Nodes</h4>
                                                    </div>
                                                    <div className="flex flex-wrap gap-1">
                                                        {item.relatedIds.map(rid => {
                                                            const rItem = timelineData.find(i => i.id === rid);
                                                            return (
                                                                <button
                                                                    key={rid}
                                                                    className="flex items-center px-2 py-1 text-[10px] rounded border border-white/20 bg-transparent hover:bg-white/10 text-white/80 hover:text-white transition-all"
                                                                    onClick={(e) => { e.stopPropagation(); handleNodeClick(rid); }}
                                                                >
                                                                    {rItem?.title}
                                                                    <ArrowUp size={8} className="ml-1 rotate-45" />
                                                                </button>
                                                            );
                                                        })}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
