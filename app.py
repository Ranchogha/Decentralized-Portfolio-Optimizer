import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from web3 import Web3
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from web3_integration import EthereumPortfolioManager
from wallet_manager import MultiWalletManager
import time
import hashlib

# Load environment variables
load_dotenv()

# --- Enhanced CoinGecko API Integration ---
class CoinGeckoAPI:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.api_key = os.getenv("COINGECKO_API_KEY")
        self.session = requests.Session()
        
        # Add headers for better API performance and authentication
        self.session.headers.update({
            'User-Agent': 'Decentralized-Portfolio-Optimizer/1.0',
            'Accept': 'application/json'
        })
        
        # Add API key to headers if available (Recommended method)
        if self.api_key:
            self.session.headers.update({
                'x-cg-demo-api-key': self.api_key
            })
        else:
            pass
    
    def _handle_api_response(self, response, endpoint_name):
        """Handle API responses with proper error handling"""
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            try:
                st.error(f"Rate limit exceeded for {endpoint_name}. Please wait before making more requests.")
            except:
                print(f"Rate limit exceeded for {endpoint_name}. Please wait before making more requests.")
            return None
        elif response.status_code == 403:
            try:
                st.error(f"Access forbidden for {endpoint_name}. Check your API key.")
            except:
                print(f"Access forbidden for {endpoint_name}. Check your API key.")
            return None
        elif response.status_code == 401:
            try:
                st.error(f"Unauthorized for {endpoint_name}. Check your API key.")
            except:
                print(f"Unauthorized for {endpoint_name}. Check your API key.")
            return None
        else:
            try:
                st.error(f"Error {response.status_code} for {endpoint_name}: {response.text}")
            except:
                print(f"Error {response.status_code} for {endpoint_name}: {response.text}")
            return None
    
    def ping_server(self):
        """Check API server status using the ping endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/ping")
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'online',
                    'message': data.get('gecko_says', 'API server is online'),
                    'response_time': response.elapsed.total_seconds()
                }
            else:
                return {
                    'status': 'error',
                    'message': f'API server returned status code: {response.status_code}',
                    'response_time': response.elapsed.total_seconds()
                }
        except Exception as e:
            return {
                'status': 'offline',
                'message': f'Cannot connect to API server: {str(e)}',
                'response_time': None
            }
    
    def get_simple_price(self, ids, vs_currencies='usd', include_market_cap=False, 
                        include_24hr_vol=False, include_24hr_change=False, 
                        include_last_updated_at=False):
        """
        Get simple price data for coins by their IDs
        Based on: https://docs.coingecko.com/v3.0.1/reference/simple-price
        """
        try:
            params = {
                'ids': ','.join(ids) if isinstance(ids, list) else ids,
                'vs_currencies': vs_currencies,
                'include_market_cap': str(include_market_cap).lower(),
                'include_24hr_vol': str(include_24hr_vol).lower(),
                'include_24hr_change': str(include_24hr_change).lower(),
                'include_last_updated_at': str(include_last_updated_at).lower()
            }
            
            response = self.session.get(f"{self.base_url}/simple/price", params=params)
            result = self._handle_api_response(response, "simple/price")
            return result if result else {}
        except Exception as e:
            st.error(f"Error fetching simple price data: {str(e)}")
            return {}
    
    def get_token_price(self, platform_id, contract_addresses, vs_currencies='usd',
                       include_market_cap=False, include_24hr_vol=False, 
                       include_24hr_change=False, include_last_updated_at=False):
        """
        Get token prices by contract addresses
        Based on: https://docs.coingecko.com/v3.0.1/reference/simple-token-price
        """
        try:
            params = {
                'contract_addresses': ','.join(contract_addresses) if isinstance(contract_addresses, list) else contract_addresses,
                'vs_currencies': vs_currencies,
                'include_market_cap': str(include_market_cap).lower(),
                'include_24hr_vol': str(include_24hr_vol).lower(),
                'include_24hr_change': str(include_24hr_change).lower(),
                'include_last_updated_at': str(include_last_updated_at).lower()
            }
            
            response = self.session.get(f"{self.base_url}/simple/token_price/{platform_id}", params=params)
            result = self._handle_api_response(response, f"simple/token_price/{platform_id}")
            return result if result else {}
        except Exception as e:
            st.error(f"Error fetching token price data: {str(e)}")
            return {}
    
    def get_supported_vs_currencies(self):
        """
        Get list of supported vs currencies
        Based on: https://docs.coingecko.com/v3.0.1/reference/simple-supported-currencies
        """
        try:
            response = self.session.get(f"{self.base_url}/simple/supported_vs_currencies")
            result = self._handle_api_response(response, "simple/supported_vs_currencies")
            return result if result else []
        except Exception as e:
            st.error(f"Error fetching supported currencies: {str(e)}")
            return []
    
    def get_coins_list(self, include_platform=False):
        """
        Get list of all supported coins with ID, name and symbol
        Based on: https://docs.coingecko.com/v3.0.1/reference/coins-list
        """
        try:
            params = {'include_platform': str(include_platform).lower()}
            response = self.session.get(f"{self.base_url}/coins/list", params=params)
            result = self._handle_api_response(response, "coins/list")
            return result if result else []
        except Exception as e:
            st.error(f"Error fetching coins list: {str(e)}")
            return []
    
    def get_coins_markets(self, vs_currency="usd", ids=None, category=None, order="market_cap_desc", 
                          per_page=100, page=1, sparkline=False, price_change_percentage="24h", 
                          include_tokens=None):
        """
        Get coins list with market data
        Based on: https://docs.coingecko.com/v3.0.1/reference/coins-markets
        """
        try:
            params = {
                'vs_currency': vs_currency,
                'order': order,
                'per_page': per_page,
                'page': page,
                'sparkline': str(sparkline).lower(),
                'price_change_percentage': price_change_percentage
            }
            
            if ids:
                params['ids'] = ','.join(ids) if isinstance(ids, list) else ids
            if category:
                params['category'] = category
            if include_tokens:
                params['include_tokens'] = include_tokens
            
            # Check cache first
            cached_result = api_cache.get("coins/markets", params)
            if cached_result:
                return cached_result
            
            # Check rate limit
            if not rate_limiter.can_make_call():
                st.warning("Rate limit approaching. Please wait before making more requests.")
                return []
            
            response = self.session.get(f"{self.base_url}/coins/markets", params=params)
            result = self._handle_api_response(response, "coins/markets")
            
            # Cache the result
            if result:
                api_cache.set("coins/markets", result, params)
            
            return result if result else []
        except Exception as e:
            try:
                st.error(f"Error fetching coins markets: {str(e)}")
            except:
                print(f"Error fetching coins markets: {str(e)}")
            return []
    
    def get_coin_data(self, coin_id, localization=True, tickers=True, market_data=True, 
                      community_data=True, developer_data=True, sparkline=False):
        """
        Get detailed coin data by ID
        Based on: https://docs.coingecko.com/v3.0.1/reference/coins-id
        """
        try:
            params = {
                'localization': str(localization).lower(),
                'tickers': str(tickers).lower(),
                'market_data': str(market_data).lower(),
                'community_data': str(community_data).lower(),
                'developer_data': str(developer_data).lower(),
                'sparkline': str(sparkline).lower()
            }
            
            response = self.session.get(f"{self.base_url}/coins/{coin_id}", params=params)
            result = self._handle_api_response(response, f"coins/{coin_id}")
            return result if result else {}
        except Exception as e:
            st.error(f"Error fetching coin data: {str(e)}")
            return {}
    
    def get_coin_tickers(self, coin_id, exchange_ids=None, include_exchange_logo=False, 
                        page=1, order="trust_score_desc", depth=False):
        """
        Get coin tickers by ID
        Based on: https://docs.coingecko.com/v3.0.1/reference/coins-id-tickers
        """
        try:
            params = {
                'include_exchange_logo': str(include_exchange_logo).lower(),
                'page': page,
                'order': order,
                'depth': str(depth).lower()
            }
            
            if exchange_ids:
                params['exchange_ids'] = ','.join(exchange_ids) if isinstance(exchange_ids, list) else exchange_ids
            
            response = self.session.get(f"{self.base_url}/coins/{coin_id}/tickers", params=params)
            result = self._handle_api_response(response, f"coins/{coin_id}/tickers")
            return result if result else {}
        except Exception as e:
            st.error(f"Error fetching coin tickers: {str(e)}")
            return {}
    
    def get_coin_history(self, coin_id, date, localization=True):
        """
        Get historical data for a coin at a specific date
        Based on: https://docs.coingecko.com/v3.0.1/reference/coins-id-history
        """
        try:
            params = {
                'date': date,
                'localization': str(localization).lower()
            }
            
            response = self.session.get(f"{self.base_url}/coins/{coin_id}/history", params=params)
            result = self._handle_api_response(response, f"coins/{coin_id}/history")
            return result if result else {}
        except Exception as e:
            st.error(f"Error fetching coin history: {str(e)}")
            return {}
    
    def get_coin_market_chart(self, coin_id, vs_currency="usd", days=30):
        """
        Get historical chart data for a coin
        Based on: https://docs.coingecko.com/v3.0.1/reference/coins-id-market-chart
        """
        try:
            params = {
                'vs_currency': vs_currency,
                'days': days
            }
            
            response = self.session.get(f"{self.base_url}/coins/{coin_id}/market_chart", params=params)
            result = self._handle_api_response(response, f"coins/{coin_id}/market_chart")
            return result if result else {}
        except Exception as e:
            st.error(f"Error fetching coin market chart: {str(e)}")
            return {}
    
    def get_coin_market_chart_range(self, coin_id, vs_currency="usd", from_timestamp=None, to_timestamp=None):
        """
        Get historical chart data for a coin within a time range
        Based on: https://docs.coingecko.com/v3.0.1/reference/coins-id-market-chart-range
        """
        try:
            params = {
                'vs_currency': vs_currency
            }
            
            if from_timestamp:
                params['from'] = from_timestamp
            if to_timestamp:
                params['to'] = to_timestamp
            
            response = self.session.get(f"{self.base_url}/coins/{coin_id}/market_chart/range", params=params)
            result = self._handle_api_response(response, f"coins/{coin_id}/market_chart/range")
            return result if result else {}
        except Exception as e:
            st.error(f"Error fetching coin market chart range: {str(e)}")
            return {}
    
    def get_coin_ohlc(self, coin_id, vs_currency="usd", days=30):
        """
        Get OHLC chart data for a coin
        Based on: https://docs.coingecko.com/v3.0.1/reference/coins-id-ohlc
        """
        try:
            params = {
                'vs_currency': vs_currency,
                'days': days
            }
            
            response = self.session.get(f"{self.base_url}/coins/{coin_id}/ohlc", params=params)
            result = self._handle_api_response(response, f"coins/{coin_id}/ohlc")
            return result if result else []
        except Exception as e:
            st.error(f"Error fetching coin OHLC: {str(e)}")
            return []
    
    def get_coin_data_by_contract(self, platform_id, contract_address):
        """
        Get coin data by token contract address
        Based on: https://docs.coingecko.com/v3.0.1/reference/coins-contract-address
        """
        try:
            response = self.session.get(f"{self.base_url}/coins/{platform_id}/contract/{contract_address}")
            result = self._handle_api_response(response, f"coins/{platform_id}/contract/{contract_address}")
            return result if result else {}
        except Exception as e:
            st.error(f"Error fetching coin data by contract: {str(e)}")
            return {}
    
    def get_contract_market_chart(self, platform_id, contract_address, vs_currency="usd", days=30):
        """
        Get historical chart data by token contract address
        Based on: https://docs.coingecko.com/v3.0.1/reference/contract-address-market-chart
        """
        try:
            params = {
                'vs_currency': vs_currency,
                'days': days
            }
            
            response = self.session.get(f"{self.base_url}/coins/{platform_id}/contract/{contract_address}/market_chart", params=params)
            result = self._handle_api_response(response, f"coins/{platform_id}/contract/{contract_address}/market_chart")
            return result if result else {}
        except Exception as e:
            st.error(f"Error fetching contract market chart: {str(e)}")
            return {}
    
    def get_contract_market_chart_range(self, platform_id, contract_address, vs_currency="usd", from_timestamp=None, to_timestamp=None):
        """
        Get historical chart data within time range by token contract address
        Based on: https://docs.coingecko.com/v3.0.1/reference/contract-address-market-chart-range
        """
        try:
            params = {
                'vs_currency': vs_currency
            }
            
            if from_timestamp:
                params['from'] = from_timestamp
            if to_timestamp:
                params['to'] = to_timestamp
            
            response = self.session.get(f"{self.base_url}/coins/{platform_id}/contract/{contract_address}/market_chart/range", params=params)
            result = self._handle_api_response(response, f"coins/{platform_id}/contract/{contract_address}/market_chart/range")
            return result if result else {}
        except Exception as e:
            st.error(f"Error fetching contract market chart range: {str(e)}")
            return {}
    

    
    def get_trending_coins(self):
        """
        Get trending search coins, NFTs and categories on CoinGecko in the last 24 hours
        Based on: https://docs.coingecko.com/v3.0.1/reference/trending-search
        
        Returns:
            dict: Trending data containing:
                - coins: Top 15 trending coins (sorted by most popular user searches)
                - nfts: Top 7 trending NFTs (sorted by highest percentage change in floor prices)
                - categories: Top 5 trending categories (sorted by most popular user searches)
                
        Cache/Update Frequency: every 10 minutes for all API plans
        """
        try:
            response = self.session.get(f"{self.base_url}/search/trending")
            result = self._handle_api_response(response, "search/trending")
            if result:
                return result
            return {}
        except Exception as e:
            st.error(f"Error fetching trending coins: {str(e)}")
            return {}
    
    def get_categories(self):
        """
        Get coin categories list (ID Map)
        Based on: https://docs.coingecko.com/v3.0.1/reference/coins-categories-list
        """
        try:
            response = self.session.get(f"{self.base_url}/coins/categories/list")
            result = self._handle_api_response(response, "coins/categories/list")
            return result if result else []
        except Exception as e:
            st.error(f"Error fetching categories: {str(e)}")
            return []
    
    def get_categories_with_market_data(self):
        """
        Get coin categories with market data (market cap, volume, ...)
        Based on: https://docs.coingecko.com/v3.0.1/reference/coins-categories
        """
        try:
            response = self.session.get(f"{self.base_url}/coins/categories")
            result = self._handle_api_response(response, "coins/categories")
            return result if result else []
        except Exception as e:
            st.error(f"Error fetching categories with market data: {str(e)}")
            return []
    
    def get_global_market_data(self):
        """
        Get cryptocurrency global data including active cryptocurrencies, markets, total crypto market cap and etc
        Based on: https://docs.coingecko.com/v3.0.1/reference/crypto-global
        
        Returns:
            dict: Global market data including:
                - active_cryptocurrencies: Number of active cryptocurrencies
                - total_market_cap: Total market cap in USD
                - total_volume: Total 24h volume in USD
                - market_cap_percentage: Market cap percentage by currency
                - market_cap_change_percentage_24h_usd: 24h market cap change percentage
                
        Cache/Update Frequency: every 10 minutes for all API plans
        """
        try:
            # Check cache first
            cached_result = api_cache.get("global")
            if cached_result:
                return cached_result
            
            # Check rate limit
            if not rate_limiter.can_make_call():
                st.warning("Rate limit approaching. Please wait before making more requests.")
                return {}
            
            response = self.session.get(f"{self.base_url}/global")
            result = self._handle_api_response(response, "global")
            
            # Cache the result
            if result:
                api_cache.set("global", result)
            
            return result if result else {}
        except Exception as e:
            try:
                st.error(f"Error fetching global market data: {str(e)}")
            except:
                print(f"Error fetching global market data: {str(e)}")
            return {}
    
    def get_defi_market_data(self):
        """
        Get top 100 cryptocurrency global decentralized finance (DeFi) data including DeFi market cap, trading volume
        Based on: https://docs.coingecko.com/v3.0.1/reference/global-defi
        
        Returns:
            dict: DeFi market data including:
                - defi_market_cap: Total DeFi market cap in USD
                - defi_24h_volume: Total DeFi 24h volume in USD
                - defi_market_cap_change_24h: 24h DeFi market cap change
                - defi_24h_volume_change_24h: 24h DeFi volume change
                - top_100_coins: Top 100 DeFi coins data
                
        Cache/Update Frequency: every 60 minutes for all API plans
        """
        try:
            response = self.session.get(f"{self.base_url}/global/decentralized_finance_defi")
            result = self._handle_api_response(response, "global/decentralized_finance_defi")
            if result and 'data' in result:
                # Ensure numeric values for DeFi data
                data = result['data']
                if 'defi_market_cap' in data:
                    try:
                        data['defi_market_cap'] = float(data['defi_market_cap'])
                    except (ValueError, TypeError):
                        data['defi_market_cap'] = 0
                if 'defi_24h_volume' in data:
                    try:
                        data['defi_24h_volume'] = float(data['defi_24h_volume'])
                    except (ValueError, TypeError):
                        data['defi_24h_volume'] = 0
            return result if result else {}
        except Exception as e:
            try:
                st.error(f"Error fetching DeFi market data: {str(e)}")
            except:
                print(f"Error fetching DeFi market data: {str(e)}")
            return {}
    
    def get_public_companies_holdings(self, coin_id):
        """
        Get public companies' Bitcoin or Ethereum holdings
        Based on: https://docs.coingecko.com/v3.0.1/reference/companies-public-treasury
        
        Args:
            coin_id (str): The coin id (e.g., 'bitcoin', 'ethereum')
            
        Returns:
            dict: Public companies holdings data including:
                - companies: List of companies with holdings
                - total_holdings: Total holdings in the specified coin
                - total_value_usd: Total value in USD
                
        Cache/Update Frequency: every 60 minutes for all API plans
        """
        try:
            # First try with API key
            response = self.session.get(f"{self.base_url}/companies/public_treasury/{coin_id}")
            result = self._handle_api_response(response, f"companies/public_treasury/{coin_id}")
            if result:
                return result
            
            # If failed, retry without API key
            print(f"Retrying {coin_id} holdings without API key...")
            response = requests.get(f"{self.base_url}/companies/public_treasury/{coin_id}")
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            try:
                st.error(f"Error fetching public companies holdings: {str(e)}")
            except:
                print(f"Error fetching public companies holdings: {str(e)}")
            return {}

# Initialize API client
api_client = CoinGeckoAPI()

# Rate limiting for API calls
import time
import hashlib
import json
from datetime import datetime, timedelta

class APICache:
    """Cache for API responses to reduce rate limiting"""
    def __init__(self, cache_ttl=300):  # 5 minutes default TTL
        self.cache = {}
        self.cache_ttl = cache_ttl
    
    def _generate_cache_key(self, endpoint, params=None):
        """Generate unique cache key for endpoint and parameters"""
        key_data = f"{endpoint}:{json.dumps(params, sort_keys=True) if params else ''}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, endpoint, params=None):
        """Get cached response if available and not expired"""
        cache_key = self._generate_cache_key(endpoint, params)
        
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < timedelta(seconds=self.cache_ttl):
                return cached_data['data']
            else:
                # Remove expired cache entry
                del self.cache[cache_key]
        
        return None
    
    def set(self, endpoint, data, params=None):
        """Cache response data with timestamp"""
        cache_key = self._generate_cache_key(endpoint, params)
        self.cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def clear(self):
        """Clear all cached data"""
        self.cache.clear()
    
    def get_cache_stats(self):
        """Get cache statistics"""
        return {
            'total_entries': len(self.cache),
            'cache_ttl': self.cache_ttl,
            'memory_usage': len(json.dumps(self.cache))
        }

class RateLimiter:
    def __init__(self, max_calls=25, time_window=60):  # Conservative rate limit
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def can_make_call(self):
        now = time.time()
        # Remove old calls outside the time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False
    
    def wait_if_needed(self):
        if not self.can_make_call():
            wait_time = self.time_window - (time.time() - self.calls[0])
            if wait_time > 0:
                time.sleep(wait_time)
            return self.can_make_call()
        return True

# Initialize rate limiter and cache
rate_limiter = RateLimiter()
api_cache = APICache(cache_ttl=300)  # 5 minutes cache TTL

# Initialize wallet manager
wallet_manager = MultiWalletManager()

# --- Enhanced Portfolio Optimization Logic ---
class PortfolioOptimizer:
    def __init__(self):
        self.risk_profiles = {
            "low": {"volatility_threshold": 0.15, "max_single_asset": 0.4, "stablecoin_min": 0.3},
            "medium": {"volatility_threshold": 0.25, "max_single_asset": 0.5, "stablecoin_min": 0.1},
            "high": {"volatility_threshold": 0.4, "max_single_asset": 0.7, "stablecoin_min": 0.0}
        }
        
        # Enhanced sector categories based on CoinGecko data
        self.sector_categories = {
            "DeFi": ["aave", "uniswap", "compound", "maker", "curve-dao-token", "synthetix", "yearn-finance", "balancer"],
            "Layer 1": ["bitcoin", "ethereum", "solana", "cardano", "polkadot", "avalanche-2", "cosmos", "algorand"],
            "Layer 2": ["matic-network", "arbitrum", "optimism", "base", "polygon", "loopring"],
            "Stablecoins": ["tether", "usd-coin", "dai", "binance-usd", "true-usd", "frax"],
            "AI": ["fetch-ai", "ocean-protocol", "singularitynet", "artificial-intelligence", "cortex", "numerai"],
            "Meme": ["dogecoin", "shiba-inu", "pepe", "floki", "bonk", "dogwifhat"],
            "Gaming": ["axie-infinity", "the-sandbox", "decentraland", "enjin-coin", "gala", "illuvium"],
            "Infrastructure": ["chainlink", "filecoin", "the-graph", "helium", "render-token", "akash-network"]
        }
    
    def calculate_volatility(self, historical_data):
        """Calculate price volatility from historical data"""
        if not historical_data or len(historical_data) < 2:
            return 0.5  # Default high volatility if no data
        
        prices = [price[1] for price in historical_data]
        returns = np.diff(prices) / prices[:-1]
        return np.std(returns)
    
    def optimize_portfolio(self, risk_profile, investment_amount, preferred_sectors, max_assets=10):
        """AI-powered portfolio optimization with enhanced sector filtering"""
        try:
            # Check rate limit before making API calls
            if not rate_limiter.can_make_call():
                st.warning("Rate limit approaching. Please wait before making more requests.")
                return {}, []
            
            # Fetch market data
            market_data = api_client.get_coins_markets(per_page=200)
            
            if not market_data:
                st.error("Failed to fetch market data")
                return {}, []
            
            # Filter by preferred sectors
            available_assets = []
            for sector in preferred_sectors:
                if sector in self.sector_categories:
                    sector_coins = self.sector_categories[sector]
                    for coin in market_data:
                        if coin['id'] in sector_coins:
                            available_assets.append(coin)
            
            if not available_assets:
                st.warning("No assets found for selected sectors. Using top market cap coins.")
                available_assets = market_data[:20]
            
            # Calculate volatility for each asset
            assets_with_volatility = []
            for asset in available_assets[:30]:  # Limit to top 30 for performance
                try:
                    historical_data = api_client.get_coin_market_chart(asset['id'])
                    volatility = self.calculate_volatility(historical_data.get('prices', []))
                    assets_with_volatility.append({
                        **asset,
                        'volatility': volatility,
                        'historical_data': historical_data.get('prices', [])
                    })
                except Exception as e:
                    st.warning(f"Could not fetch data for {asset['name']}: {str(e)}")
                    continue
            
            # Apply risk-based filtering
            risk_config = self.risk_profiles[risk_profile]
            filtered_assets = [
                asset for asset in assets_with_volatility
                if asset['volatility'] <= risk_config['volatility_threshold']
            ]
            
            if not filtered_assets:
                st.warning("No assets meet volatility criteria. Using all available assets.")
                filtered_assets = assets_with_volatility
            
            # Sort by market cap and limit assets
            filtered_assets.sort(key=lambda x: x['market_cap'], reverse=True)
            selected_assets = filtered_assets[:max_assets]
            
            # Generate allocation based on risk profile
            allocation = self._generate_allocation(selected_assets, risk_profile, investment_amount)
            
            return allocation, selected_assets
            
        except Exception as e:
            st.error(f"Error optimizing portfolio: {str(e)}")
            return {}, []
    
    def _generate_allocation(self, assets, risk_profile, investment_amount):
        """Generate optimal allocation based on risk profile"""
        allocation = {}
        
        if risk_profile == "low":
            # Conservative allocation with stablecoins
            stablecoins = [a for a in assets if a['id'] in self.sector_categories['Stablecoins']]
            if stablecoins:
                allocation[stablecoins[0]['id']] = 0.4
            
            # Add blue-chip cryptocurrencies
            blue_chips = [a for a in assets if a['id'] in ['bitcoin', 'ethereum']]
            for i, asset in enumerate(blue_chips[:2]):
                allocation[asset['id']] = 0.3 - (i * 0.1)
            
            # Add diversified assets
            remaining_assets = [a for a in assets if a['id'] not in allocation]
            remaining_weight = 1 - sum(allocation.values())
            for i, asset in enumerate(remaining_assets[:3]):
                weight = remaining_weight / min(3, len(remaining_assets))
                allocation[asset['id']] = weight
        
        elif risk_profile == "medium":
            # Balanced allocation
            total_weight = 0
            for i, asset in enumerate(assets[:5]):
                weight = 0.25 - (i * 0.05)
                if weight > 0:
                    allocation[asset['id']] = weight
                    total_weight += weight
            
            # Normalize weights
            if total_weight > 0:
                for asset_id in allocation:
                    allocation[asset_id] = allocation[asset_id] / total_weight
        
        else:  # High risk
            # Aggressive allocation with higher weights to top assets
            for i, asset in enumerate(assets[:4]):
                weight = 0.4 - (i * 0.1)
                if weight > 0:
                    allocation[asset['id']] = weight
            
            # Normalize weights
            total_weight = sum(allocation.values())
            if total_weight > 0:
                for asset_id in allocation:
                    allocation[asset_id] = allocation[asset_id] / total_weight
        
        return allocation

# Initialize optimizer
optimizer = PortfolioOptimizer()

# --- Enhanced Web3 Integration for Ethereum ---
class EthereumIntegration:
    def __init__(self):
        self.w3 = None
        self.contract = None
        self.contract_address = None
        self.account = None
        
        # Try to connect to Ethereum network
        try:
            rpc_url = os.getenv("ETHEREUM_RPC_URL")
            if rpc_url:
                self.w3 = Web3(Web3.HTTPProvider(rpc_url))
                if self.w3.is_connected():
                    st.success("✅ Connected to Ethereum network")
                else:
                    st.warning("⚠️ Ethereum connection not available")
            else:
                st.info("ℹ️ Ethereum RPC URL not configured")
        except Exception as e:
            st.warning(f"⚠️ Ethereum connection not available: {str(e)}")
    
    def save_portfolio_allocation(self, portfolio_data, risk_profile, sectors):
        """Save portfolio allocation to Ethereum blockchain"""
        if not self.w3:
            st.error("Ethereum connection not available")
            return False
        
        try:
            # Prepare portfolio data for blockchain
            allocation_data = {
                "timestamp": datetime.now().isoformat(),
                "portfolio": portfolio_data,
                "risk_profile": risk_profile,
                "sectors": sectors,
                "blockchain": "ethereum"
            }
            
            st.success("✅ Portfolio allocation data prepared for blockchain storage")
            st.json(allocation_data)
            return True
            
        except Exception as e:
            st.error(f"Error saving to blockchain: {str(e)}")
            return False

# Initialize Web3 with build artifacts support
portfolio_manager = EthereumPortfolioManager()

# --- Enhanced Streamlit Web Application ---
st.set_page_config(
    page_title="Decentralized Portfolio Optimizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better web app styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    .sector-toggle {
        background: #e8f4fd;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🚀 Decentralized Portfolio Optimizer</h1>
    <p>AI-powered portfolio management using CoinGecko MCP and Ethereum blockchain</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for user inputs
with st.sidebar:
    st.header("📋 Portfolio Configuration")
    
    # Risk Profile Selection
    risk_profile = st.selectbox(
        "Risk Profile",
        ["low", "medium", "high"],
        help="Low: Conservative with stablecoins, Medium: Balanced, High: Aggressive growth"
    )
    
    # Investment Amount
    investment_amount = st.number_input(
        "Investment Amount (USD)",
        min_value=100,
        value=10000,
        step=100,
        help="Total amount to invest across the portfolio"
    )
    
    # Enhanced Sector Selection with Toggles
    st.subheader("🏢 Sector Selection")
    st.markdown("Toggle sectors to include in your portfolio:")
    
    sector_options = {
        "DeFi": "Decentralized Finance protocols",
        "Layer 1": "Base blockchain networks",
        "Layer 2": "Scaling solutions",
        "Stablecoins": "Price-stable cryptocurrencies",
        "AI": "Artificial Intelligence tokens",
        "Gaming": "Gaming and metaverse tokens",
        "Infrastructure": "Blockchain infrastructure"
    }
    
    selected_sectors = []
    for sector, description in sector_options.items():
        if st.checkbox(f"{sector}", value=sector in ["DeFi", "Layer 1"], help=description):
            selected_sectors.append(sector)
    
    if not selected_sectors:
        st.warning("Please select at least one sector")
        selected_sectors = ["DeFi", "Layer 1"]
    
    # Portfolio Size
    max_assets = st.slider(
        "Maximum Assets",
        min_value=3,
        max_value=15,
        value=8,
        help="Maximum number of assets in the portfolio"
    )
    
    # Blockchain Integration
    st.subheader("🔗 Blockchain Features")
    
    # Show blockchain connection status
    network_info = portfolio_manager.get_network_info()
    
    save_to_blockchain = st.checkbox(
        "Save to Ethereum Blockchain",
        value=False,
        help="Store portfolio allocation on Ethereum blockchain"
    )
    
    # Wallet Connection Section
    st.subheader("💼 Wallet Connection")
    wallet_manager.render_wallet_connection_ui()
    
    # Market Data Refresh
    if st.button("🔄 Refresh Market Data"):
        st.rerun()

# Developer-only API Status Check (hidden from users)
if os.getenv("DEBUG", "false").lower() == "true":
    with st.sidebar:
        st.subheader("🔧 Developer API Status")
        
        # Use the proper ping endpoint to check API server status
        ping_result = api_client.ping_server()
        
        if ping_result['status'] == 'online':
            st.success(f"✅ {ping_result['message']}")
            if ping_result['response_time']:
                st.info(f"⏱️ Response time: {ping_result['response_time']:.3f}s")
        elif ping_result['status'] == 'error':
            st.error(f"❌ {ping_result['message']}")
        else:
            st.error(f"❌ {ping_result['message']}")
        
        # Rate limit status
        remaining_calls = rate_limiter.max_calls - len(rate_limiter.calls)
        st.info(f"📊 API Calls: {remaining_calls}/{rate_limiter.max_calls} remaining")
        
        # Cache statistics
        cache_stats = api_cache.get_cache_stats()
        st.info(f"💾 Cache: {cache_stats['total_entries']} entries, TTL: {cache_stats['cache_ttl']}s")
        
        # Additional API status info
        if ping_result['status'] == 'online':
            st.success("🟢 API Server Status: Healthy")
        else:
            st.error("🔴 API Server Status: Unhealthy")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Tab for different functionalities
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Portfolio Optimization", "💰 Price Queries", "🪙 Coins API", "🔗 Contract API", "🔗 Blockchain Operations"])
    
    with tab1:
        st.subheader("🎯 Portfolio Generation")
        
        if st.button("🚀 Generate Optimized Portfolio", type="primary", use_container_width=True):
            with st.spinner("Analyzing market data and optimizing portfolio..."):
                allocation, selected_assets = optimizer.optimize_portfolio(
                    risk_profile, investment_amount, selected_sectors, max_assets
                )
            
            if allocation and selected_assets:
                st.success("✅ Portfolio optimized successfully!")
                
                # Create asset details dataframe
                asset_details = []
                for asset in selected_assets:
                    if asset['id'] in allocation:
                        asset_details.append({
                            'Asset': asset['name'],
                            'Symbol': asset['symbol'].upper(),
                            'Allocation %': round(allocation[asset['id']] * 100, 2),
                            'Amount (USD)': round(allocation[asset['id']] * investment_amount, 2),
                            'Current Price': f"${asset['current_price']:,.2f}",
                            'Market Cap': f"${asset['market_cap']:,.0f}",
                            '24h Change': f"{asset['price_change_percentage_24h']:.2f}%",
                            'Volatility': f"{asset.get('volatility', 0):.3f}"
                        })
                
                df = pd.DataFrame(asset_details)
                
                # Display portfolio summary
                st.subheader("📊 Portfolio Summary")
                col_sum1, col_sum2, col_sum3 = st.columns(3)
                
                with col_sum1:
                    st.metric("Total Investment", f"${investment_amount:,.2f}")
                
                with col_sum2:
                    st.metric("Number of Assets", len(allocation))
                
                with col_sum3:
                    total_allocation = sum(allocation.values())
                    st.metric("Total Allocation", f"{total_allocation*100:.1f}%")
                
                # Portfolio table
                st.dataframe(df, use_container_width=True)
                
                # Enhanced Visualizations
                st.subheader("📈 Portfolio Visualizations")
                
                # Pie Chart
                fig_pie = px.pie(
                    df, 
                    values='Amount (USD)', 
                    names='Asset',
                    title=f"Portfolio Allocation - {risk_profile.title()} Risk Profile",
                    hover_data=['Allocation %']
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
                
                # Historical Performance Chart
                if selected_assets:
                    st.subheader("📈 Historical Performance (30 Days)")
                    
                    fig_line = go.Figure()
                    
                    for asset in selected_assets[:5]:  # Limit to top 5 for clarity
                        if asset['id'] in allocation and asset.get('historical_data'):
                            historical_data = asset['historical_data']
                            if len(historical_data) > 1:
                                timestamps = [pd.to_datetime(price[0], unit='ms') for price in historical_data]
                                prices = [price[1] for price in historical_data]
                                
                                # Normalize prices to percentage change
                                if prices[0] > 0:
                                    normalized_prices = [(p / prices[0] - 1) * 100 for p in prices]
                                    
                                    fig_line.add_trace(
                                        go.Scatter(
                                            x=timestamps,
                                            y=normalized_prices,
                                            name=f"{asset['name']} ({asset['symbol'].upper()})",
                                            mode='lines'
                                        )
                                    )
                    
                    fig_line.update_layout(
                        title="30-Day Price Performance (Normalized)",
                        xaxis_title="Date",
                        yaxis_title="Price Change (%)",
                        height=500,
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig_line, use_container_width=True)
                
                # Risk Metrics
                st.subheader("⚖️ Risk Analysis")
                col_risk1, col_risk2, col_risk3 = st.columns(3)
                
                with col_risk1:
                    avg_volatility = np.mean([asset.get('volatility', 0) for asset in selected_assets if asset['id'] in allocation])
                    st.metric("Average Volatility", f"{avg_volatility:.3f}")
                
                with col_risk2:
                    portfolio_diversity = len(allocation)
                    st.metric("Portfolio Diversity", f"{portfolio_diversity} assets")
                
                with col_risk3:
                    max_allocation = max(allocation.values()) if allocation else 0
                    st.metric("Largest Position", f"{max_allocation*100:.1f}%")
                
                # Blockchain Integration
                if save_to_blockchain:
                    st.subheader("🔗 Blockchain Integration")
                    
                    # Show blockchain status
                    network_info = portfolio_manager.get_network_info()
                    if network_info:
                        st.info(f"🌐 Connected to Ethereum Network (Chain ID: {network_info['chain_id']})")
                    else:
                        st.warning("⚠️ Not connected to Ethereum network. Using demo mode.")
                    
                    # Store portfolio on blockchain
                    with st.spinner("Storing portfolio on Ethereum blockchain..."):
                        success = portfolio_manager.store_portfolio_on_blockchain(
                            portfolio_data=allocation,
                            risk_profile=risk_profile,
                            sectors=selected_sectors
                        )
                        
                        if success:
                            st.success("✅ Portfolio stored on Ethereum blockchain!")
                            
                            # Show portfolio summary from blockchain
                            st.subheader("📊 Blockchain Portfolio Summary")
                            
                            # Get contract info
                            contract_info = portfolio_manager.get_contract_info()
                            if contract_info:
                                col_bc1, col_bc2, col_bc3 = st.columns(3)
                                with col_bc1:
                                    st.metric("Contract Address", contract_info['address'][:10] + "...")
                                with col_bc2:
                                    st.metric("Functions Available", contract_info['abi_functions'])
                                with col_bc3:
                                    st.metric("Events Available", contract_info['abi_events'])
                            
                            # Show transaction details
                            st.info("🔗 Portfolio data is now immutable on the Ethereum blockchain")
                        else:
                            st.error("❌ Failed to store portfolio on blockchain")
                
                else:
                    st.error("❌ Failed to generate portfolio. Please try again.")
    
    with tab2:
        st.subheader("💰 Price Queries")
        
        # Simple Price Query by IDs
        st.write("**Query prices by Coin IDs**")
        coin_ids_input = st.text_input("Coin IDs (comma-separated)", 
                                     value="bitcoin,ethereum,cardano",
                                     help="Enter coin IDs separated by commas (e.g., bitcoin,ethereum)")
        
        # Supported currencies
        supported_currencies = api_client.get_supported_vs_currencies()
        if supported_currencies:
            vs_currency = st.selectbox("Currency", supported_currencies[:10], 
                                     index=0, help="Select the currency to compare against")
        else:
            vs_currency = "usd"
        
        # Additional data options
        col_options = st.columns(2)
        with col_options[0]:
            include_market_cap = st.checkbox("Include Market Cap", value=False)
            include_24hr_vol = st.checkbox("Include 24h Volume", value=False)
        with col_options[1]:
            include_24hr_change = st.checkbox("Include 24h Change", value=False)
            include_last_updated = st.checkbox("Include Last Updated", value=False)
        
        if st.button("🔍 Query Prices by IDs", key="query_ids"):
            if coin_ids_input.strip():
                coin_ids = [id.strip() for id in coin_ids_input.split(",")]
                price_data = api_client.get_simple_price(
                    ids=coin_ids,
                    vs_currencies=vs_currency,
                    include_market_cap=include_market_cap,
                    include_24hr_vol=include_24hr_vol,
                    include_24hr_change=include_24hr_change,
                    include_last_updated_at=include_last_updated
                )
                
                if price_data:
                    st.success("✅ Price data retrieved successfully!")
                    st.json(price_data)
                else:
                    st.error("❌ Failed to retrieve price data")
        
        st.divider()
        
        # Token Price Query by Contract Addresses
        st.write("**Query prices by Token Contract Addresses**")
        platform_id = st.text_input("Platform ID", value="ethereum",
                                   help="Enter the platform ID (e.g., ethereum, binance-smart-chain)")
        contract_addresses_input = st.text_input("Contract Addresses (comma-separated)", 
                                               value="0xa0b86a33e6441b8c4b8c4b8c4b8c4b8c4b8c4b8c",
                                               help="Enter contract addresses separated by commas")
        
        if st.button("🔍 Query Token Prices", key="query_tokens"):
            if platform_id.strip() and contract_addresses_input.strip():
                contract_addresses = [addr.strip() for addr in contract_addresses_input.split(",")]
                token_price_data = api_client.get_token_price(
                    platform_id=platform_id,
                    contract_addresses=contract_addresses,
                    vs_currencies=vs_currency,
                    include_market_cap=include_market_cap,
                    include_24hr_vol=include_24hr_vol,
                    include_24hr_change=include_24hr_change,
                    include_last_updated_at=include_last_updated
                )
                
                if token_price_data:
                    st.success("✅ Token price data retrieved successfully!")
                    st.json(token_price_data)
                else:
                    st.error("❌ Failed to retrieve token price data")
    
    with tab3:
        st.subheader("🪙 Coins API")
        
        # Coins List
        st.write("**Get All Supported Coins**")
        include_platform = st.checkbox("Include Platform Data", value=False, 
                                     help="Include platform contract addresses")
        
        if st.button("📋 Get Coins List", key="coins_list"):
            coins_list = api_client.get_coins_list(include_platform=include_platform)
            if coins_list:
                st.success(f"✅ Retrieved {len(coins_list)} coins")
                # Show first 10 coins as example
                df_coins = pd.DataFrame(coins_list[:10])
                st.dataframe(df_coins, use_container_width=True)
                st.info(f"Showing first 10 of {len(coins_list)} total coins")
            else:
                st.error("❌ Failed to retrieve coins list")
        
        st.divider()
        
        # Coins Markets
        st.write("**Get Coins with Market Data**")
        col_market1, col_market2 = st.columns(2)
        
        with col_market1:
            market_vs_currency = st.selectbox("Currency", ["usd", "eur", "btc"], key="market_currency")
            market_order = st.selectbox("Order By", ["market_cap_desc", "market_cap_asc", "volume_desc", "id_asc"], key="market_order")
            market_per_page = st.slider("Results per page", 10, 250, 50, key="market_per_page")
        
        with col_market2:
            market_page = st.number_input("Page", min_value=1, value=1, key="market_page")
            market_sparkline = st.checkbox("Include Sparkline", value=False, key="market_sparkline")
            market_change_period = st.selectbox("Price Change Period", ["24h", "7d", "30d"], key="market_change")
        
        if st.button("📊 Get Market Data", key="market_data"):
            market_data = api_client.get_coins_markets(
                vs_currency=market_vs_currency,
                order=market_order,
                per_page=market_per_page,
                page=market_page,
                sparkline=market_sparkline,
                price_change_percentage=market_change_period
            )
            if market_data:
                st.success(f"✅ Retrieved {len(market_data)} coins with market data")
                df_market = pd.DataFrame(market_data)
                # Select key columns for display
                display_cols = ['name', 'symbol', 'current_price', 'market_cap', 'total_volume', 'price_change_percentage_24h']
                available_cols = [col for col in display_cols if col in df_market.columns]
                st.dataframe(df_market[available_cols], use_container_width=True)
            else:
                st.error("❌ Failed to retrieve market data")
        
        st.divider()
        
        # Coin Data by ID
        st.write("**Get Detailed Coin Data**")
        coin_id_input = st.text_input("Coin ID", value="bitcoin", 
                                     help="Enter coin ID (e.g., bitcoin, ethereum)")
        
        col_coin1, col_coin2 = st.columns(2)
        with col_coin1:
            include_tickers = st.checkbox("Include Tickers", value=True, key="coin_tickers_checkbox")
            include_market_data = st.checkbox("Include Market Data", value=True, key="coin_market")
            include_community = st.checkbox("Include Community Data", value=True, key="coin_community")
        
        with col_coin2:
            include_developer = st.checkbox("Include Developer Data", value=True, key="coin_developer")
            include_sparkline = st.checkbox("Include Sparkline", value=False, key="coin_sparkline")
            include_localization = st.checkbox("Include Localization", value=True, key="coin_localization")
        
        if st.button("🔍 Get Coin Data", key="coin_data"):
            coin_data = api_client.get_coin_data(
                coin_id=coin_id_input,
                tickers=include_tickers,
                market_data=include_market_data,
                community_data=include_community,
                developer_data=include_developer,
                sparkline=include_sparkline,
                localization=include_localization
            )
            if coin_data:
                st.success("✅ Coin data retrieved successfully!")
                st.json(coin_data)
            else:
                st.error("❌ Failed to retrieve coin data")
        
        st.divider()
        
        # Coin Tickers
        st.write("**Get Coin Tickers**")
        ticker_coin_id = st.text_input("Coin ID for Tickers", value="bitcoin", key="ticker_coin")
        
        col_ticker1, col_ticker2 = st.columns(2)
        with col_ticker1:
            include_exchange_logo = st.checkbox("Include Exchange Logo", value=False, key="ticker_logo")
            ticker_depth = st.checkbox("Include Depth", value=False, key="ticker_depth")
        
        with col_ticker2:
            ticker_order = st.selectbox("Order By", ["trust_score_desc", "volume_desc"], key="ticker_order")
            ticker_page = st.number_input("Page", min_value=1, value=1, key="ticker_page")
        
        if st.button("📈 Get Coin Tickers", key="coin_tickers"):
            ticker_data = api_client.get_coin_tickers(
                coin_id=ticker_coin_id,
                include_exchange_logo=include_exchange_logo,
                page=ticker_page,
                order=ticker_order,
                depth=ticker_depth
            )
            if ticker_data:
                st.success("✅ Coin tickers retrieved successfully!")
                st.json(ticker_data)
            else:
                st.error("❌ Failed to retrieve coin tickers")
        
        st.divider()
        
        # Historical Data
        st.write("**Get Historical Data**")
        history_coin_id = st.text_input("Coin ID for History", value="bitcoin", key="history_coin")
        history_date = st.date_input("Date", value=pd.to_datetime("2024-01-01"), key="history_date")
        include_history_localization = st.checkbox("Include Localization", value=True, key="history_localization")
        
        if st.button("📅 Get Historical Data", key="coin_history"):
            history_data = api_client.get_coin_history(
                coin_id=history_coin_id,
                date=history_date.strftime("%d-%m-%Y"),
                localization=include_history_localization
            )
            if history_data:
                st.success("✅ Historical data retrieved successfully!")
                st.json(history_data)
            else:
                st.error("❌ Failed to retrieve historical data")
        
        st.divider()
        
        # Market Chart Data
        st.write("**Get Market Chart Data**")
        chart_coin_id = st.text_input("Coin ID for Chart", value="bitcoin", key="chart_coin")
        chart_vs_currency = st.selectbox("Currency", ["usd", "eur", "btc"], key="chart_currency")
        chart_days = st.selectbox("Days", [1, 7, 14, 30, 90, 180, 365], key="chart_days")
        
        if st.button("📊 Get Market Chart", key="market_chart"):
            chart_data = api_client.get_coin_market_chart(
                coin_id=chart_coin_id,
                vs_currency=chart_vs_currency,
                days=chart_days
            )
            if chart_data:
                st.success("✅ Market chart data retrieved successfully!")
                st.json(chart_data)
            else:
                st.error("❌ Failed to retrieve market chart data")
        
        st.divider()
        
        # OHLC Data
        st.write("**Get OHLC Chart Data**")
        ohlc_coin_id = st.text_input("Coin ID for OHLC", value="bitcoin", key="ohlc_coin")
        ohlc_vs_currency = st.selectbox("Currency", ["usd", "eur", "btc"], key="ohlc_currency")
        ohlc_days = st.selectbox("Days", [1, 7, 14, 30, 90, 180, 365], key="ohlc_days")
        
        if st.button("📈 Get OHLC Data", key="ohlc_data"):
            ohlc_data = api_client.get_coin_ohlc(
                coin_id=ohlc_coin_id,
                vs_currency=ohlc_vs_currency,
                days=ohlc_days
            )
            if ohlc_data:
                st.success("✅ OHLC data retrieved successfully!")
                st.json(ohlc_data)
            else:
                st.error("❌ Failed to retrieve OHLC data")
    
    with tab4:
        st.subheader("🔗 Contract API")
        
        # Coin Data by Contract Address
        st.write("**Get Coin Data by Token Contract Address**")
        contract_platform_id = st.text_input("Platform ID", value="ethereum", key="contract_platform")
        contract_address_input = st.text_input("Contract Address", 
                                            value="0xdac17f958d2ee523a2206206994597c13d831ec7",
                                            help="Enter token contract address (e.g., USDT on Ethereum)")
        
        if st.button("🔍 Get Coin Data by Contract", key="contract_data"):
            if contract_platform_id.strip() and contract_address_input.strip():
                contract_data = api_client.get_coin_data_by_contract(
                    platform_id=contract_platform_id,
                    contract_address=contract_address_input
                )
                
                if contract_data:
                    st.success("✅ Coin data by contract retrieved successfully!")
                    st.json(contract_data)
                else:
                    st.error("❌ Failed to retrieve coin data by contract")
        
        st.divider()
        
        # Contract Market Chart
        st.write("**Get Historical Chart Data by Contract Address**")
        chart_contract_platform = st.text_input("Platform ID", value="ethereum", key="chart_contract_platform")
        chart_contract_address = st.text_input("Contract Address", 
                                             value="0xdac17f958d2ee523a2206206994597c13d831ec7", 
                                             key="chart_contract_address")
        chart_contract_vs_currency = st.selectbox("Currency", ["usd", "eur", "btc"], key="chart_contract_currency")
        chart_contract_days = st.selectbox("Days", [1, 7, 14, 30, 90, 180, 365], key="chart_contract_days")
        
        if st.button("📊 Get Contract Market Chart", key="contract_chart"):
            if chart_contract_platform.strip() and chart_contract_address.strip():
                contract_chart_data = api_client.get_contract_market_chart(
                    platform_id=chart_contract_platform,
                    contract_address=chart_contract_address,
                    vs_currency=chart_contract_vs_currency,
                    days=chart_contract_days
                )
                
                if contract_chart_data:
                    st.success("✅ Contract market chart data retrieved successfully!")
                    st.json(contract_chart_data)
                else:
                    st.error("❌ Failed to retrieve contract market chart data")
        
        st.divider()
        
        # Contract Market Chart Range
        st.write("**Get Historical Chart Data within Time Range by Contract Address**")
        range_contract_platform = st.text_input("Platform ID", value="ethereum", key="range_contract_platform")
        range_contract_address = st.text_input("Contract Address", 
                                             value="0xdac17f958d2ee523a2206206994597c13d831ec7", 
                                             key="range_contract_address")
        range_contract_vs_currency = st.selectbox("Currency", ["usd", "eur", "btc"], key="range_contract_currency")
        
        col_range1, col_range2 = st.columns(2)
        with col_range1:
            from_timestamp = st.number_input("From Timestamp (UNIX)", 
                                           value=int((pd.Timestamp.now() - pd.Timedelta(days=7)).timestamp()),
                                           key="from_timestamp")
        with col_range2:
            to_timestamp = st.number_input("To Timestamp (UNIX)", 
                                         value=int(pd.Timestamp.now().timestamp()),
                                         key="to_timestamp")
        
        if st.button("📈 Get Contract Market Chart Range", key="contract_range"):
            if range_contract_platform.strip() and range_contract_address.strip():
                contract_range_data = api_client.get_contract_market_chart_range(
                    platform_id=range_contract_platform,
                    contract_address=range_contract_address,
                    vs_currency=range_contract_vs_currency,
                    from_timestamp=from_timestamp,
                    to_timestamp=to_timestamp
                )
                
                if contract_range_data:
                    st.success("✅ Contract market chart range data retrieved successfully!")
                    st.json(contract_range_data)
                else:
                    st.error("❌ Failed to retrieve contract market chart range data")
    
    with tab5:
        st.subheader("🔗 Blockchain Operations")
        
        # Contract Status
        st.write("**Smart Contract Status**")
        contract_info = portfolio_manager.get_contract_info()
        if contract_info:
            col_contract1, col_contract2 = st.columns(2)
            with col_contract1:
                st.metric("Contract Address", contract_info['address'][:10] + "...")
                st.metric("ABI Functions", contract_info['abi_functions'])
            with col_contract2:
                st.metric("ABI Events", contract_info['abi_events'])
                st.metric("Network", contract_info.get('network', 'Unknown'))
            
            st.success("✅ Smart contract loaded successfully")
        else:
            st.error("❌ Smart contract not available")
        
        st.divider()
        
        # Network Information
        st.write("**Network Connection**")
        network_info = portfolio_manager.get_network_info()
        if network_info:
            col_net1, col_net2 = st.columns(2)
            with col_net1:
                st.metric("Chain ID", network_info['chain_id'])
                st.metric("Block Number", network_info['block_number'])
            with col_net2:
                st.metric("Gas Price", f"{network_info['gas_price']} Gwei")
                st.metric("Connected", "✅ Yes")
        else:
            st.warning("⚠️ Not connected to Ethereum network")
        
        st.divider()
        
        # Portfolio Storage Test
        st.write("**Portfolio Storage Test**")
        
        # Test portfolio data
        test_portfolio = {
            "bitcoin": 0.4,
            "ethereum": 0.3,
            "cardano": 0.2,
            "polkadot": 0.1
        }
        
        col_test1, col_test2 = st.columns(2)
        with col_test1:
            if st.button("🧪 Test Portfolio Storage", key="test_storage"):
                with st.spinner("Testing portfolio storage..."):
                    success = portfolio_manager.store_portfolio_on_blockchain(
                        portfolio_data=test_portfolio,
                        risk_profile="medium",
                        sectors=["DeFi", "Layer 1"]
                    )
                    if success:
                        st.success("✅ Test portfolio stored successfully!")
                    else:
                        st.error("❌ Test portfolio storage failed")
        
        with col_test2:
            if st.button("📊 Retrieve Test Portfolio", key="retrieve_test"):
                with st.spinner("Retrieving test portfolio..."):
                    portfolio = portfolio_manager.retrieve_portfolio_from_blockchain()
                    if portfolio:
                        st.success("✅ Test portfolio retrieved successfully!")
                        st.json(portfolio)
                    else:
                        st.error("❌ Failed to retrieve test portfolio")
        
        st.divider()
        
        # Contract Functions
        st.write("**Available Contract Functions**")
        if contract_info and 'abi' in contract_info:
            functions = [item for item in contract_info['abi'] if item.get('type') == 'function']
            if functions:
                st.write("Available functions:")
                for func in functions[:5]:  # Show first 5 functions
                    st.code(f"{func['name']}({', '.join([input['name'] for input in func.get('inputs', [])])})")
            else:
                st.info("No functions found in contract ABI")

with col2:
    st.subheader("ℹ️ Portfolio Insights")
    
    # Risk Profile Explanation
    risk_explanations = {
        "low": "Conservative approach with stablecoins and blue-chip cryptocurrencies. Lower volatility, steady returns.",
        "medium": "Balanced allocation across different sectors. Moderate risk with growth potential.",
        "high": "Aggressive strategy focusing on high-growth assets. Higher volatility, higher potential returns."
    }
    
    st.info(f"**{risk_profile.title()} Risk Profile:**\n{risk_explanations[risk_profile]}")
    
    # Sector Information
    st.subheader("🏢 Selected Sectors")
    for sector in selected_sectors:
        if sector in optimizer.sector_categories:
            asset_count = len(optimizer.sector_categories[sector])
            st.write(f"• **{sector}**: {asset_count} available assets")
    
    # Market Status
    st.subheader("📈 Market Status")
    try:
        market_data = api_client.get_coins_markets(per_page=5)
        if market_data:
            btc_price = next((coin['current_price'] for coin in market_data if coin['id'] == 'bitcoin'), 0)
            eth_price = next((coin['current_price'] for coin in market_data if coin['id'] == 'ethereum'), 0)
            
            st.metric("Bitcoin", f"${btc_price:,.2f}")
            st.metric("Ethereum", f"${eth_price:,.2f}")
    except:
        st.write("Market data temporarily unavailable")
    
    # Global Market Data
    st.subheader("🌍 Global Market Data")
    try:
        global_data = api_client.get_global_market_data()
        if global_data and 'data' in global_data:
            data = global_data['data']
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_market_cap = data.get('total_market_cap', {}).get('usd', 0)
                st.metric("Total Market Cap", f"${total_market_cap:,.0f}")
            
            with col2:
                total_volume = data.get('total_volume', {}).get('usd', 0)
                st.metric("24h Volume", f"${total_volume:,.0f}")
            
            with col3:
                market_cap_percentage = data.get('market_cap_percentage', {}).get('btc', 0)
                st.metric("BTC Dominance", f"{market_cap_percentage:.1f}%")
    except:
        st.write("Global market data unavailable")
    
    # DeFi Market Data
    st.subheader("🏦 DeFi Market Data")
    try:
        defi_data = api_client.get_defi_market_data()
        if defi_data and 'data' in defi_data:
            data = defi_data['data']
            col1, col2 = st.columns(2)
            
            with col1:
                defi_market_cap = data.get('defi_market_cap', 0)
                if isinstance(defi_market_cap, (int, float)):
                    st.metric("DeFi Market Cap", f"${defi_market_cap:,.0f}")
                else:
                    st.metric("DeFi Market Cap", "Data unavailable")
            
            with col2:
                defi_volume = data.get('defi_24h_volume', 0)
                if isinstance(defi_volume, (int, float)):
                    st.metric("DeFi 24h Volume", f"${defi_volume:,.0f}")
                else:
                    st.metric("DeFi 24h Volume", "Data unavailable")
    except Exception as e:
        st.write("DeFi market data temporarily unavailable")
    
    # Public Companies Holdings
    st.subheader("🏦 Public Companies Holdings")
    try:
        coin_id_input = st.text_input("Coin ID (e.g., bitcoin, ethereum)", value="bitcoin", key="public_companies_coin")
        if st.button("🔍 Get Public Companies Holdings", key="public_companies_holdings"):
            companies_data = api_client.get_public_companies_holdings(coin_id_input)
            if companies_data:
                st.success("✅ Public companies holdings data retrieved successfully!")
                st.json(companies_data)
            else:
                st.error("❌ Failed to retrieve public companies holdings data")
    except Exception as e:
        st.write("Public companies holdings data temporarily unavailable")
    
    # Trending Coins
    st.subheader("🔥 Trending Coins")
    try:
        trending = api_client.get_trending_coins()
        if trending:
            for coin in trending[:3]:
                st.write(f"• **{coin['item']['name']}**: {coin['item']['symbol'].upper()}")
    except:
        st.write("Trending data unavailable")

# Footer
st.markdown("---")
st.markdown(
    "🔗 **Powered by:** CoinGecko MCP Server | Streamlit | Plotly | Ethereum Blockchain"
) 