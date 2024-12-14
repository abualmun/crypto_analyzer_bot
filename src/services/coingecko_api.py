
API_KEY = 'CG-QbiHEtuJRDvmqSGpAiFZcCby'

import requests

class CoinGeckoAPI:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": API_KEY,
        }

    def ping(self):
        endpoint = f"{self.base_url}/ping"
        response = requests.get(endpoint, headers=self.headers)

        # Check for request success and return JSON, or raise error.
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_simple_price(self, ids, vs_currencies, include_market_cap=False, include_24hr_vol=False, 
                     include_24hr_change=False, include_last_updated_at=False, precision=None, api_key=API_KEY):
  
        # Makes a GET request to the /simple/price endpoint.

        # Args:
        #     ids (str): Coins' IDs, comma-separated.
        #     vs_currencies (str): Target currency, comma-separated.
        #     include_market_cap (bool, optional): Include market cap. Default is False.
        #     include_24hr_vol (bool, optional): Include 24hr volume. Default is False.
        #     include_24hr_change (bool, optional): Include 24hr change. Default is False.
        #     include_last_updated_at (bool, optional): Include last updated time. Default is False.
        #     precision (str, optional): Decimal places for currency price value.
        #     api_key (str, optional): API key for authorization.

        # Returns:
        #     dict: The JSON response from the API.
    
        endpoint = f"{self.base_url}/simple/price"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        
        params = {
            "ids": ids,
            "vs_currencies": vs_currencies,
            "include_market_cap": str(include_market_cap).lower(),
            "include_24hr_vol": str(include_24hr_vol).lower(),
            "include_24hr_change": str(include_24hr_change).lower(),
            "include_last_updated_at": str(include_last_updated_at).lower(),
            "precision": precision
        }
        
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_token_price(self, id, contract_addresses, vs_currencies, include_market_cap=False, 
                        include_24hr_vol=False, include_24hr_change=False, include_last_updated_at=False, precision=None, api_key=API_KEY):
        endpoint = f"{self.base_url}/simple/token_price/{id}"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        params = {
            "contract_addresses": contract_addresses,
            "vs_currencies": vs_currencies,
            "include_market_cap": str(include_market_cap).lower(),
            "include_24hr_vol": str(include_24hr_vol).lower(),
            "include_24hr_change": str(include_24hr_change).lower(),
            "include_last_updated_at": str(include_last_updated_at).lower(),
            "precision": precision
        }
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def get_supported_vs_currencies(self, api_key=API_KEY):
        endpoint = f"{self.base_url}/simple/supported_vs_currencies"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def get_coins_list(self, include_platform=False, api_key=API_KEY):
        endpoint = f"{self.base_url}/coins/list"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        params = {
            "include_platform": str(include_platform).lower()
        }
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
        
    def get_coins_markets(self, vs_currency, ids=None, category=None, order="market_cap_desc", per_page=100, 
                        page=1, sparkline=False, price_change_percentage=None, locale="en", precision=None, api_key=API_KEY):
        endpoint = f"{self.base_url}/coins/markets"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        params = {
            "vs_currency": vs_currency,
            "ids": ids,
            "category": category,
            "order": order,
            "per_page": per_page,
            "page": page,
            "sparkline": str(sparkline).lower(),
            "price_change_percentage": price_change_percentage,
            "locale": locale,
            "precision": precision
        }
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def get_coin_details(self, id, localization=True, tickers=True, market_data=True, community_data=True, 
                        developer_data=True, sparkline=False, api_key=API_KEY):
        endpoint = f"{self.base_url}/coins/{id}"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        params = {
            "localization": str(localization).lower(),
            "tickers": str(tickers).lower(),
            "market_data": str(market_data).lower(),
            "community_data": str(community_data).lower(),
            "developer_data": str(developer_data).lower(),
            "sparkline": str(sparkline).lower()
        }
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def get_coin_tickers(self, id, exchange_ids=None, include_exchange_logo=False, page=1, order="trust_score_desc", 
                        depth=False, api_key=API_KEY):
        endpoint = f"{self.base_url}/coins/{id}/tickers"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        params = {
            "exchange_ids": exchange_ids,
            "include_exchange_logo": str(include_exchange_logo).lower(),
            "page": page,
            "order": order,
            "depth": str(depth).lower()
        }
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def get_coin_history(self, id, date, localization=True, api_key=API_KEY):
        endpoint = f"{self.base_url}/coins/{id}/history"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        params = {
            "date": date,
            "localization": str(localization).lower()
        }
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def get_coin_market_chart(self, id, vs_currency, days, interval=None, precision=None, api_key=API_KEY):
        endpoint = f"{self.base_url}/coins/{id}/market_chart"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        params = {
            "vs_currency": vs_currency,
            "days": days,
            "interval": interval,
            "precision": precision
        }
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def get_coin_ohlc(self, id, vs_currency, days, precision=None, api_key=API_KEY):
        endpoint = f"{self.base_url}/coins/{id}/ohlc"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        params = {
            "vs_currency": vs_currency,
            "days": days,
            "precision": precision
        }
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_asset_platforms(self, filter=None, api_key=API_KEY):
        endpoint = f"{self.base_url}/asset_platforms"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        params = {
            "filter": filter
        }
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def get_categories_list(self, api_key=API_KEY):
        endpoint = f"{self.base_url}/coins/categories/list"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def get_categories(self, order="market_cap_desc", api_key=API_KEY):
        endpoint = f"{self.base_url}/coins/categories"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        params = {
            "order": order
        }
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def get_exchanges(self, per_page=100, page=1, api_key=API_KEY):
        endpoint = f"{self.base_url}/exchanges"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        params = {
            "per_page": per_page,
            "page": page
        }
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def get_exchange_details(self, id, api_key=API_KEY):
        endpoint = f"{self.base_url}/exchanges/{id}"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def get_exchange_tickers(self, id, coin_ids=None, include_exchange_logo=False, page=1, depth=False, order="trust_score_desc", api_key=API_KEY):
        endpoint = f"{self.base_url}/exchanges/{id}/tickers"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        params = {
            "coin_ids": coin_ids,
            "include_exchange_logo": str(include_exchange_logo).lower(),
            "page": page,
            "depth": str(depth).lower(),
            "order": order
        }
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def get_global(self, api_key=API_KEY):
        endpoint = f"{self.base_url}/global"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def get_global_defi(self, api_key=API_KEY):
        endpoint = f"{self.base_url}/global/decentralized_finance_defi"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def get_exchange_volume_chart(self, id, days, api_key=API_KEY):
        endpoint = f"{self.base_url}/exchanges/{id}/volume_chart"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        params = {
            "days": days
        }
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def get_derivatives(self, api_key=API_KEY):
        endpoint = f"{self.base_url}/derivatives"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def get_derivative_exchanges(self, order="open_interest_btc_desc", per_page=100, page=1, api_key=API_KEY):
        endpoint = f"{self.base_url}/derivatives/exchanges"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        params = {
            "order": order,
            "per_page": per_page,
            "page": page
        }
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def get_derivative_exchange_details(self, id, include_tickers=None, api_key=API_KEY):
        endpoint = f"{self.base_url}/derivatives/exchanges/{id}"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        params = {
            "include_tickers": include_tickers
        }
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def get_derivative_exchanges_list(self, api_key=API_KEY):
        endpoint = f"{self.base_url}/derivatives/exchanges/list"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def get_exchange_rates(self, api_key=API_KEY):
        endpoint = f"{self.base_url}/exchange_rates"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def search(self, query, api_key=API_KEY):
        endpoint = f"{self.base_url}/search"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        params = {
            "query": query
        }
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def get_trending(self, api_key=API_KEY):
        endpoint = f"{self.base_url}/search/trending"
        headers = self.headers.copy()
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


# Usage Example
if __name__ == "__main__":


    api = CoinGeckoAPI()
    result = api.get_trending()
    print(result)
