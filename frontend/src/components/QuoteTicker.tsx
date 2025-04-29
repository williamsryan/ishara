'use client'

const sampleTickers = [
    { symbol: 'AAPL', price: 210.96, change: +0.82 },
    { symbol: 'GOOG', price: 161.48, change: -0.94 },
    { symbol: 'SPX', price: 5542.54, change: +13.79 },
    { symbol: 'DIA', price: 404.69, change: +2.42 },
    { symbol: 'IXIC', price: 17390.78, change: +24.64 },
]

export default function QuoteTicker() {
    return (
        <aside className="w-full md:w-64 bg-white border rounded-xl shadow-md p-4 space-y-4 sticky top-4 h-fit">
            <h3 className="text-md font-semibold text-gray-700 border-b pb-2">📈 Watchlist</h3>
            <ul className="space-y-2 text-sm">
                {sampleTickers.map((t) => (
                    <li key={t.symbol} className="flex justify-between">
                        <span className="font-medium text-gray-800">{t.symbol}</span>
                        <span
                            className={`font-mono ${t.change >= 0 ? 'text-green-600' : 'text-red-600'
                                }`}
                        >
                            {t.price.toFixed(2)} ({t.change >= 0 ? '+' : ''}
                            {t.change.toFixed(2)})
                        </span>
                    </li>
                ))}
            </ul>
        </aside>
    )
}
