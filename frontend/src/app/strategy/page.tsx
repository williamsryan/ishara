import QuoteTicker from '@/components/QuoteTicker'

export default function StrategyPage() {
    return (
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_300px] gap-6">
            <div className="space-y-6">
                <h2 className="text-2xl font-bold text-gray-800">🧠 Strategy Builder</h2>
                <div className="p-4 bg-white rounded-xl border shadow-sm">
                    Placeholder for visual rule builder or strategy config editor.
                </div>
                <div className="p-4 bg-white rounded-xl border shadow-sm">
                    Panel for backtest results, equity curves, etc.
                </div>
            </div>

            <QuoteTicker />
        </div>
    )
}
