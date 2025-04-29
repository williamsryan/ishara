'use client'

import Link from 'next/link';
import { ReactNode, useState } from 'react';

export default function DashboardLayout({ children }: { children: ReactNode }) {
    const [menuOpen, setMenuOpen] = useState(false);

    return (
        <div className="flex flex-col h-screen bg-gray-50 text-gray-900">
            {/* Top Navbar */}
            <header className="flex items-center justify-between p-4 bg-white shadow-md">
                <div className="flex items-center gap-6">
                    <Link href="/" className="text-2xl font-bold text-blue-600 hover:text-blue-800 transition">
                        Ishara
                    </Link>

                    {/* Dropdown Menu */}
                    <div className="relative">
                        <button
                            onClick={() => setMenuOpen(!menuOpen)}
                            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-md text-gray-700"
                        >
                            Modules ▾
                        </button>
                        {menuOpen && (
                            <div className="absolute mt-2 w-48 bg-white rounded-md shadow-lg z-50">
                                <Link href="/budget" className="block px-4 py-2 hover:bg-gray-100">Budget</Link>
                                <Link href="/strategy" className="block px-4 py-2 hover:bg-gray-100">Strategy</Link>
                                <Link href="/broker" className="block px-4 py-2 hover:bg-gray-100">Broker</Link>
                                <Link href="/logs" className="block px-4 py-2 hover:bg-gray-100">Logs</Link>
                            </div>
                        )}
                    </div>
                </div>

                {/* Future: User Section */}
                <div>
                    {/* Placeholder for future user login/avatar */}
                    <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition">
                        Login
                    </button>
                </div>
            </header>

            {/* Body */}
            <div className="flex flex-1 overflow-hidden">
                {/* Sidebar (Desktop Only) */}
                <aside className="hidden md:flex flex-col w-64 bg-white border-r shadow-inner p-6">
                    <nav className="flex flex-col gap-6">
                        <Link href="/budget" className="hover:text-blue-500">Budget</Link>
                        <Link href="/strategy" className="hover:text-blue-500">Strategy</Link>
                        <Link href="/broker" className="hover:text-blue-500">Broker</Link>
                        <Link href="/logs" className="hover:text-blue-500">Logs</Link>
                    </nav>
                </aside>

                {/* Main Content */}
                <main className="flex-1 overflow-y-auto p-8">
                    {children}
                </main>
            </div>
        </div>
    );
}
