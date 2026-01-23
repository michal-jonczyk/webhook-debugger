import {useState} from 'react'

function CreateEndpoint() {
    const [endpointName, setEndpointName] = useState('')
    const [createdEndpoint, setCreatedEndpoint] = useState(null)
    const [requests, setRequests] = useState([])
    const [showRequests, setShowRequests] = useState(false)

    const handleCreate = async () => {
        try {
            const response = await fetch('http://localhost:8000/endpoints', {
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
            const response = await fetch(`http://localhost:8000/endpoints/${createdEndpoint.id}/requests`)
            const data = await response.json()
            console.log('📦 Backend response:', data)
            setRequests(data.requests || [])
            setShowRequests(true)
        } catch (error) {
            console.error('❌ Error loading requests:', error)
        }
    }

    return (
        <div className="max-w-2xl mx-auto p-6">
            <h1 className="text-3xl font-bold mb-8">Create Webhook Endpoint</h1>

            <div className="bg-white rounded-lg shadow p-6">
                <label className="block mb-2 font-medium">
                    Endpoint Name(optional)
                </label>

                <input
                    type="text"
                    value={endpointName}
                    onChange={(e) => setEndpointName(e.target.value)}
                    placeholder="my-webhook"
                    className="w-full border rounded px-4 py-2 mb-4"
                />

                <button
                    onClick={handleCreate}
                    className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600"
                >
                    Create Endpoint
                </button>
            </div>

            {createdEndpoint && (
                <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-6">
                    <h2 className="text-xl font-bold text-green-800 mb-2">
                        ✅ Endpoint Created!
                    </h2>
                    <p className="text-sm text-gray-600 mb-2">Your webhook URL:</p>

                    <div className="flex gap-2 mb-4">
                        <div className="flex-1 bg-white border rounded p-3 font-mono text-sm break-all">
                            {createdEndpoint.url}
                        </div>

                        <button
                            onClick={() => {
                                navigator.clipboard.writeText(createdEndpoint.url)
                                alert('URL copied!')
                            }}
                            className="bg-blue-500 text-white px-4 rounded hover:bg-blue-600"
                        >
                            Copy
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
                                alert('Test request sent!')
                            }}
                            className="bg-green-500 text-white px-4 rounded hover:bg-green-600"
                        >
                            Send Test
                        </button>
                    </div>

                    <button
                        onClick={loadRequests}
                        className="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600"
                    >
                        Show Requests
                    </button>
                </div>
            )}

            {showRequests && (
                <div className="mt-6">
                    <h2 className="text-2xl font-bold mb-4">Request History ({requests.length})</h2>

                    {requests.length === 0 ? (
                        <p className="text-gray-500">No requests yet. Send a test request!</p>
                    ) : (
                        <div className="space-y-4">
                            {requests.map((req, index) => (
                                <div key={index} className="bg-white border rounded-lg p-4">
                                    <div className="flex justify-between mb-2">
                                        <span className="font-bold">{req.method}</span>
                                        <span className="text-sm text-gray-500">
                                            {new Date(req.timestamp).toLocaleString()}
                                        </span>
                                    </div>

                                    <div className="mb-2">
                                        <p className="text-sm font-medium text-gray-600">Body:</p>
                                        <pre className="bg-gray-50 p-2 rounded text-xs overflow-x-auto">
                                            {req.body_raw || 'Empty'}
                                        </pre>
                                    </div>

                                    <div>
                                        <p className="text-sm font-medium text-gray-600">Headers:</p>
                                        <pre className="bg-gray-50 p-2 rounded text-xs overflow-x-auto">
                                            {JSON.stringify(req.headers, null, 2)}
                                        </pre>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}

export default CreateEndpoint