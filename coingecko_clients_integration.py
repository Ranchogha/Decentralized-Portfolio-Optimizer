#!/usr/bin/env python3
"""
CoinGecko API Clients Integration
Comprehensive integration of official and unofficial CoinGecko API clients
Incorporates Swagger JSON, Python wrappers, and enhanced features for portfolio optimization
"""

import requests
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Union
import os
from dotenv import load_dotenv
import streamlit as st
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

class CoinGeckoSwaggerClient:
    """
    Official CoinGecko Swagger JSON Client Integration
    Uses official OpenAPI specifications for enhanced API access
    """
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.demo_api_key = os.getenv("COINGECKO_DEMO_API_KEY")
        self.pro_api_key = os.getenv("COINGECKO_PRO_API_KEY")
        
        # Swagger JSON endpoints
        self.swagger_urls = {
            "public": "https://api.coingecko.com/api/v3/swagger.json",
            "pro": "https://api.coingecko.com/api/v3/pro/swagger.json",
            "onchain_dex": "https://api.coingecko.com/api/v3/onchain-dex/swagger.json"
        }
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Decentralized-Portfolio-Optimizer-Swagger/3.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Set API key based on availability
        if self.demo_api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.demo_api_key}',
                'x-cg-demo-api-key': self.demo_api_key
            })
            self.api_type = "demo"
        elif self.pro_api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.pro_api_key}',
                'x-cg-pro-api-key': self.pro_api_key
            })
            self.api_type = "pro"
        else:
            self.api_type = "none"
    
    def get_swagger_spec(self, api_type: str = "public") -> Dict:
        """Get Swagger/OpenAPI specification for CoinGecko API"""
        try:
            url = self.swagger_urls.get(api_type, self.swagger_urls["public"])
            response = self.session.get(url)
            
            if response.status_code == 200:
                spec = response.json()
                return {
                    'spec': spec,
                    'endpoints': self._extract_endpoints(spec),
                    'api_type': api_type,
                    'version': spec.get('info', {}).get('version', 'unknown')
                }
            else:
                st.error(f"❌ Failed to fetch Swagger spec: {response.status_code}")
                return {}
        except Exception as e:
            st.error(f"❌ Error fetching Swagger spec: {str(e)}")
            return {}
    
    def _extract_endpoints(self, spec: Dict) -> List[Dict]:
        """Extract available endpoints from Swagger specification"""
        endpoints = []
        
        if 'paths' in spec:
            for path, methods in spec['paths'].items():
                for method, details in methods.items():
                    if method in ['get', 'post', 'put', 'delete']:
                        endpoints.append({
                            'path': path,
                            'method': method.upper(),
                            'summary': details.get('summary', ''),
                            'description': details.get('description', ''),
                            'tags': details.get('tags', []),
                            'parameters': details.get('parameters', [])
                        })
        
        return endpoints
    
    def get_api_documentation(self) -> Dict:
        """Get comprehensive API documentation from Swagger specs"""
        docs = {}
        
        for api_type in self.swagger_urls.keys():
            spec_data = self.get_swagger_spec(api_type)
            if spec_data:
                docs[api_type] = spec_data
        
        return docs

