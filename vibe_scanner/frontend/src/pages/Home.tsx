
import React, { useState, useRef, useEffect, useTransition } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Scan, Figma, FilePlus, Wand2, X, Paperclip, Send, ArrowUp } from "lucide-react";
import { cn } from "../lib/utils";

// Mock hook for textarea auto-resize
function useTextareaResize({ minHeight, maxHeight }: { minHeight: number; maxHeight: number }) {
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const adjustHeight = (reset?: boolean) => {
        const textarea = textareaRef.current;
        if(!textarea) return;

        if(reset) {
            textarea.style.height = `${minHeight}px`;
            return;
        }

        textarea.style.height = "auto";
        const newHeight = Math.min(Math.max(textarea.scrollHeight, minHeight), maxHeight);
        textarea.style.height = `${newHeight}px`;
    };

    useEffect(() => {
        adjustHeight();
    }, []);

    return { textareaRef, adjustHeight };
}

export default function Home() {
    const [inputValue, setInputValue] = useState("");
    const [attachments, setAttachments] = useState<string[]>([]);
    const [isSubmitted, setIsSubmitted] = useState(false);
    const [isPending, startTransition] = useTransition();
    const [selectedIndex, setSelectedIndex] = useState(-1);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [activeSuggestion, setActiveSuggestion] = useState<string | null>(null);
    const [cursorPosition, setCursorPosition] = useState({ x: 0, y: 0 });
    const { textareaRef, adjustHeight } = useTextareaResize({ minHeight: 60, maxHeight: 200 });
    const [isFocused, setIsFocused] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    const suggestions = [
        { icon: <Scan className="w-4 h-4" />, label: "Clone UI", description: "Generate a UI from a screenshot", prefix: "/clone" },
        { icon: <Figma className="w-4 h-4" />, label: "Import Figma", description: "Import a design from Figma", prefix: "/figma" },
        { icon: <FilePlus className="w-4 h-4" />, label: "Create Page", description: "Generate a new web page", prefix: "/page" },
        { icon: <Wand2 className="w-4 h-4" />, label: "Improve", description: "Improve existing UI design", prefix: "/improve" },
    ];

    useEffect(() => {
        if(inputValue.startsWith("/") && !inputValue.includes(" ")) {
            setShowSuggestions(true);
            const index = suggestions.findIndex(s => s.prefix.startsWith(inputValue));
            if(index >= 0) setSelectedIndex(index);
            else setSelectedIndex(-1);
        } else {
            setShowSuggestions(false);
        }
    }, [inputValue]);

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            setCursorPosition({ x: e.clientX, y: e.clientY });
        };
        window.addEventListener("mousemove", handleMouseMove);
        return () => window.removeEventListener("mousemove", handleMouseMove);
    }, []);

    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            const target = e.target as Node;
            // Should verify logic here, but keeping it simple for now
            if(containerRef.current && !containerRef.current.contains(target)) {
                setShowSuggestions(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if(showSuggestions) {
            if(e.key === "ArrowDown") {
                e.preventDefault();
                setSelectedIndex(prev => (prev < suggestions.length - 1 ? prev + 1 : 0));
            } else if(e.key === "ArrowUp") {
                e.preventDefault();
                setSelectedIndex(prev => (prev > 0 ? prev - 1 : suggestions.length - 1));
            } else if(e.key === "Tab" || e.key === "Enter") {
                e.preventDefault();
                if(selectedIndex >= 0) {
                    const s = suggestions[selectedIndex];
                    setInputValue(s.prefix + " ");
                    setShowSuggestions(false);
                    setActiveSuggestion(s.label);
                    setTimeout(() => setActiveSuggestion(null), 3500);
                }
            } else if(e.key === "Escape") {
                e.preventDefault();
                setShowSuggestions(false);
            }
        } else {
            if(e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                if(inputValue.trim()) handleSubmit();
            }
        }
    };

    const handleSubmit = () => {
        if(inputValue.trim()) {
            startTransition(() => {
                setIsSubmitted(true);
                setTimeout(() => {
                    setIsSubmitted(false);
                    setInputValue("");
                    adjustHeight(true);
                }, 3000);
            });
        }
    };

    const addAttachment = () => {
        const name = `file-${Math.floor(Math.random() * 1000)}.pdf`;
        setAttachments(prev => [...prev, name]);
    };

    const removeAttachment = (index: number) => {
        setAttachments(prev => prev.filter((_, i) => i !== index));
    };

    const handleSuggestionClick = (index: number) => {
        const s = suggestions[index];
        setInputValue(s.prefix + " ");
        setShowSuggestions(false);
        setActiveSuggestion(s.label);
        setTimeout(() => setActiveSuggestion(null), 2000);
    };

    return (
        <div className="min-h-screen flex flex-col w-full items-center justify-center bg-transparent text-white p-6 relative overflow-hidden">
            {/* Background Blobs */}
            <div className="absolute inset-0 w-full h-full overflow-hidden pointer-events-none">
                <div className="absolute top-0 left-1/4 w-96 h-96 bg-violet-500/10 rounded-full mix-blend-normal filter blur-[128px] animate-pulse" />
                <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-indigo-500/10 rounded-full mix-blend-normal filter blur-[128px] animate-pulse delay-700" />
                <div className="absolute top-1/4 right-1/3 w-64 h-64 bg-fuchsia-500/10 rounded-full mix-blend-normal filter blur-[96px] animate-pulse delay-1000" />
            </div>

            <div className="w-full max-w-2xl mx-auto relative z-10">
                <motion.div
                    className="relative z-10 space-y-12"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, ease: "easeOut" }}
                >
                    {/* Header */}
                    <div className="text-center space-y-3">
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2, duration: 0.5 }}
                            className="inline-block"
                        >
                            <h1 className="text-3xl font-medium tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white/90 to-white/40 pb-1">
                                How can I help today?
                            </h1>
                            <motion.div
                                className="h-px bg-gradient-to-r from-transparent via-white/20 to-transparent"
                                initial={{ width: 0, opacity: 0 }}
                                animate={{ width: "100%", opacity: 1 }}
                                transition={{ delay: 0.5, duration: 0.8 }}
                            />
                        </motion.div>
                        <motion.p
                            className="text-sm text-white/40"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.3 }}
                        >
                            Type a command or ask a question
                        </motion.p>
                    </div>

                    {/* Input Container */}
                    <motion.div
                        className="relative backdrop-blur-2xl bg-white/[0.02] rounded-2xl border border-white/[0.05] shadow-2xl"
                        initial={{ scale: 0.98 }}
                        animate={{ scale: 1 }}
                        transition={{ delay: 0.1 }}
                    >
                        <AnimatePresence>
                            {showSuggestions && (
                                <motion.div
                                    ref={containerRef}
                                    className="absolute left-4 right-4 bottom-full mb-2 backdrop-blur-xl bg-black/90 rounded-lg z-50 shadow-lg border border-white/10 overflow-hidden"
                                    initial={{ opacity: 0, y: 5 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: 5 }}
                                    transition={{ duration: 0.15 }}
                                >
                                    <div className="py-1 bg-black/95">
                                        {suggestions.map((s, i) => (
                                            <motion.div
                                                key={s.prefix}
                                                className={cn(
                                                    "flex items-center gap-2 px-3 py-2 text-xs transition-colors cursor-pointer",
                                                    selectedIndex === i ? "bg-white/10 text-white" : "text-white/70 hover:bg-white/5"
                                                )}
                                                onClick={() => handleSuggestionClick(i)}
                                                initial={{ opacity: 0 }}
                                                animate={{ opacity: 1 }}
                                                transition={{ delay: i * 0.03 }}
                                            >
                                                <div className="w-5 h-5 flex items-center justify-center text-white/60">
                                                    {s.icon}
                                                </div>
                                                <div className="font-medium">{s.label}</div>
                                                <div className="text-white/40 text-xs ml-1">{s.prefix}</div>
                                            </motion.div>
                                        ))}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <div className="p-4">
                            <textarea
                                ref={textareaRef}
                                value={inputValue}
                                onChange={(e) => {
                                    setInputValue(e.target.value);
                                    adjustHeight();
                                }}
                                onKeyDown={handleKeyDown}
                                onFocus={() => setIsFocused(true)}
                                onBlur={() => setIsFocused(false)}
                                placeholder="Ask zap a question..."
                                className={cn(
                                    "w-full px-4 py-3 resize-none bg-transparent border-none text-white/90 text-sm focus:outline-none placeholder:text-white/20 min-h-[60px]"
                                )}
                                style={{ overflow: "hidden" }}
                            />
                        </div>

                        <AnimatePresence>
                            {attachments.length > 0 && (
                                <motion.div
                                    className="px-4 pb-3 flex gap-2 flex-wrap"
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: "auto" }}
                                    exit={{ opacity: 0, height: 0 }}
                                >
                                    {attachments.map((file, i) => (
                                        <motion.div
                                            key={i}
                                            className="flex items-center gap-2 text-xs bg-white/[0.03] py-1.5 px-3 rounded-lg text-white/70"
                                            initial={{ opacity: 0, scale: 0.9 }}
                                            animate={{ opacity: 1, scale: 1 }}
                                            exit={{ opacity: 0, scale: 0.9 }}
                                        >
                                            <span>{file}</span>
                                            <button onClick={() => removeAttachment(i)} className="text-white/40 hover:text-white transition-colors">
                                                <X className="w-3 h-3" />
                                            </button>
                                        </motion.div>
                                    ))}
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <div className="p-4 border-t border-white/[0.05] flex items-center justify-between gap-4">
                            <div className="flex items-center gap-3">
                                <motion.button
                                    type="button"
                                    onClick={addAttachment}
                                    whileTap={{ scale: 0.94 }}
                                    className="p-2 text-white/40 hover:text-white/90 rounded-lg transition-colors relative group"
                                >
                                    <Paperclip className="w-4 h-4" />
                                </motion.button>
                            </div>
                            <div className="flex items-center gap-2">
                                <motion.button
                                    type="button"
                                    onClick={handleSubmit}
                                    disabled={!inputValue.trim()}
                                    whileTap={{ scale: 0.94 }}
                                    className={cn(
                                        "p-2 rounded-lg transition-all duration-200",
                                        inputValue.trim()
                                            ? "bg-white text-black hover:bg-white/90 shadow-lg shadow-white/10"
                                            : "bg-white/10 text-white/30 cursor-not-allowed"
                                    )}
                                >
                                    {isPending ? <div className="w-4 h-4 border-2 border-black/50 border-t-black rounded-full animate-spin" /> : <ArrowUp className="w-4 h-4" />}
                                </motion.button>
                            </div>
                        </div>
                    </motion.div>
                </motion.div>
            </div>
        </div>
    );
}
