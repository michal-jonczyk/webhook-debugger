import { useState, useEffect, useRef } from 'react'

const API_URL = 'https://webhook-debugger-production-48ab.up.railway.app'

function CreateEndpoint() {
    const [endpointName, setEndpointName] = useState('')
    const [createdEndpoint, setCreatedEndpoint] = useState(null)
    const [requests, setRequests] = useState([])
    const [showRequests, setShowRequests] = useState(false)
    const [wsConnected, setWsConnected] = useState(false)

    const wsRef = useRef(null)

    useEffect(() => {
        if (!createdEndpoint) return

        const wsUrl = API_URL.replace('https://', 'wss://').replace('http://', 'ws://')
        const ws = new WebSocket(`${wsUrl}/ws/${createdEndpoint.id}`)
        wsRef.current = ws

        ws.onopen = () => {
            console.log('✅ WebSocket Connected')
            setWsConnected(true)
        }

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data)
            console.log('📨 WebSocket message:', message)

            if (message.type === 'new_request') {
                setRequests(prev => [message.data, ...prev])
                setShowRequests(true)
                console.log('✨ New request added in real-time!')
            }
        }

        ws.onerror = (error) => {
            console.error('❌ WebSocket error:', error)
        }

        ws.onclose = () => {
            console.log('🔌 WebSocket disconnected')
            setWsConnected(false)
        }

        return () => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.close()
            }
        }
    }, [createdEndpoint])

    const handleCreate = async () => {
        try {
            const response = await fetch(`${API_URL}/endpoints`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: endpointName })
            })

            const data = await response.json()
            setCreatedEndpoint(data)
            console.log('✅ Endpoint created:', data)
        } catch (error) {
            console.error('❌ Error:', error)
        }
    }

    const loadRequests = async () => {
        try {
            const response = await fetch(`${API_URL}/endpoints/${createdEndpoint.id}/requests`)
            const data = await response.json()
            console.log('📦 Backend response:', data)
            setRequests(data.requests || [])
            setShowRequests(true)
        } catch (error) {
            console.error('❌ Error loading requests:', error)
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-8 px-4">
            <div className="max-w-5xl mx-auto">
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold text-gray-900 mb-2">
                        🔍 Webhook Debugger
                    </h1>
                    <p className="text-gray-600">
                        Real-time webhook inspection with AI-powered mock responses
                    </p>
                </div>

                <div className="bg-white rounded-xl shadow-lg p-8 mb-6">
                    <h2 className="text-xl font-semibold mb-4">Create New Endpoint</h2>

                    <label className="block mb-2 font-medium text-gray-700">
                        Endpoint Name (optional)
                    </label>

                    <div className="flex gap-3">
                        <input
                            type="text"
                            value={endpointName}
                            onChange={(e) => setEndpointName(e.target.value)}
                            placeholder="my-webhook-endpoint"
                            className="flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />

                        <button
                            onClick={handleCreate}
                            className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 font-medium transition-colors"
                        >
                            Create Endpoint
                        </button>
                    </div>
                </div>

                {createdEndpoint && (
                    <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl p-6 mb-6">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-2xl font-bold text-green-800 flex items-center gap-2">
                                ✅ Endpoint Created!
                            </h2>

                            {wsConnected && (
                                <div className="flex items-center gap-2 bg-green-100 px-4 py-2 rounded-full">
                                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                                    <span className="text-sm text-green-700 font-semibold">Live</span>
                                </div>
                            )}
                        </div>

                        <p className="text-sm text-gray-700 mb-3 font-medium">Your webhook URL:</p>

                        <div className="bg-white border-2 border-green-300 rounded-lg p-4 mb-4">
                            <code className="text-sm text-gray-800 break-all font-mono">
                                {createdEndpoint.url}
                            </code>
                        </div>

                        <div className="flex flex-wrap gap-3">
                            <button
                                onClick={() => {
                                    navigator.clipboard.writeText(createdEndpoint.url)
                                    alert('✅ URL copied to clipboard!')
                                }}
                                className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 font-medium transition-colors"
                            >
                                📋 Copy URL
                            </button>

                            <button
                                onClick={async () => {
                                    const response = await fetch(createdEndpoint.url, {
                                        method: 'POST',
                                        headers: {'Content-Type': 'application/json'},
                                        body: JSON.stringify({
                                            test: true,
                                            message: 'Hello from frontend!',
                                            timestamp: new Date().toISOString()
                                        })
                                    })
                                    const result = await response.json()
                                    console.log('Test sent:', result)
                                }}
                                className="bg-green-500 text-white px-6 py-2 rounded-lg hover:bg-green-600 font-medium transition-colors"
                            >
                                🚀 Send Test
                            </button>

                            <button
                                onClick={loadRequests}
                                className="bg-purple-500 text-white px-6 py-2 rounded-lg hover:bg-purple-600 font-medium transition-colors"
                            >
                                📜 Load History
                            </button>
                        </div>
                    </div>
                )}

                {showRequests && (
                    <div className="bg-white rounded-xl shadow-lg p-6">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-2xl font-bold text-gray-900">
                                Request History ({requests.length})
                            </h2>
                            {wsConnected && (
                                <span className="text-green-600 text-sm font-semibold flex items-center gap-2">
                                    <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                                    Real-time updates
                                </span>
                            )}
                        </div>

                        {requests.length === 0 ? (
                            <div className="text-center py-12">
                                <div className="text-6xl mb-4">📭</div>
                                <p className="text-gray-500 text-lg">No requests yet</p>
                                <p className="text-gray-400 text-sm">Send a test request to see it appear here!</p>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {requests.map((req, index) => (
                                    <div
                                        key={req.id || index}
                                        className="border-2 border-gray-200 rounded-lg p-5 hover:border-blue-300 transition-colors animate-fadeIn"
                                    >
                                        <div className="flex items-center justify-between mb-4">
                                            <div className="flex items-center gap-3">
                                                <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-bold">
                                                    {req.method}
                                                </span>
                                                {req.ai_mock_response && !req.ai_mock_response.error && (
                                                    <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1">
                                                        🤖 AI Generated
                                                    </span>
                                                )}
                                            </div>
                                            <span className="text-sm text-gray-500">
                                                {new Date(req.timestamp).toLocaleString()}
                                            </span>
                                        </div>

                                        {req.ai_mock_response && !req.ai_mock_response.error && (
                                            <div className="mb-4 bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-200 rounded-lg p-4">
                                                <div className="flex items-center justify-between mb-2">
                                                    <h4 className="font-bold text-purple-900 flex items-center gap-2">
                                                        🤖 AI Mock Response
                                                    </h4>
                                                    <div className="flex items-center gap-3 text-xs">
                                                        <span className="text-purple-700">
                                                            {req.ai_mock_response.tokens_used} tokens
                                                        </span>
                                                        <span className="text-purple-600 font-mono">
                                                            {req.ai_mock_response.ai_model}
                                                        </span>
                                                    </div>
                                                </div>
                                                <pre className="bg-white p-3 rounded border border-purple-200 text-sm overflow-x-auto">
                                                    {JSON.stringify(req.ai_mock_response.mock_response, null, 2)}
                                                </pre>
                                            </div>
                                        )}

                                        {req.ai_mock_response?.rate_limited && (
                                            <div className="mb-4 bg-yellow-50 border-2 border-yellow-300 rounded-lg p-4">
                                                <div className="flex items-center gap-2 text-yellow-800">
                                                    <span className="text-xl">⚠️</span>
                                                    <div>
                                                        <p className="font-semibold">Rate Limit Reached</p>
                                                        <p className="text-sm">{req.ai_mock_response.message}</p>
                                                    </div>
                                                </div>
                                            </div>
                                        )}

                                        <div className="mb-3">
                                            <p className="text-sm font-semibold text-gray-700 mb-2">Request Body:</p>
                                            <pre className="bg-gray-50 p-3 rounded border border-gray-200 text-xs overflow-x-auto">
                                                {req.body_raw || '(empty)'}
                                            </pre>
                                        </div>

                                        <details className="cursor-pointer">
                                            <summary className="text-sm font-semibold text-gray-700 hover:text-gray-900">
                                                📋 Headers (click to expand)
                                            </summary>
                                            <pre className="bg-gray-50 p-3 rounded border border-gray-200 text-xs overflow-x-auto mt-2">
                                                {JSON.stringify(req.headers, null, 2)}
                                            </pre>
                                        </details>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    )
}

export default CreateEndpoint/ /   f o r c e   r e b u i l d  
 