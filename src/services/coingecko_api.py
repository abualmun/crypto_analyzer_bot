
API_KEY = 'CG-QbiHEtuJRDvmqSGpAiFZcCby'

import requests

class CoinGeckoAPI:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.headers = {
            "accept": "application/json",
            "header": API_KEY,
        }

    def ping(self):
        endpoint = f"{self.base_url}/ping"
        response = requests.get(endpoint, headers=self.headers)

        # Check for request success and return JSON, or raise error.
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    

# Usage Example
if __name__ == "__main__":


    api = CoinGeckoAPI()
    result = api.ping()
    print("API Response:", result)
   


CoinGeckoAPI().ping()