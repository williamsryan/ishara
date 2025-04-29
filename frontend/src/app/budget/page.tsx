import QuoteTicker from '@/components/QuoteTicker'

export default function BudgetPage() {
    return (
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_300px] gap-6">
            {/* Main Content */}
            <div className="space-y-6">
                <h2 className="text-2xl font-bold text-gray-800">💰 Budgeting</h2>
                <div className="p-4 bg-white rounded-xl border shadow-sm">
                    Placeholder for budget chart, cash flow analysis, or imported Sheet data.
                </div>
                <div className="p-4 bg-white rounded-xl border shadow-sm">
                    Budget categories + trend breakdown module.
                </div>
            </div>

            {/* Watchlist Ticker */}
            <QuoteTicker />
        </div>
    )
}
