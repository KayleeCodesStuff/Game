import requests

try:
    response = requests.get('https://www.google.com')
    if response.status_code == 200:
        print("Internet access is working.")
    else:
        print("Failed to access the internet.")
except Exception as e:
    print(f"Error: {e}")
