import concurrent.futures
import requests
import time
import json
import statistics

# Configuration
# Configuration
IP = "54.80.85.151"
PORT = "4123"
URL = f"http://{IP}:{PORT}/v1/audio/speech/stream"

PAYLOAD = {
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

def send_request(request_id):
    try:
        start_time = time.time()
        print(f"🚀 [Req {request_id}] STARTING...")
        
        # Use a session for connection pooling, though for 5reqs it matters less, good practice
        with requests.Session() as session:
            response = session.post(URL, json=PAYLOAD, stream=True, timeout=60)
            
            if response.status_code != 200:
                 print(f"❌ [Req {request_id}] FAILED: {response.status_code}")
                 return request_id, False, 0, 0, f"Status {response.status_code}"

            first_byte_time = None
            byte_count = 0
            chunk_count_val = 0
            
            for chunk in response.iter_content(chunk_size=None):
                if chunk:
                    current_time = time.time()
                    if first_byte_time is None:
                        first_byte_time = current_time - start_time
                        print(f"⚡️ [Req {request_id}] TTFB: {first_byte_time*1000:.1f}ms")
                    
                    byte_count += len(chunk)
                    chunk_count_val += 1
            
            total_time = time.time() - start_time
            print(f"✅ [Req {request_id}] DONE in {total_time:.2f}s ({byte_count} bytes)")
            return request_id, True, first_byte_time, total_time, None
        
    except Exception as e:
        print(f"❌ [Req {request_id}] ERROR: {e}")
        return request_id, False, 0, 0, str(e)

def run_concurrent_test(num_requests=5):
    print(f"🔥 Starting load test with {num_requests} concurrent requests to {URL}...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
        futures = [executor.submit(send_request, i+1) for i in range(num_requests)]
        
        results = []
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
            
    # Print stats
    print("\n" + "="*80)
    print(f"{'ID':<5} {'Status':<10} {'TTFB (ms)':<15} {'Total (s)':<15} {'Error'}")
    print("-" * 80)
    
    successful = 0
    ttfbs = []
    totals = []
    
    results.sort(key=lambda x: x[0])
    
    for req_id, success, ttfb, total, error in results:
        status = "✅ OK" if success else "❌ Fail"
        ttfb_ms = f"{ttfb*1000:.1f}" if ttfb else "-"
        total_s = f"{total:.2f}" if total else "-"
        err_str = error if error else ""
        
        print(f"{req_id:<5} {status:<10} {ttfb_ms:<15} {total_s:<15} {err_str}")
        
        if success:
            successful += 1
            ttfbs.append(ttfb * 1000)
            totals.append(total)

    print("-" * 80)
    if successful > 0:
        print(f"📉 Min TTFB: {min(ttfbs):.1f} ms")
        print(f"📈 Max TTFB: {max(ttfbs):.1f} ms")
        print(f"✨ Avg TTFB: {statistics.mean(ttfbs):.1f} ms")
    else:
        print("❌ No successful requests.")

if __name__ == "__main__":
    run_concurrent_test(5)
