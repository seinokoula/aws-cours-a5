import json
import sys
sys.path.append('..')
from index import handler

def run_test(event_file):
    print(f"\nTesting with {event_file}:")
    print("-" * 50)
    
    with open(event_file, 'r') as f:
        event = json.load(f)
    
    result = handler(event, None)
    print(f"Status Code: {result['statusCode']}")
    print(f"Response: {result['body']}\n")

def main():
    test_files = [
        'test-get-by-id.json',
        'test-get-by-email.json',
        'test-invalid-email.json',
        'test-missing-params.json'
    ]
    
    for test_file in test_files:
        run_test(test_file)

if __name__ == "__main__":
    main()
