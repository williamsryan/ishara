'use client'

import Link from 'next/link'
import { ReactNode } from 'react'
import {
    Home,
    BarChart3,
    Layers,
    Database,
    Settings,
} from 'lucide-react'

const navItems = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Budget', href: '/budget', icon: Database },
    { name: 'Strategy', href: '/strategy', icon: BarChart3 },
    { name: 'Broker', href: '/broker', icon: Layers },
    { name: 'Settings', href: '/settings', icon: Settings },
]

export default function DashboardLayout({ children }: { children: ReactNode }) {
    return (
        <div className="flex h-screen bg-gray-100 text-gray-800 font-sans">
            {/* Sidebar */}
            <aside className="w-20 bg-white border-r flex flex-col items-center py-6 space-y-8 shadow-sm">
                {navItems.map(({ name, href, icon: Icon }) => (
                    <Link
                        key={name}
                        href={href}
                        title={name}
                        className="hover:text-blue-600 flex flex-col items-center gap-1 text-sm text-gray-500"
                    >
                        <Icon className="w-6 h-6" />
                        <span className="text-xs">{name}</span>
                    </Link>
                ))}
            </aside>

            {/* Main */}
            <div className="flex flex-col flex-1">
                {/* Top nav */}
                <header className="flex items-center justify-between px-6 py-4 bg-white border-b shadow-sm">
                    <h1 className="text-xl font-bold tracking-tight text-blue-600">Ishara</h1>
                    <div className="space-x-2">
                        <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium">
                            Login
                        </button>
                        {/* <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium">
                            Select Sheet
                        </button> */}
                    </div>
                </header>

                {/* Main content */}
                <main className="flex-1 overflow-y-auto p-6 bg-gray-50">
                    <div className="max-w-screen-xl mx-auto space-y-6">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    )
}
