
import urllib.request
import urllib.error
import json
import time
import sys

def verify_gateway():
    url = "http://localhost:8484/sse"
    print(f"Testing connection to {url}...")
    
    try:
        # We expect a 405 Method Not Allowed or similar for GET/POST without correct headers,
        # but for SSE, it should ideally upgrade or at least connect.
        # Actually, the MCP spec for SSE is a GET request with Accept: text/event-stream
        
        req = urllib.request.Request(url, headers={"Accept": "text/event-stream"})
        
        # We won't block reading the stream, just check if we can connect
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"Response Code: {response.getcode()}")
            headers = dict(response.info())
            print(f"Content-Type: {headers.get('Content-Type')}")
            
            if response.getcode() == 200:
                print("SUCCESS: Connected to SSE endpoint.")
                return True
            else:
                print(f"FAILURE: Unexpected status code {response.getcode()}")
                return False
                
    except urllib.error.HTTPError as e:
        # 421 Misdirected Request is what we are trying to fix
        if e.code == 421:
            print("FAILURE: Received 421 Misdirected Request (Host header issue still present).")
            return False
        else:
            print(f"WARNING: HTTP Error {e.code}: {e.reason}")
            # If it's not 421, it might still be 'working' regarding our fix (which was for 421)
            # but we really want a clean 200 for SSE.
            # However, depending on implementation, maybe it needs a session ID or something?
            # Standard MCP SSE is just GET /sse
            return False
            
    except urllib.error.URLError as e:
        print(f"FAILURE: Connection refused or network error: {e.reason}")
        return False
    except Exception as e:
        print(f"FAILURE: unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = verify_gateway()
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
