#!/usr/bin/env python3
"""
Rate Limiting and Caching Solution for CoinGecko API
Fixes the rate limit issues in the portfolio optimizer
"""

import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import streamlit as st
import requests

class EnhancedRateLimiter:
    """Enhanced rate limiter with intelligent backoff and caching"""
    
    def __init__(self):
        # CoinGecko rate limits
        self.public_rate_limit = 50  # calls per minute for public API
        self.pro_rate_limit = 1000   # calls per minute for pro API
        self.calls_made = 0
        self.last_reset = time.time()
        self.backoff_time = 0
        
        # Cache settings
        self.cache_duration = 300  # 5 minutes
        self.cache = {}
        
    def can_make_call(self) -> bool:
        """Check if we can make an API call"""
        current_time = time.time()
        
        # Reset counter if minute has passed
        if current_time - self.last_reset >= 60:
            self.calls_made = 0
            self.last_reset = current_time
            self.backoff_time = 0
        
        # Check if we're in backoff period
        if current_time < self.backoff_time:
            return False
        
        # Get current rate limit based on API key
        api_key = st.secrets.get("COINGECKO_API_KEY", "")
        current_limit = self.pro_rate_limit if api_key else self.public_rate_limit
        
        return self.calls_made < current_limit
    
    def record_call(self):
        """Record that an API call was made"""
        self.calls_made += 1
        
        # If we hit the limit, set backoff
        api_key = st.secrets.get("COINGECKO_API_KEY", "")
        current_limit = self.pro_rate_limit if api_key else self.public_rate_limit
        
        if self.calls_made >= current_limit:
            self.backoff_time = time.time() + 60  # Wait 1 minute
    
    def get_wait_time(self) -> float:
        """Get how long to wait before next call"""
        if self.can_make_call():
            return 0
        
        api_key = st.secrets.get("COINGECKO_API_KEY", "")
        current_limit = self.pro_rate_limit if api_key else self.public_rate_limit
        
        if self.calls_made >= current_limit:
            return max(0, self.backoff_time - time.time())
        
        return 0

class EnhancedCache:
    """Enhanced caching with TTL and intelligent invalidation"""
    
    def __init__(self, default_ttl=300):
        self.cache = {}
        self.default_ttl = default_ttl
    
    def _generate_key(self, endpoint: str, params: Dict = None) -> str:
        """Generate cache key"""
        key_data = f"{endpoint}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, endpoint: str, params: Dict = None) -> Optional[Any]:
        """Get cached data"""
        key = self._generate_key(endpoint, params)
        
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.default_ttl:
                return data
        
        return None
    
    def set(self, endpoint: str, data: Any, params: Dict = None):
        """Set cached data"""
        key = self._generate_key(endpoint, params)
        self.cache[key] = (data, time.time())
    
    def clear_expired(self):
        """Clear expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp >= self.default_ttl
        ]
        for key in expired_keys:
            del self.cache[key]

class CoinGeckoAPIWithRateLimit:
    """CoinGecko API wrapper with enhanced rate limiting and caching"""
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.rate_limiter = EnhancedRateLimiter()
        self.cache = EnhancedCache()
        self.session = requests.Session()
        
        # Set up headers
        api_key = st.secrets.get("COINGECKO_API_KEY", "")
        self.session.headers.update({
            'User-Agent': 'Decentralized-Portfolio-Optimizer/2.0',
            'Accept': 'application/json'
        })
        
        if api_key:
            self.session.headers.update({
                'x-cg-demo-api-key': api_key
            })
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with rate limiting and caching"""
        
        # Check cache first
        cached_data = self.cache.get(endpoint, params)
        if cached_data:
            return cached_data
        
        # Check rate limit
        if not self.rate_limiter.can_make_call():
            wait_time = self.rate_limiter.get_wait_time()
            st.warning(f"⏱️ Rate limit reached. Please wait {wait_time:.1f} seconds...")
            return None
        
        try:
            # Make the request
            response = self.session.get(f"{self.base_url}/{endpoint}", params=params)
            self.rate_limiter.record_call()
            
            if response.status_code == 200:
                data = response.json()
                # Cache successful responses
                self.cache.set(endpoint, data, params)
                return data
            elif response.status_code == 429:
                st.warning("⏱️ Rate limit exceeded. Please wait before making more requests.")
                return None
            else:
                st.error(f"❌ API Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            st.error(f"❌ Request failed: {str(e)}")
            return None
    
    def get_coins_markets(self, vs_currency="usd", per_page=50, page=1) -> Optional[List[Dict]]:
        """Get market data with rate limiting"""
        params = {
            'vs_currency': vs_currency,
            'per_page': per_page,
            'page': page,
            'order': 'market_cap_desc'
        }
        return self._make_request('coins/markets', params)
    
    def get_simple_price(self, ids: List[str], vs_currencies="usd") -> Optional[Dict]:
        """Get simple price data with rate limiting"""
        params = {
            'ids': ','.join(ids),
            'vs_currencies': vs_currencies
        }
        return self._make_request('simple/price', params)
    
    def get_global_market_data(self) -> Optional[Dict]:
        """Get global market data with rate limiting"""
        return self._make_request('global')

def create_fallback_data():
    """Create fallback data when API is unavailable"""
    return {
        'market_data': [
            {
                'id': 'bitcoin',
                'symbol': 'btc',
                'name': 'Bitcoin',
                'current_price': 45000,
                'market_cap': 850000000000,
                'price_change_percentage_24h': 2.5,
                'total_volume': 25000000000
            },
            {
                'id': 'ethereum',
                'symbol': 'eth',
                'name': 'Ethereum',
                'current_price': 2800,
                'market_cap': 350000000000,
                'price_change_percentage_24h': 1.8,
                'total_volume': 15000000000
            },
            {
                'id': 'binancecoin',
                'symbol': 'bnb',
                'name': 'BNB',
                'current_price': 320,
                'market_cap': 50000000000,
                'price_change_percentage_24h': 0.5,
                'total_volume': 2000000000
            }
        ],
        'global_data': {
            'total_market_cap': {'usd': 1200000000000},
            'total_volume': {'usd': 50000000000},
            'market_cap_percentage': {'btc': 45.2, 'eth': 28.1}
        }
    }

# Initialize the enhanced API
enhanced_api = CoinGeckoAPIWithRateLimit() 