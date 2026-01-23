import {useState} from 'react'

function CreateEndpoint() {
    const [endpointName, setEndpointName] = useState('')
    const [createdEndpoint, setCreatedEndpoint] = useState(null)

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

                    <div className="flex gap-2">
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
                    </div>
                </div>
            )}
        </div>
    )
}

export default CreateEndpoint