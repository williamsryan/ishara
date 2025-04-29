import './globals.css'
import type { Metadata } from 'next'
import { ReactNode } from 'react'
import DashboardLayout from '@/components/DashboardLayout'

export const metadata: Metadata = {
  title: 'Ishara - Unified Budgeting & Trading',
  description: 'Manage your personal finance and trading strategies in one place.',
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="h-full bg-gray-50 text-gray-900">
      <body className="h-full">
        <DashboardLayout>
          {children}
        </DashboardLayout>
      </body>
    </html>
  )
}
