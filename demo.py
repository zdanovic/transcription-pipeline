import time
import requests
import json
import sys

API_URL = "http://localhost:8000/api/v1"

def main():
    if len(sys.argv) < 2:
        print("Usage: python demo.py <path_to_audio_file>")
        sys.exit(1)

    audio_file_path = sys.argv[1]

    print(f"Submitting {audio_file_path} for transcription...")
    
    try:
        with open(audio_file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{API_URL}/transcribe", files=files)
    except FileNotFoundError:
        print(f"Error: File {audio_file_path} not found.")
        sys.exit(1)
    except requests.ConnectionError:
        print("Error: Could not connect to API. Is the server running on localhost:8000?")
        sys.exit(1)
        
    if response.status_code != 200:
        print(f"Error submitting file: {response.text}")
        sys.exit(1)

    data = response.json()
    job_id = data["job_id"]
    print(f"Successfully submitted! Assigned job_id: {job_id}")

    print("Polling for results...")
    while True:
        res = requests.get(f"{API_URL}/jobs/{job_id}")
        if res.status_code != 200:
            print(f"Error fetching job status: {res.text}")
            sys.exit(1)
            
        job_data = res.json()
        status = job_data["status"]
        print(f"Polling... Status: {status}")
        
        if status == "completed":
            print("\nTranscription completed successfully!")
            print(json.dumps(job_data["result"], indent=2))
            break
        elif status == "failed":
            print(f"\nTranscription failed! Error: {job_data.get('error')}")
            break
            
        time.sleep(2)

if __name__ == "__main__":
    main()
