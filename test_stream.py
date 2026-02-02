import requests
import time
import sys
import json

# User provided configuration
IP = "54.80.85.151"
PORT = "4123" # Fallback to standard port 
URL = f"http://{IP}:{PORT}/v1/audio/speech/stream"

def test_streaming():
    print(f"🚀 Connecting to {URL}...")
    
    # User provided payload
    payload = {
        "input": "Hey Homesoul—good to see you. Hope today’s treating you gently. Take a breath, settle in, and let’s make something cool together. I’m right here, tuned in, steady, and ready whenever you are.",
        "voice": "homesoul",
        "response_format": "wav",
        "speed": 1,
        "stream_format": "audio",
        "exaggeration": 0.25,
        "cfg_weight": 1,
        "temperature": 0.5,
        "streaming_chunk_size": 50,
        "streaming_strategy": "sentence",
        "streaming_buffer_size": 1,
        "streaming_quality": "balanced"
    }

    print(f"📋 Payload: {json.dumps(payload, indent=2)}")

    try:
        start_time = time.time()
        
        # Initiate request with stream=True
        response = requests.post(URL, json=payload, stream=True, timeout=30) # Increased timeout
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Error: {response.text}")
            return

        print("🎧 Receiving stream...")
        
        chunk_count = 0
        total_bytes = 0
        first_byte_received = False
        
        # Iterate over chunks
        for chunk in response.iter_content(chunk_size=None):
            if chunk:
                current_time = time.time()
                elapsed = current_time - start_time
                
                if not first_byte_received:
                    print(f"⚡️ Time to First Byte (Latency): {elapsed*1000:.2f} ms")
                    first_byte_received = True
                
                chunk_size = len(chunk)
                total_bytes += chunk_size
                chunk_count += 1
                
                # Print every chunk to see the flow, or every Nth if too many
                print(f"   📦 Chunk {chunk_count}: {chunk_size} bytes (T+{elapsed:.2f}s)")

        total_time = time.time() - start_time
        print(f"\n✅ Stream Complete!")
        print(f"📊 Summary:")
        print(f"   - Total Time: {total_time:.2f}s")
        print(f"   - Total Size: {total_bytes} bytes")
        print(f"   - Chunks: {chunk_count}")
        if chunk_count > 0:
             print(f"   - Avg Chunk Size: {total_bytes / chunk_count:.1f} bytes")

    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Refused. Is the server running on {IP}:{PORT}?")
    except Exception as e:
        print(f"\n❌ Exception: {e}")

if __name__ == "__main__":
    test_streaming()
