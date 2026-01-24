import os
from anthropic import Anthropic

# Load API key from .env
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

print(f"API Key (first 20 chars): {api_key[:20]}...")
print(f"API Key length: {len(api_key)}")

client = Anthropic(api_key=api_key)

print("\n🔍 Testing API connection...\n")

try:
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=100,
        messages=[
            {"role": "user", "content": "Say 'Hello World' in JSON format"}
        ]
    )
    print("✅ SUCCESS!")
    print("\nResponse:")
    print(message.content[0].text)

except Exception as e:
    print(f"❌ ERROR: {e}")
    print(f"\nError type: {type(e)}")