'use client'

import { useEffect, useState } from 'react'
import QuoteTicker from '@/components/QuoteTicker'
import CodeMirror from '@uiw/react-codemirror'
import { yaml as yamlLang } from '@codemirror/lang-yaml'
import * as YAML from 'js-yaml'

const DEFAULT_CONFIG = {
    broker: 'alpaca',
    alpaca: {
        paper: true,
        api_key: 'YOUR_API_KEY',
        secret_key: 'YOUR_SECRET_KEY',
    },
    strategy: {
        max_positions: 5,
        risk_model: 'fixed_fraction',
    },
}

export default function SettingsPage() {
    const [yaml, setYaml] = useState('')
    const [config, setConfig] = useState(DEFAULT_CONFIG)
    const [status, setStatus] = useState<'idle' | 'saved' | 'error'>('idle')

    // On load: pull from localStorage or default
    useEffect(() => {
        const saved = localStorage.getItem('ishara_config')
        if (saved) {
            try {
                const parsed = YAML.load(saved)
                if (typeof parsed === 'object') {
                    setConfig(parsed as any)
                    setYaml(saved)
                }
            } catch (e) {
                console.error('Invalid YAML, using default')
                const raw = YAML.dump(DEFAULT_CONFIG)
                setYaml(raw)
                setConfig(DEFAULT_CONFIG)
            }
        } else {
            const raw = YAML.dump(DEFAULT_CONFIG)
            setYaml(raw)
            setConfig(DEFAULT_CONFIG)
        }
    }, [])

    // Save to localStorage
    const saveConfig = () => {
        try {
            const dumped = YAML.dump(config)
            localStorage.setItem('ishara_config', dumped)
            setYaml(dumped)
            setStatus('saved')
            setTimeout(() => setStatus('idle'), 2000)
        } catch (e) {
            console.error(e)
            setStatus('error')
        }
    }

    // When user edits YAML manually
    const handleYamlChange = (value: string) => {
        setYaml(value)
        try {
            const parsed = YAML.load(value)
            if (typeof parsed === 'object') {
                setConfig(parsed as any)
                setStatus('idle')
            }
        } catch {
            // Don't update config if parse fails
        }
    }

    return (
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_300px] gap-6">
            <div className="space-y-6">
                <h2 className="text-2xl font-bold text-gray-800">⚙️ Settings</h2>

                {/* Basic Visual Settings */}
                <div className="bg-white p-6 rounded-xl border shadow-sm space-y-4">
                    <h3 className="text-lg font-semibold text-gray-700">Basic Configuration</h3>

                    <div className="space-y-2">
                        <label className="block font-medium">Default Broker</label>
                        <select
                            className="w-full border px-3 py-2 rounded-md"
                            value={config.broker}
                            onChange={(e) =>
                                setConfig({ ...config, broker: e.target.value })
                            }
                        >
                            <option value="alpaca">Alpaca</option>
                            <option value="ibkr">Interactive Brokers</option>
                        </select>
                    </div>

                    <div className="space-y-2">
                        <label className="block font-medium">Max Positions</label>
                        <input
                            type="number"
                            className="w-full border px-3 py-2 rounded-md"
                            value={config.strategy.max_positions}
                            onChange={(e) =>
                                setConfig({
                                    ...config,
                                    strategy: {
                                        ...config.strategy,
                                        max_positions: parseInt(e.target.value || '0'),
                                    },
                                })
                            }
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="block font-medium">Risk Model</label>
                        <select
                            className="w-full border px-3 py-2 rounded-md"
                            value={config.strategy.risk_model}
                            onChange={(e) =>
                                setConfig({
                                    ...config,
                                    strategy: {
                                        ...config.strategy,
                                        risk_model: e.target.value,
                                    },
                                })
                            }
                        >
                            <option value="fixed_fraction">Fixed Fraction</option>
                            <option value="volatility_adjusted">Volatility Adjusted</option>
                            <option value="equal_weight">Equal Weight</option>
                        </select>
                    </div>
                </div>

                {/* YAML Editor */}
                <div className="bg-white p-6 rounded-xl border shadow-sm space-y-4">
                    <h3 className="text-lg font-semibold text-gray-700">YAML Config Editor</h3>
                    <CodeMirror
                        value={yaml}
                        height="300px"
                        theme="light"
                        extensions={[yamlLang()]}
                        onChange={handleYamlChange}
                    />
                    <div className="flex justify-between items-center mt-3">
                        <p className="text-xs text-gray-500">
                            Editing YAML or inputs above will sync automatically.
                        </p>
                        <button
                            onClick={saveConfig}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm"
                        >
                            Save Config
                        </button>
                    </div>
                    {status === 'saved' && (
                        <p className="text-green-600 text-sm mt-1">✓ Config saved!</p>
                    )}
                    {status === 'error' && (
                        <p className="text-red-600 text-sm mt-1">✗ Error saving config</p>
                    )}
                </div>
            </div>

            <QuoteTicker />
        </div>
    )
}
