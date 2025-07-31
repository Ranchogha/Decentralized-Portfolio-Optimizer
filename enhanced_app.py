#!/usr/bin/env python3
"""
Enhanced Decentralized Portfolio Optimizer
Incorporating CoinGecko Python SDK features for better performance and cooler interface
"""

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
import asyncio
from typing import Dict, List, Optional, Any

# Load environment variables
load_dotenv()

# Enhanced CoinGecko API Integration with SDK-inspired features
class EnhancedCoinGeckoAPI:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.api_key = os.getenv("COINGECKO_API_KEY")
        self.session = requests.Session()
        
        # Enhanced headers for better API performance
        self.session.headers.update({
            'User-Agent': 'Decentralized-Portfolio-Optimizer/2.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Add API key to headers if available
        if self.api_key:
            self.session.headers.update({
                'x-cg-demo-api-key': self.api_key
            })
            st.success("✅ CoinGecko API key configured")
        else:
            st.info("ℹ️ Using public CoinGecko API endpoints")
    
    def _handle_api_response(self, response, endpoint_name):
        """Enhanced API response handling with better error messages"""
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            st.error(f"🚫 Rate limit exceeded for {endpoint_name}. Please wait before making more requests.")
            return None
        elif response.status_code == 403:
            st.error(f"🔒 Access forbidden for {endpoint_name}. Check your API key.")
            return None
        elif response.status_code == 401:
            st.error(f"🔑 Unauthorized for {endpoint_name}. Check your API key.")
            return None
        else:
            st.error(f"❌ Error {response.status_code} for {endpoint_name}: {response.text}")
            return None
    
    def ping_server(self):
        """Check API server status with enhanced response"""
        try:
            response = self.session.get(f"{self.base_url}/ping")
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'online',
                    'message': data.get('gecko_says', 'API server is online'),
                    'response_time': response.elapsed.total_seconds(),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'error',
                    'message': f'API server returned status code: {response.status_code}',
                    'response_time': response.elapsed.total_seconds(),
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            return {
                'status': 'offline',
                'message': f'Cannot connect to API server: {str(e)}',
                'response_time': None,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_simple_price(self, ids, vs_currencies='usd', include_market_cap=False, 
                        include_24hr_vol=False, include_24hr_change=False, 
                        include_last_updated_at=False):
        """Enhanced simple price API with better error handling"""
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
            st.error(f"❌ Error fetching simple price data: {str(e)}")
            return {}
    
    def get_coins_markets(self, vs_currency="usd", ids=None, category=None, order="market_cap_desc", 
                          per_page=100, page=1, sparkline=False, price_change_percentage="24h", 
                          include_tokens=None):
        """Enhanced market data API with better filtering"""
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
                st.warning("⏱️ Rate limit approaching. Please wait before making more requests.")
                return []
            
            response = self.session.get(f"{self.base_url}/coins/markets", params=params)
            result = self._handle_api_response(response, "coins/markets")
            
            # Cache the result
            if result:
                api_cache.set("coins/markets", result, params)
            
            return result if result else []
        except Exception as e:
            st.error(f"❌ Error fetching coins markets: {str(e)}")
            return []
    
    def get_trending_coins(self):
        """Enhanced trending coins API"""
        try:
            response = self.session.get(f"{self.base_url}/search/trending")
            result = self._handle_api_response(response, "search/trending")
            if result:
                return result
            return {}
        except Exception as e:
            st.error(f"❌ Error fetching trending coins: {str(e)}")
            return {}
    
    def get_global_market_data(self):
        """Enhanced global market data API"""
        try:
            # Check cache first
            cached_result = api_cache.get("global")
            if cached_result:
                return cached_result
            
            # Check rate limit
            if not rate_limiter.can_make_call():
                st.warning("⏱️ Rate limit approaching. Please wait before making more requests.")
                return {}
            
            response = self.session.get(f"{self.base_url}/global")
            result = self._handle_api_response(response, "global")
            
            # Cache the result
            if result:
                api_cache.set("global", result)
            
            return result if result else {}
        except Exception as e:
            st.error(f"❌ Error fetching global market data: {str(e)}")
            return {}
    
    def get_defi_market_data(self):
        """Enhanced DeFi market data API"""
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
            st.error(f"❌ Error fetching DeFi market data: {str(e)}")
            return {}
    
    def get_coin_market_chart(self, coin_id, vs_currency="usd", days=30):
        """Enhanced market chart API with better error handling"""
        try:
            params = {
                'vs_currency': vs_currency,
                'days': days
            }
            
            response = self.session.get(f"{self.base_url}/coins/{coin_id}/market_chart", params=params)
            result = self._handle_api_response(response, f"coins/{coin_id}/market_chart")
            return result if result else {}
        except Exception as e:
            st.error(f"❌ Error fetching coin market chart: {str(e)}")
            return {}

# Initialize enhanced API client
api_client = EnhancedCoinGeckoAPI()

# Enhanced caching system
class EnhancedAPICache:
    """Enhanced cache for API responses with better performance"""
    def __init__(self, cache_ttl=300):  # 5 minutes default TTL
        self.cache = {}
        self.cache_ttl = cache_ttl
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
    
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
                self.stats['hits'] += 1
                return cached_data['data']
            else:
                # Remove expired cache entry
                del self.cache[cache_key]
                self.stats['evictions'] += 1
        
        self.stats['misses'] += 1
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
        self.stats = {'hits': 0, 'misses': 0, 'evictions': 0}
    
    def get_cache_stats(self):
        """Get enhanced cache statistics"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total_entries': len(self.cache),
            'cache_ttl': self.cache_ttl,
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'evictions': self.stats['evictions'],
            'hit_rate': f"{hit_rate:.1f}%",
            'memory_usage': len(json.dumps(self.cache))
        }

# Enhanced rate limiter
class EnhancedRateLimiter:
    def __init__(self, max_calls=25, time_window=60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.stats = {
            'total_calls': 0,
            'rate_limited_calls': 0
        }
    
    def can_make_call(self):
        now = time.time()
        # Remove old calls outside the time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            self.stats['total_calls'] += 1
            return True
        
        self.stats['rate_limited_calls'] += 1
        return False
    
    def get_stats(self):
        """Get rate limiter statistics"""
        return {
            'max_calls': self.max_calls,
            'time_window': self.time_window,
            'current_calls': len(self.calls),
            'remaining_calls': max(0, self.max_calls - len(self.calls)),
            'total_calls': self.stats['total_calls'],
            'rate_limited_calls': self.stats['rate_limited_calls']
        }

# Initialize enhanced rate limiter and cache
rate_limiter = EnhancedRateLimiter()
api_cache = EnhancedAPICache(cache_ttl=300)  # 5 minutes cache TTL

# Initialize wallet manager
wallet_manager = MultiWalletManager()

# Enhanced Portfolio Optimization Logic
class EnhancedPortfolioOptimizer:
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
        """Enhanced AI-powered portfolio optimization with better sector filtering"""
        try:
            # Check rate limit before making API calls
            if not rate_limiter.can_make_call():
                st.warning("⏱️ Rate limit approaching. Please wait before making more requests.")
                return {}, []
            
            # Fetch market data
            market_data = api_client.get_coins_markets(per_page=200)
            
            if not market_data:
                st.error("❌ Failed to fetch market data")
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
                st.warning("⚠️ No assets found for selected sectors. Using top market cap coins.")
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
                    st.warning(f"⚠️ Could not fetch data for {asset['name']}: {str(e)}")
                    continue
            
            # Apply risk-based filtering
            risk_config = self.risk_profiles[risk_profile]
            filtered_assets = [
                asset for asset in assets_with_volatility
                if asset['volatility'] <= risk_config['volatility_threshold']
            ]
            
            if not filtered_assets:
                st.warning("⚠️ No assets meet volatility criteria. Using all available assets.")
                filtered_assets = assets_with_volatility
            
            # Sort by market cap and limit assets
            filtered_assets.sort(key=lambda x: x['market_cap'], reverse=True)
            selected_assets = filtered_assets[:max_assets]
            
            # Generate allocation based on risk profile
            allocation = self._generate_allocation(selected_assets, risk_profile, investment_amount)
            
            return allocation, selected_assets
            
        except Exception as e:
            st.error(f"❌ Error optimizing portfolio: {str(e)}")
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

# Initialize enhanced optimizer
optimizer = EnhancedPortfolioOptimizer()

# Initialize Web3 with build artifacts support
portfolio_manager = EthereumPortfolioManager()

# Enhanced Streamlit Web Application
st.set_page_config(
    page_title="🚀 Enhanced Decentralized Portfolio Optimizer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for cooler styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        color: white;
        margin: 0.5rem 0;
    }
    .sector-toggle {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    .sector-toggle:hover {
        border-color: #667eea;
        transform: translateY(-2px);
    }
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-online { background-color: #00ff00; }
    .status-offline { background-color: #ff0000; }
    .status-warning { background-color: #ffaa00; }
</style>
""", unsafe_allow_html=True)

# Enhanced main header
st.markdown("""
<div class="main-header">
    <h1>🚀 Enhanced Decentralized Portfolio Optimizer</h1>
    <p>Powered by CoinGecko Python SDK & Ethereum Blockchain</p>
    <p>AI-powered portfolio management with real-time market data</p>
</div>
""", unsafe_allow_html=True)

# Enhanced sidebar for user inputs
with st.sidebar:
    st.header("🎯 Portfolio Configuration")
    
    # Risk Profile Selection with enhanced styling
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
    
    # Enhanced Sector Selection with cool toggles
    st.subheader("🏢 Sector Selection")
    st.markdown("Select sectors to include in your portfolio:")
    
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
        st.warning("⚠️ Please select at least one sector")
        selected_sectors = ["DeFi", "Layer 1"]
    
    # Portfolio Size
    max_assets = st.slider(
        "Maximum Assets",
        min_value=3,
        max_value=15,
        value=8,
        help="Maximum number of assets in the portfolio"
    )
    
    # Enhanced Blockchain Integration
    st.subheader("🔗 Blockchain Features")
    
    # Show enhanced blockchain connection status
    network_info = portfolio_manager.get_network_info()
    if network_info:
        st.success(f"✅ Connected to Ethereum (Chain ID: {network_info['chain_id']})")
    else:
        st.warning("⚠️ Not connected to Ethereum network")
    
    save_to_blockchain = st.checkbox(
        "Save to Ethereum Blockchain",
        value=False,
        help="Store portfolio allocation on Ethereum blockchain"
    )
    
    # Enhanced Wallet Connection Section
    st.subheader("💼 Wallet Connection")
    wallet_manager.render_wallet_connection_ui()
    
    # Enhanced Market Data Refresh
    if st.button("🔄 Refresh Market Data", type="primary"):
        st.rerun()

# Enhanced API Status Check
if os.getenv("DEBUG", "false").lower() == "true":
    with st.sidebar:
        st.subheader("🔧 Enhanced API Status")
        
        # Enhanced ping endpoint to check API server status
        ping_result = api_client.ping_server()
        
        if ping_result['status'] == 'online':
            st.success(f"✅ {ping_result['message']}")
            if ping_result['response_time']:
                st.info(f"⏱️ Response time: {ping_result['response_time']:.3f}s")
        elif ping_result['status'] == 'error':
            st.error(f"❌ {ping_result['message']}")
        else:
            st.error(f"❌ {ping_result['message']}")
        
        # Enhanced rate limit status
        rate_stats = rate_limiter.get_stats()
        st.info(f"📊 API Calls: {rate_stats['remaining_calls']}/{rate_stats['max_calls']} remaining")
        
        # Enhanced cache statistics
        cache_stats = api_cache.get_cache_stats()
        st.info(f"💾 Cache: {cache_stats['hit_rate']} hit rate, {cache_stats['total_entries']} entries")

# Main content area with enhanced layout
col1, col2 = st.columns([2, 1])

with col1:
    # Enhanced tabs for different functionalities
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Portfolio Optimization", "🔍 SEARCH", "🪙 Coins API", "🔗 Contract API", "🔗 Blockchain Operations"])
    
    with tab1:
        st.subheader("🎯 Enhanced Portfolio Generation")
        
        if st.button("🚀 Generate Optimized Portfolio", type="primary", use_container_width=True):
            with st.spinner("🤖 AI is analyzing market data and optimizing your portfolio..."):
                allocation, selected_assets = optimizer.optimize_portfolio(
                    risk_profile, investment_amount, selected_sectors, max_assets
                )
            
            if allocation and selected_assets:
                st.success("✅ Portfolio optimized successfully!")
                
                # Enhanced asset details dataframe
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
                
                # Enhanced portfolio summary with cool metrics
                st.subheader("📊 Enhanced Portfolio Summary")
                col_sum1, col_sum2, col_sum3 = st.columns(3)
                
                with col_sum1:
                    st.metric("Total Investment", f"${investment_amount:,.2f}")
                
                with col_sum2:
                    st.metric("Number of Assets", len(allocation))
                
                with col_sum3:
                    total_allocation = sum(allocation.values())
                    st.metric("Total Allocation", f"{total_allocation*100:.1f}%")
                
                # Enhanced portfolio table
                st.dataframe(df, use_container_width=True)
                
                # Enhanced Visualizations with cooler charts
                st.subheader("📈 Enhanced Portfolio Visualizations")
                
                # Enhanced Pie Chart
                fig_pie = px.pie(
                    df, 
                    values='Amount (USD)', 
                    names='Asset',
                    title=f"Portfolio Allocation - {risk_profile.title()} Risk Profile",
                    hover_data=['Allocation %'],
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie.update_layout(
                    title_font_size=20,
                    title_font_color="#667eea",
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_pie, use_container_width=True)
                
                # Enhanced Historical Performance Chart
                if selected_assets:
                    st.subheader("📈 Enhanced Historical Performance (30 Days)")
                    
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
                                            mode='lines',
                                            line=dict(width=3)
                                        )
                                    )
                    
                    fig_line.update_layout(
                        title="30-Day Price Performance (Normalized)",
                        xaxis_title="Date",
                        yaxis_title="Price Change (%)",
                        height=500,
                        hovermode='x unified',
                        title_font_size=20,
                        title_font_color="#667eea",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig_line, use_container_width=True)
                
                # Enhanced Risk Metrics
                st.subheader("⚖️ Enhanced Risk Analysis")
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
                
                # Enhanced Blockchain Integration
                if save_to_blockchain:
                    st.subheader("🔗 Enhanced Blockchain Integration")
                    
                    # Show enhanced blockchain status
                    network_info = portfolio_manager.get_network_info()
                    if network_info:
                        st.info(f"🌐 Connected to Ethereum Network (Chain ID: {network_info['chain_id']})")
                    else:
                        st.warning("⚠️ Not connected to Ethereum network. Using demo mode.")
                    
                    # Store portfolio on blockchain
                    with st.spinner("🔗 Storing portfolio on Ethereum blockchain..."):
                        success = portfolio_manager.store_portfolio_on_blockchain(
                            portfolio_data=allocation,
                            risk_profile=risk_profile,
                            sectors=selected_sectors
                        )
                        
                        if success:
                            st.success("✅ Portfolio stored on Ethereum blockchain!")
                            
                            # Show enhanced portfolio summary from blockchain
                            st.subheader("📊 Enhanced Blockchain Portfolio Summary")
                            
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
                            
                            # Show enhanced transaction details
                            st.info("🔗 Portfolio data is now immutable on the Ethereum blockchain")
                        else:
                            st.error("❌ Failed to store portfolio on blockchain")
                
                else:
                    st.error("❌ Failed to generate portfolio. Please try again.")

# Enhanced sidebar insights
with col2:
    st.subheader("ℹ️ Enhanced Portfolio Insights")
    
    # Enhanced Risk Profile Explanation
    risk_explanations = {
        "low": "Conservative approach with stablecoins and blue-chip cryptocurrencies. Lower volatility, steady returns.",
        "medium": "Balanced allocation across different sectors. Moderate risk with growth potential.",
        "high": "Aggressive strategy focusing on high-growth assets. Higher volatility, higher potential returns."
    }
    
    st.info(f"**{risk_profile.title()} Risk Profile:**\n{risk_explanations[risk_profile]}")
    
    # Enhanced Sector Information
    st.subheader("🏢 Selected Sectors")
    for sector in selected_sectors:
        if sector in optimizer.sector_categories:
            asset_count = len(optimizer.sector_categories[sector])
            st.write(f"• **{sector}**: {asset_count} available assets")
    
    # Enhanced Market Status
    st.subheader("📈 Enhanced Market Status")
    try:
        market_data = api_client.get_coins_markets(per_page=5)
        if market_data:
            btc_price = next((coin['current_price'] for coin in market_data if coin['id'] == 'bitcoin'), 0)
            eth_price = next((coin['current_price'] for coin in market_data if coin['id'] == 'ethereum'), 0)
            
            st.metric("Bitcoin", f"${btc_price:,.2f}")
            st.metric("Ethereum", f"${eth_price:,.2f}")
    except:
        st.write("Market data temporarily unavailable")
    
    # Enhanced Global Market Data
    st.subheader("🌍 Enhanced Global Market Data")
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
    
    # Enhanced DeFi Market Data
    st.subheader("🏦 Enhanced DeFi Market Data")
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
    
    # Enhanced Trending Coins
    st.subheader("🔥 Enhanced Trending Coins")
    try:
        trending = api_client.get_trending_coins()
        if trending:
            for coin in trending.get('coins', [])[:3]:
                st.write(f"• **{coin['item']['name']}**: {coin['item']['symbol'].upper()}")
    except:
        st.write("Trending data unavailable")

# Enhanced footer
st.markdown("---")
st.markdown(
    "🔗 **Powered by:** CoinGecko Python SDK | Streamlit | Plotly | Ethereum Blockchain | Enhanced UI/UX"
) 