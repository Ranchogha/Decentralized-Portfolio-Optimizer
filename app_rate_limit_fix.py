#!/usr/bin/env python3
"""
Simple Rate Limit Fix for app.py
Add this to your existing app.py to fix rate limiting issues
"""

import time
import streamlit as st
from typing import Optional, Dict, List
import requests

# Add this at the top of your app.py after imports
class SimpleRateLimiter:
    """Simple rate limiter for CoinGecko API"""
    
    def __init__(self):
        self.last_call = 0
        self.min_interval = 1.2  # 1.2 seconds between calls (50 calls per minute)
    
    def wait_if_needed(self):
        """Wait if needed to respect rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_call
        
        if time_since_last < self.min_interval:
            wait_time = self.min_interval - time_since_last
            time.sleep(wait_time)
        
        self.last_call = time.time()

# Initialize rate limiter
rate_limiter = SimpleRateLimiter()

# Add this function to your app.py
def get_market_data_with_rate_limit():
    """Get market data with rate limiting"""
    try:
        # Wait before making API call
        rate_limiter.wait_if_needed()
        
        # Your existing API call here
        # Replace this with your actual API call
        response = requests.get("https://api.coingecko.com/api/v3/coins/markets", 
                              params={'vs_currency': 'usd', 'per_page': 50, 'page': 1})
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            st.warning("⏱️ Rate limit exceeded. Please wait 60 seconds and try again.")
            return None
        else:
            st.error(f"❌ API Error: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"❌ Request failed: {str(e)}")
        return None

# Add this to your portfolio generation section
def generate_portfolio_with_fallback():
    """Generate portfolio with fallback data"""
    
    # Try to get real data first
    market_data = get_market_data_with_rate_limit()
    
    if not market_data:
        st.warning("⚠️ Using fallback data due to API limits")
        # Use fallback data
        market_data = [
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
        ]
    
    return market_data

# Add this to your main app logic
def main_with_rate_limit():
    """Main app logic with rate limiting"""
    
    # Check API key
    api_key = st.secrets.get("COINGECKO_API_KEY", "")
    if not api_key:
        st.warning("⚠️ No CoinGecko API key found. Using public endpoints (rate limited).")
        st.info("💡 Get a free API key at: https://www.coingecko.com/api")
    
    # Generate portfolio with rate limiting
    if st.button("🚀 Generate AI-Optimized Portfolio", type="primary"):
        with st.spinner("🔄 Generating portfolio..."):
            market_data = generate_portfolio_with_fallback()
            
            if market_data:
                st.success(f"✅ Found {len(market_data)} market assets")
                # Continue with your portfolio generation logic
            else:
                st.error("❌ Failed to get market data. Please try again later.")

# Usage instructions:
"""
1. Add the SimpleRateLimiter class to your app.py
2. Replace your API calls with get_market_data_with_rate_limit()
3. Use generate_portfolio_with_fallback() for portfolio generation
4. Add main_with_rate_limit() to your main app logic

This will:
- ✅ Respect rate limits (50 calls/minute for public API)
- ✅ Provide fallback data when API is unavailable
- ✅ Show helpful error messages
- ✅ Continue working even with rate limits
""" 