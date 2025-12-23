import React, { useState, useEffect } from 'react';
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
    LayoutDashboard,
    Users,
    Calendar,
    Trophy,
    Settings,
    LogOut,
    Menu,
    X,
    Database
} from 'lucide-react';

const DashboardLayout = () => {
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const token = localStorage.getItem('admin_token');
        if (!token) {
            navigate('/login');
        }
    }, [navigate]);

    const handleLogout = () => {
        localStorage.removeItem('admin_token');
        navigate('/login');
    };

    const menuItems = [
        { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
        { path: '/matches', icon: Calendar, label: 'Matches' },
        { path: '/teams', icon: Trophy, label: 'Teams' },
        { path: '/users', icon: Users, label: 'Users' },
        { path: '/system', icon: Database, label: 'System & Seed' },
    ];

    return (
        <div className="flex h-screen bg-slate-900 text-slate-100">
            {/* Sidebar */}
            <aside
                className={`fixed inset-y-0 left-0 z-50 w-64 bg-slate-800 border-r border-slate-700 transition-transform duration-300 ease-in-out ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
                    } md:relative md:translate-x-0`}
            >
                <div className="flex items-center justify-between h-16 px-4 bg-slate-900 border-b border-slate-700">
                    <div className="flex items-center space-x-2">
                        <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-blue-600 bg-clip-text text-transparent">
                            ScoreFlow Admin
                        </span>
                    </div>
                    <button
                        onClick={() => setIsSidebarOpen(false)}
                        className="md:hidden text-slate-400 hover:text-white"
                    >
                        <X size={24} />
                    </button>
                </div>

                <nav className="p-4 space-y-2">
                    {menuItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) =>
                                `flex items-center px-4 py-3 rounded-lg transition-colors ${isActive
                                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/50'
                                    : 'text-slate-400 hover:bg-slate-700 hover:text-white'
                                }`
                            }
                        >
                            <item.icon size={20} className="mr-3" />
                            <span className="font-medium">{item.label}</span>
                        </NavLink>
                    ))}
                </nav>

                <div className="absolute bottom-0 w-full p-4 border-t border-slate-700 bg-slate-800">
                    <button
                        onClick={handleLogout}
                        className="flex items-center w-full px-4 py-3 text-slate-400 hover:bg-red-500/10 hover:text-red-400 rounded-lg transition-colors"
                    >
                        <LogOut size={20} className="mr-3" />
                        <span className="font-medium">Logout</span>
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
                {/* Header */}
                <header className="h-16 bg-slate-800 border-b border-slate-700 flex items-center justify-between px-4 md:px-6">
                    <button
                        onClick={() => setIsSidebarOpen(true)}
                        className="md:hidden text-slate-400 hover:text-white"
                    >
                        <Menu size={24} />
                    </button>

                    <div className="ml-auto flex items-center space-x-4">
                        <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold">
                            A
                        </div>
                        <span className="text-sm font-medium text-slate-300">Administrator</span>
                    </div>
                </header>

                {/* Content Scrollable Area */}
                <main className="flex-1 overflow-auto p-4 md:p-6 pb-20">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default DashboardLayout;
