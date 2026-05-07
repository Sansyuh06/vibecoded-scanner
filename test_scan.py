import requests
import time
import sys

def test_api_startup():
    base_url = "http://localhost:8000"
    print(f"Checking API at {base_url}...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ API is healthy!")
            print(f"Health status: {response.json()}")
        else:
            print(f"❌ API returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to API: {e}")
        return False
    return True

def trigger_test_scan(target_url="https://example.com"):
    base_url = "http://localhost:8000/api/v1"
    print(f"\nTriggering test scan for {target_url}...")
    
    try:
        response = requests.post(
            f"{base_url}/scans/",
            json={"target_url": target_url}
        )
        
        if response.status_code == 201:
            scan_data = response.json()
            scan_id = scan_data["id"]
            print(f"✅ Scan created successfully! ID: {scan_id}")
            return scan_id
        else:
            print(f"❌ Failed to create scan. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error triggering scan: {e}")
        return None

def monitor_scan(scan_id):
    base_url = "http://localhost:8000/api/v1"
    print(f"\nMonitoring scan {scan_id}...")
    
    max_attempts = 30
    for i in range(max_attempts):
        try:
            response = requests.get(f"{base_url}/scans/{scan_id}")
            if response.status_code == 200:
                data = response.json()
                status = data["status"]
                print(f"Attempt {i+1}: Current status is '{status}'")
                
                if status == "COMPLETED":
                    print("\n✅ Scan COMPLETED!")
                    print(f"Found {data['findings_count']} findings.")
                    for finding in data["findings"]:
                        print(f"  - [{finding['severity']}] {finding['name']}: {finding['description']}")
                    return True
                elif status == "FAILED":
                    print("\n❌ Scan FAILED.")
                    return False
            else:
                print(f"❌ Error checking status. Status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error monitoring scan: {e}")
            
        time.sleep(2)
    
    print("\n⌛ Monitoring timed out.")
    return False

if __name__ == "__main__":
    if test_api_startup():
        scan_id = trigger_test_scan()
        if scan_id:
            monitor_scan(scan_id)
