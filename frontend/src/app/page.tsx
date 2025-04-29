'use client'

import { ArrowRight } from 'lucide-react'
import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="min-h-full flex flex-col items-center justify-center px-6 py-16 bg-gradient-to-br from-gray-50 to-white text-gray-900">
      {/* Welcome Section */}
      <div className="text-center max-w-2xl space-y-4 mb-12">
        <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl text-gray-800">
          Welcome to <span className="text-blue-600">Ishara</span>
        </h1>
        <p className="text-lg text-gray-600">
          Unified personal finance, strategy management, and trading intelligence. Connect Sheets, define workflows, and execute trades — all in one interface.
        </p>

        <div className="flex gap-4 justify-center pt-4">
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg shadow transition font-medium">
            Connect Google
          </button>
          <button className="bg-green-600 hover:bg-green-700 text-white px-5 py-2 rounded-lg shadow transition font-medium">
            Select Sheet
          </button>
        </div>
      </div>

      {/* Modules */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl w-full">
        <Link
          href="/budget"
          className="p-6 bg-white shadow-md hover:shadow-lg hover:-translate-y-1 transition rounded-xl text-center"
        >
          <h2 className="text-xl font-semibold text-blue-700 mb-2">💰 Budgeting</h2>
          <p className="text-gray-600 text-sm">View, manage, and optimize your finances.</p>
        </Link>
        <Link
          href="/strategy"
          className="p-6 bg-white shadow-md hover:shadow-lg hover:-translate-y-1 transition rounded-xl text-center"
        >
          <h2 className="text-xl font-semibold text-purple-700 mb-2">🧠 Strategies</h2>
          <p className="text-gray-600 text-sm">Create and manage trading strategies visually.</p>
        </Link>
        <Link
          href="/broker"
          className="p-6 bg-white shadow-md hover:shadow-lg hover:-translate-y-1 transition rounded-xl text-center"
        >
          <h2 className="text-xl font-semibold text-green-700 mb-2">🔌 Broker Setup</h2>
          <p className="text-gray-600 text-sm">Connect Alpaca, IBKR, and configure trading.</p>
        </Link>
      </div>
    </div>
  )
}