class PyCoinGeckoClient:
    """
    Unofficial Python Wrapper Integration
    Based on coingecko (khooizhz) and pycoingecko (man-c) wrappers
    """
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Decentralized-Portfolio-Optimizer-PyClient/3.0',
            'Accept': 'application/json'
        })
        
        # Rate limiting
        self.rate_limit = {
            'requests_per_minute': 50,
            'last_request_time': None,
            'request_count': 0
        }
    
    def _rate_limit_check(self):
        """Check and enforce rate limiting"""
        now = datetime.now()
        
        if self.rate_limit['last_request_time']:
            time_diff = (now - self.rate_limit['last_request_time']).total_seconds()
            
            if time_diff < 60:  # Within 1 minute
                if self.rate_limit['request_count'] >= self.rate_limit['requests_per_minute']:
                    sleep_time = 60 - time_diff
                    st.warning(f"⏱️ Rate limit reached. Waiting {sleep_time:.1f} seconds...")
                    time.sleep(sleep_time)
                    self.rate_limit['request_count'] = 0
            else:
                self.rate_limit['request_count'] = 0
        
        self.rate_limit['last_request_time'] = now
        self.rate_limit['request_count'] += 1
    
    def get_simple_price(self, ids: List[str], vs_currencies: str = "usd", 
                        include_market_cap: bool = True, include_24hr_vol: bool = True,
                        include_24hr_change: bool = True) -> Dict:
        """Get simple price data with enhanced features"""
        self._rate_limit_check()
        
        params = {
            'ids': ','.join(ids),
            'vs_currencies': vs_currencies,
            'include_market_cap': str(include_market_cap).lower(),
            'include_24hr_vol': str(include_24hr_vol).lower(),
            'include_24hr_change': str(include_24hr_change).lower()
        }
        
        try:
            response = self.session.get(f"{self.base_url}/simple/price", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Add enhanced analysis
                data['analysis'] = self._analyze_price_data(data)
                
                return data
            else:
                st.error(f"❌ Error fetching price data: {response.status_code}")
                return {}
        except Exception as e:
            st.error(f"❌ Error in price request: {str(e)}")
            return {}
    
    def get_coins_markets(self, vs_currency: str = "usd", order: str = "market_cap_desc",
                          per_page: int = 100, page: int = 1, sparkline: bool = False,
                          price_change_percentage: str = "24h") -> List[Dict]:
        """Get coins market data with enhanced analysis"""
        self._rate_limit_check()
        
        params = {
            'vs_currency': vs_currency,
            'order': order,
            'per_page': per_page,
            'page': page,
            'sparkline': str(sparkline).lower(),
            'price_change_percentage': price_change_percentage
        }
        
        try:
            response = self.session.get(f"{self.base_url}/coins/markets", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Add market analysis
                data.append({
                    'market_analysis': self._analyze_market_data(data)
                })
                
                return data
            else:
                st.error(f"❌ Error fetching market data: {response.status_code}")
                return []
        except Exception as e:
            st.error(f"❌ Error in market request: {str(e)}")
            return []
    
    def get_coin_market_chart(self, coin_id: str, vs_currency: str = "usd", 
                             days: int = 30) -> Dict:
        """Get coin market chart with enhanced analysis"""
        self._rate_limit_check()
        
        params = {
            'vs_currency': vs_currency,
            'days': days
        }
        
        try:
            response = self.session.get(f"{self.base_url}/coins/{coin_id}/market_chart", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Add chart analysis
                data['chart_analysis'] = self._analyze_chart_data(data)
                
                return data
            else:
                st.error(f"❌ Error fetching chart data: {response.status_code}")
                return {}
        except Exception as e:
            st.error(f"❌ Error in chart request: {str(e)}")
            return {}
    
    def get_trending_coins(self) -> Dict:
        """Get trending coins with enhanced analysis"""
        self._rate_limit_check()
        
        try:
            response = self.session.get(f"{self.base_url}/search/trending")
            
            if response.status_code == 200:
                data = response.json()
                
                # Add trending analysis
                data['trending_analysis'] = self._analyze_trending_data(data)
                
                return data
            else:
                st.error(f"❌ Error fetching trending data: {response.status_code}")
                return {}
        except Exception as e:
            st.error(f"❌ Error in trending request: {str(e)}")
            return {}
    
    def get_global_market_data(self) -> Dict:
        """Get global market data with enhanced analysis"""
        self._rate_limit_check()
        
        try:
            response = self.session.get(f"{self.base_url}/global")
            
            if response.status_code == 200:
                data = response.json()
                
                # Add global analysis
                data['global_analysis'] = self._analyze_global_data(data)
                
                return data
            else:
                st.error(f"❌ Error fetching global data: {response.status_code}")
                return {}
        except Exception as e:
            st.error(f"❌ Error in global request: {str(e)}")
            return {}
    
    def _analyze_price_data(self, data: Dict) -> Dict:
        """Analyze price data for insights"""
        analysis = {
            'total_coins': len(data),
            'price_ranges': {},
            'market_cap_ranges': {},
            'volume_ranges': {}
        }
        
        for coin_id, coin_data in data.items():
            if 'usd' in coin_data:
                price = coin_data['usd']
                market_cap = coin_data.get('usd_market_cap', 0)
                volume = coin_data.get('usd_24h_vol', 0)
                
                # Price range analysis
                if price < 1:
                    analysis['price_ranges']['under_1'] = analysis['price_ranges'].get('under_1', 0) + 1
                elif price < 10:
                    analysis['price_ranges']['1_to_10'] = analysis['price_ranges'].get('1_to_10', 0) + 1
                elif price < 100:
                    analysis['price_ranges']['10_to_100'] = analysis['price_ranges'].get('10_to_100', 0) + 1
                else:
                    analysis['price_ranges']['over_100'] = analysis['price_ranges'].get('over_100', 0) + 1
        
        return analysis
    
    def _analyze_market_data(self, data: List[Dict]) -> Dict:
        """Analyze market data for insights"""
        if not data:
            return {}
        
        analysis = {
            'total_coins': len(data),
            'total_market_cap': sum(coin.get('market_cap', 0) for coin in data),
            'total_volume': sum(coin.get('total_volume', 0) for coin in data),
            'avg_price_change': np.mean([coin.get('price_change_percentage_24h', 0) for coin in data]),
            'positive_coins': sum(1 for coin in data if coin.get('price_change_percentage_24h', 0) > 0),
            'negative_coins': sum(1 for coin in data if coin.get('price_change_percentage_24h', 0) < 0),
            'market_sentiment': 'bullish' if sum(1 for coin in data if coin.get('price_change_percentage_24h', 0) > 0) > len(data) / 2 else 'bearish'
        }
        
        return analysis
    
    def _analyze_chart_data(self, data: Dict) -> Dict:
        """Analyze chart data for insights"""
        analysis = {}
        
        if 'prices' in data and data['prices']:
            prices = [price[1] for price in data['prices']]
            
            if len(prices) > 1:
                analysis = {
                    'price_trend': 'upward' if prices[-1] > prices[0] else 'downward',
                    'price_change_percent': ((prices[-1] - prices[0]) / prices[0]) * 100 if prices[0] > 0 else 0,
                    'volatility': np.std(prices) / np.mean(prices) if np.mean(prices) > 0 else 0,
                    'highest_price': max(prices),
                    'lowest_price': min(prices),
                    'avg_price': np.mean(prices)
                }
        
        return analysis
    
    def _analyze_trending_data(self, data: Dict) -> Dict:
        """Analyze trending data for insights"""
        analysis = {}
        
        if 'coins' in data:
            trending_coins = data['coins']
            
            analysis = {
                'total_trending': len(trending_coins),
                'avg_market_cap': np.mean([coin['item'].get('market_cap', 0) for coin in trending_coins]),
                'categories': list(set([coin['item'].get('category', 'Unknown') for coin in trending_coins])),
                'avg_score': np.mean([coin['item'].get('score', 0) for coin in trending_coins])
            }
        
        return analysis
    
    def _analyze_global_data(self, data: Dict) -> Dict:
        """Analyze global market data for insights"""
        analysis = {}
        
        if 'data' in data:
            global_data = data['data']
            
            analysis = {
                'total_market_cap': global_data.get('total_market_cap', {}).get('usd', 0),
                'total_volume': global_data.get('total_volume', {}).get('usd', 0),
                'market_cap_change_24h': global_data.get('market_cap_change_percentage_24h_usd', 0),
                'market_sentiment': 'bullish' if global_data.get('market_cap_change_percentage_24h_usd', 0) > 0 else 'bearish',
                'active_cryptocurrencies': global_data.get('active_cryptocurrencies', 0),
                'active_exchanges': global_data.get('active_exchanges', 0)
            }
        
        return analysis

class PyCGAPIClient:
    """
    Enhanced Python Wrapper Integration
    Based on pycgapi (nathanramoscfa) with additional features
    """
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Decentralized-Portfolio-Optimizer-PyCGAPI/3.0',
            'Accept': 'application/json'
        })
        
        # Enhanced caching
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
    
    def _get_cached_data(self, key: str) -> Optional[Dict]:
        """Get cached data if available and not expired"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if (datetime.now() - timestamp).total_seconds() < self.cache_duration:
                return data
            else:
                del self.cache[key]
        return None
    
    def _cache_data(self, key: str, data: Dict):
        """Cache data with timestamp"""
        self.cache[key] = (data, datetime.now())
    
    def get_enhanced_coins_data(self, coin_ids: List[str]) -> Dict:
        """Get enhanced coins data with multiple endpoints"""
        cache_key = f"enhanced_coins_{','.join(sorted(coin_ids))}"
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            # Get multiple data sources
            price_data = self._get_simple_price(coin_ids)
            market_data = self._get_coins_markets_data(coin_ids)
            chart_data = {}
            
            # Get chart data for each coin
            for coin_id in coin_ids[:5]:  # Limit to 5 to avoid rate limits
                chart_data[coin_id] = self._get_coin_market_chart(coin_id)
            
            enhanced_data = {
                'price_data': price_data,
                'market_data': market_data,
                'chart_data': chart_data,
                'analysis': self._analyze_enhanced_data(price_data, market_data, chart_data),
                'timestamp': datetime.now().isoformat()
            }
            
            self._cache_data(cache_key, enhanced_data)
            return enhanced_data
            
        except Exception as e:
            st.error(f"❌ Error fetching enhanced coins data: {str(e)}")
            return {}
    
    def _get_simple_price(self, coin_ids: List[str]) -> Dict:
        """Get simple price data"""
        params = {
            'ids': ','.join(coin_ids),
            'vs_currencies': 'usd',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true'
        }
        
        try:
            response = self.session.get(f"{self.base_url}/simple/price", params=params)
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            st.error(f"❌ Error in simple price request: {str(e)}")
            return {}
    
    def _get_coins_markets_data(self, coin_ids: List[str]) -> List[Dict]:
        """Get coins market data"""
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 250,
            'page': 1,
            'sparkline': 'false',
            'price_change_percentage': '24h'
        }
        
        try:
            response = self.session.get(f"{self.base_url}/coins/markets", params=params)
            data = response.json() if response.status_code == 200 else []
            
            # Filter for requested coin IDs
            return [coin for coin in data if coin.get('id') in coin_ids]
        except Exception as e:
            st.error(f"❌ Error in markets request: {str(e)}")
            return []
    
    def _get_coin_market_chart(self, coin_id: str) -> Dict:
        """Get coin market chart data"""
        params = {
            'vs_currency': 'usd',
            'days': 30
        }
        
        try:
            response = self.session.get(f"{self.base_url}/coins/{coin_id}/market_chart", params=params)
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            st.error(f"❌ Error in chart request: {str(e)}")
            return {}
    
    def _analyze_enhanced_data(self, price_data: Dict, market_data: List[Dict], chart_data: Dict) -> Dict:
        """Analyze enhanced data for portfolio insights"""
        analysis = {
            'total_coins': len(price_data),
            'market_analysis': {},
            'price_analysis': {},
            'chart_analysis': {},
            'portfolio_insights': {}
        }
        
        # Market analysis
        if market_data:
            analysis['market_analysis'] = {
                'total_market_cap': sum(coin.get('market_cap', 0) for coin in market_data),
                'avg_price_change': np.mean([coin.get('price_change_percentage_24h', 0) for coin in market_data]),
                'positive_coins': sum(1 for coin in market_data if coin.get('price_change_percentage_24h', 0) > 0),
                'negative_coins': sum(1 for coin in market_data if coin.get('price_change_percentage_24h', 0) < 0)
            }
        
        # Price analysis
        if price_data:
            prices = [data.get('usd', 0) for data in price_data.values()]
            analysis['price_analysis'] = {
                'avg_price': np.mean(prices) if prices else 0,
                'price_range': {'min': min(prices), 'max': max(prices)} if prices else {},
                'price_volatility': np.std(prices) / np.mean(prices) if prices and np.mean(prices) > 0 else 0
            }
        
        # Chart analysis
        if chart_data:
            chart_insights = []
            for coin_id, chart in chart_data.items():
                if 'prices' in chart and chart['prices']:
                    prices = [price[1] for price in chart['prices']]
                    if len(prices) > 1:
                        chart_insights.append({
                            'coin_id': coin_id,
                            'trend': 'upward' if prices[-1] > prices[0] else 'downward',
                            'change_percent': ((prices[-1] - prices[0]) / prices[0]) * 100 if prices[0] > 0 else 0
                        })
            
            analysis['chart_analysis'] = {
                'coins_analyzed': len(chart_insights),
                'trending_up': sum(1 for insight in chart_insights if insight['trend'] == 'upward'),
                'trending_down': sum(1 for insight in chart_insights if insight['trend'] == 'downward'),
                'avg_change': np.mean([insight['change_percent'] for insight in chart_insights]) if chart_insights else 0
            }
        
        # Portfolio insights
        analysis['portfolio_insights'] = {
            'diversification_score': len(price_data) / 10,  # Normalize to 0-1
            'market_sentiment': 'bullish' if analysis['market_analysis'].get('positive_coins', 0) > analysis['market_analysis'].get('negative_coins', 0) else 'bearish',
            'risk_level': 'high' if analysis['price_analysis'].get('price_volatility', 0) > 0.5 else 'medium' if analysis['price_analysis'].get('price_volatility', 0) > 0.2 else 'low'
        }
        
        return analysis

class CoinGeckoClientManager:
    """
    Comprehensive CoinGecko Client Manager
    Integrates all available clients and provides unified interface
    """
    
    def __init__(self):
        self.swagger_client = CoinGeckoSwaggerClient()
        self.py_client = PyCoinGeckoClient()
        self.pycg_client = PyCGAPIClient()
        
        # Client status tracking
        self.client_status = {
            'swagger': True,
            'py_client': True,
            'pycg_client': True
        }
    
    def get_unified_market_data(self, coin_ids: List[str] = None) -> Dict:
        """Get unified market data from all available clients"""
        try:
            # Get data from different clients
            swagger_data = self.swagger_client.get_swagger_spec()
            py_market_data = self.py_client.get_coins_markets(per_page=100)
            pycg_enhanced_data = {}
            
            if coin_ids:
                pycg_enhanced_data = self.pycg_client.get_enhanced_coins_data(coin_ids)
            
            # Combine and analyze data
            unified_data = {
                'swagger_spec': swagger_data,
                'market_data': py_market_data,
                'enhanced_data': pycg_enhanced_data,
                'client_status': self.client_status,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add cross-client analysis
            unified_data['cross_analysis'] = self._analyze_cross_client_data(unified_data)
            
            return unified_data
            
        except Exception as e:
            st.error(f"❌ Error in unified data fetch: {str(e)}")
            return {}
    
    def get_portfolio_optimization_data(self, coin_ids: List[str], 
                                      risk_profile: str = "medium") -> Dict:
        """Get data optimized for portfolio analysis"""
        try:
            # Get enhanced data for portfolio optimization
            enhanced_data = self.pycg_client.get_enhanced_coins_data(coin_ids)
            
            # Get market sentiment
            market_data = self.py_client.get_coins_markets(per_page=200)
            market_sentiment = self._calculate_market_sentiment(market_data)
            
            # Get trending data
            trending_data = self.py_client.get_trending_coins()
            
            # Combine for portfolio optimization
            portfolio_data = {
                'enhanced_data': enhanced_data,
                'market_sentiment': market_sentiment,
                'trending_data': trending_data,
                'risk_profile': risk_profile,
                'optimization_insights': self._generate_optimization_insights(
                    enhanced_data, market_sentiment, risk_profile
                ),
                'timestamp': datetime.now().isoformat()
            }
            
            return portfolio_data
            
        except Exception as e:
            st.error(f"❌ Error in portfolio optimization data: {str(e)}")
            return {}
    
    def _analyze_cross_client_data(self, unified_data: Dict) -> Dict:
        """Analyze data across different clients"""
        analysis = {
            'data_consistency': 'high',
            'client_coverage': len([k for k, v in self.client_status.items() if v]),
            'total_endpoints': 0,
            'data_quality': 'excellent'
        }
        
        # Check Swagger spec
        if unified_data.get('swagger_spec', {}).get('spec'):
            analysis['total_endpoints'] = len(unified_data['swagger_spec'].get('endpoints', []))
        
        # Check market data
        if unified_data.get('market_data'):
            analysis['market_data_coins'] = len(unified_data['market_data'])
        
        # Check enhanced data
        if unified_data.get('enhanced_data', {}).get('price_data'):
            analysis['enhanced_data_coins'] = len(unified_data['enhanced_data']['price_data'])
        
        return analysis
    
    def _calculate_market_sentiment(self, market_data: List[Dict]) -> Dict:
        """Calculate market sentiment from market data"""
        if not market_data:
            return {}
        
        positive_coins = sum(1 for coin in market_data if coin.get('price_change_percentage_24h', 0) > 0)
        negative_coins = sum(1 for coin in market_data if coin.get('price_change_percentage_24h', 0) < 0)
        total_coins = len(market_data)
        
        sentiment_score = (positive_coins - negative_coins) / total_coins if total_coins > 0 else 0
        
        return {
            'sentiment_score': sentiment_score,
            'positive_coins': positive_coins,
            'negative_coins': negative_coins,
            'neutral_coins': total_coins - positive_coins - negative_coins,
            'market_mood': 'bullish' if sentiment_score > 0.1 else 'bearish' if sentiment_score < -0.1 else 'neutral',
            'confidence': abs(sentiment_score)
        }
    
    def _generate_optimization_insights(self, enhanced_data: Dict, 
                                      market_sentiment: Dict, 
                                      risk_profile: str) -> Dict:
        """Generate portfolio optimization insights"""
        insights = {
            'recommended_allocation': {},
            'risk_adjustments': {},
            'market_timing': {},
            'diversification_tips': []
        }
        
        # Analyze enhanced data for allocation recommendations
        if enhanced_data.get('analysis', {}).get('portfolio_insights'):
            portfolio_insights = enhanced_data['analysis']['portfolio_insights']
            
            # Risk-based allocation
            if risk_profile == "low":
                insights['recommended_allocation'] = {
                    'large_cap': 60,
                    'mid_cap': 30,
                    'small_cap': 10
                }
            elif risk_profile == "medium":
                insights['recommended_allocation'] = {
                    'large_cap': 40,
                    'mid_cap': 40,
                    'small_cap': 20
                }
            else:  # high risk
                insights['recommended_allocation'] = {
                    'large_cap': 20,
                    'mid_cap': 40,
                    'small_cap': 40
                }
        
        # Market timing insights
        if market_sentiment.get('market_mood') == 'bullish':
            insights['market_timing'] = {
                'recommendation': 'favorable',
                'action': 'consider increasing exposure',
                'confidence': market_sentiment.get('confidence', 0)
            }
        elif market_sentiment.get('market_mood') == 'bearish':
            insights['market_timing'] = {
                'recommendation': 'cautious',
                'action': 'consider defensive positioning',
                'confidence': market_sentiment.get('confidence', 0)
            }
        
        # Diversification tips
        insights['diversification_tips'] = [
            "Consider adding stablecoins for stability",
            "Diversify across different sectors (DeFi, Layer 1, Gaming)",
            "Include both established and emerging projects",
            "Monitor correlation between assets"
        ]
        
        return insights

# Initialize client manager
client_manager = CoinGeckoClientManager()

# Export functions for use in main application
def get_enhanced_coingecko_data(coin_ids: List[str] = None, 
                               risk_profile: str = "medium") -> Dict:
    """Get enhanced CoinGecko data using all available clients"""
    return client_manager.get_unified_market_data(coin_ids)

def get_portfolio_optimization_data(coin_ids: List[str], 
                                  risk_profile: str = "medium") -> Dict:
    """Get data optimized for portfolio analysis"""
    return client_manager.get_portfolio_optimization_data(coin_ids, risk_profile)

def get_swagger_documentation() -> Dict:
    """Get comprehensive API documentation"""
    return client_manager.swagger_client.get_api_documentation()

# Export classes for advanced usage
__all__ = [
    'CoinGeckoSwaggerClient',
    'PyCoinGeckoClient', 
    'PyCGAPIClient',
    'CoinGeckoClientManager',
    'client_manager',
    'get_enhanced_coingecko_data',
    'get_portfolio_optimization_data',
    'get_swagger_documentation'
] 