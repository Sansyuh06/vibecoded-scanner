
import React, { useState, useEffect } from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { ChevronDown, Check } from "lucide-react";
import { cn } from "../../lib/utils";

const demos = [
    { name: "AI Chat Interface", path: "/" },
    { name: "Radial Orbital Timeline", path: "/report" },
];

export function AppLayout() {
    const navigate = useNavigate();
    const location = useLocation();
    const [open, setOpen] = useState(false);

    // Determine current demo based on path
    const currentDemo = demos.find(d => d.path === location.pathname) || demos[0];

    return (
        <div className="relative flex min-h-screen w-full flex-col bg-background text-foreground overflow-hidden">
            {/* Dynamic Background */}
            <div className="absolute inset-0 w-full h-full lab-bg pointer-events-none">
                <div className="absolute inset-0 bg-[radial-gradient(#00000021_1px,transparent_1px)] dark:bg-[radial-gradient(#ffffff22_1px,transparent_1px)]" />
            </div>

            {/* Navigation Switcher (Top Right) */}
            <div className="absolute z-50 top-4 right-14 flex flex-col items-end gap-1">
                <div className="relative">
                    <button
                        onClick={() => setOpen(!open)}
                        className="flex h-8 items-center justify-between gap-2 rounded-md border border-input bg-background/50 backdrop-blur-sm px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 [&>span]:line-clamp-1 w-[200px] hover:bg-accent hover:text-accent-foreground transition-colors"
                    >
                        <span className="truncate">{currentDemo.name}</span>
                        <ChevronDown className="h-4 w-4 opacity-50" />
                    </button>

                    {open && (
                        <div className="absolute top-full mt-1 w-[200px] z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md animate-in fade-in-0 zoom-in-95">
                            <div className="p-1">
                                {demos.map((demo) => (
                                    <div
                                        key={demo.path}
                                        className={cn(
                                            "relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none focus:bg-accent focus:text-accent-foreground hover:bg-accent hover:text-accent-foreground transition-colors cursor-pointer",
                                            currentDemo.path === demo.path && "bg-accent"
                                        )}
                                        onClick={() => {
                                            navigate(demo.path);
                                            setOpen(false);
                                        }}
                                    >
                                        {currentDemo.path === demo.path && (
                                            <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
                                                <Check className="h-4 w-4" />
                                            </span>
                                        )}
                                        <span>{demo.name}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Main Content Area */}
            <div className="flex w-full justify-center relative flex-1">
                <Outlet />
            </div>
        </div>
    );
}
