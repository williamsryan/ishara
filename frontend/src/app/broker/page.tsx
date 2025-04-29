import QuoteTicker from '@/components/QuoteTicker'

export default function BrokerPage() {
    return (
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_300px] gap-6">
            <div className="space-y-6">
                <h2 className="text-2xl font-bold text-gray-800">🔌 Broker Setup</h2>
                <div className="p-4 bg-white rounded-xl border shadow-sm">
                    Select Alpaca, IBKR, or other brokerage accounts here.
                </div>
                <div className="p-4 bg-white rounded-xl border shadow-sm">
                    Link authentication, set default account, and risk profiles.
                </div>
            </div>

            <QuoteTicker />
        </div>
    )
}
