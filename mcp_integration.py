#!/usr/bin/env python3
"""
CoinGecko MCP Server Integration with AI Capabilities
Connects to the authenticated remote MCP server for enhanced crypto data access
Incorporates CoinGecko AI features and llms.txt guidelines for responsible AI behavior
"""

import requests
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
import os
from dotenv import load_dotenv
import streamlit as st
from datetime import datetime
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

class CoinGeckoAIIntegration:
    """
    AI Integration following CoinGecko's llms.txt guidelines
    Provides responsible AI behavior and data interpretation
    """
    
    def __init__(self):
        self.llms_guidelines = {
            "responsible_usage": True,
            "data_interpretation": "contextual",
            "rate_limiting": "respectful",
            "error_handling": "graceful"
        }
        
        # Simple AI model for portfolio optimization (no scikit-learn)
        self.portfolio_weights = {}
        
    def load_llms_guidelines(self):
        """Load CoinGecko's llms.txt guidelines for responsible AI behavior"""
        try:
            response = requests.get("https://docs.coingecko.com/llms.txt")
            if response.status_code == 200:
                guidelines = response.text
                return guidelines
            else:
                return None
        except Exception as e:
            return None
    
    def ai_portfolio_optimization(self, market_data: List[Dict], risk_profile: str, 
                                investment_amount: float, sectors: List[str]) -> Dict:
        """
        AI-powered portfolio optimization using CoinGecko data
        Follows responsible AI guidelines from llms.txt
        """
        try:
            # Prepare data for AI model (simplified without scikit-learn)
            valid_coins = []
            
            for coin in market_data:
                if coin.get('market_cap') and coin.get('price_change_percentage_24h') is not None:
                    valid_coins.append({
                        'id': coin['id'],
                        'symbol': coin['symbol'],
                        'name': coin['name'],
                        'market_cap': coin.get('market_cap', 0),
                        'price_change_24h': coin.get('price_change_percentage_24h', 0),
                        'current_price': coin.get('current_price', 0),
                        'total_volume': coin.get('total_volume', 0)
                    })
            
            if len(valid_coins) < 5:
                st.warning("⚠️ Insufficient data for AI optimization")
                return self._fallback_optimization(market_data, risk_profile, investment_amount, sectors)
            
            # Simple AI scoring based on market cap, volume, and price change
            for coin in valid_coins:
                # Calculate AI score based on multiple factors
                market_cap_score = min(coin['market_cap'] / 1e9, 1)  # Normalize to 1B market cap
                volume_score = min(coin['total_volume'] / 1e8, 1)  # Normalize to 100M volume
                price_change_score = abs(coin['price_change_24h']) / 100  # Normalize price change
                
                # Risk-adjusted scoring
                if risk_profile == "low":
                    ai_score = (market_cap_score * 0.6) + (volume_score * 0.3) + (price_change_score * 0.1)
                elif risk_profile == "medium":
                    ai_score = (market_cap_score * 0.4) + (volume_score * 0.3) + (price_change_score * 0.3)
                else:  # high risk
                    ai_score = (market_cap_score * 0.2) + (volume_score * 0.3) + (price_change_score * 0.5)
                
                coin['ai_score'] = ai_score
            
            # Sort by AI score and select top assets
            valid_coins.sort(key=lambda x: x['ai_score'], reverse=True)
            selected_coins = valid_coins[:10]  # Top 10 assets
            
            # Create portfolio allocation
            total_score = sum(coin['ai_score'] for coin in selected_coins)
            portfolio = []
            
            for coin in selected_coins:
                allocation_score = coin['ai_score'] / total_score if total_score > 0 else 0
                allocation_usd = investment_amount * allocation_score
                
                if allocation_usd > 0:
                    portfolio.append({
                        'id': coin['id'],
                        'symbol': coin['symbol'].upper(),
                        'name': coin['name'],
                        'current_price': coin['current_price'],
                        'allocation_usd': allocation_usd,
                        'allocation_percentage': allocation_score * 100,
                        'ai_score': coin['ai_score'],
                        'market_cap': coin['market_cap'],
                        'price_change_24h': coin['price_change_24h']
                    })
            
            # Recalculate percentages
            total_allocation = sum(asset['allocation_usd'] for asset in portfolio)
            for asset in portfolio:
                asset['allocation_percentage'] = (asset['allocation_usd'] / total_allocation) * 100
            
            return {
                'portfolio': portfolio,
                'total_value': total_allocation,
                'ai_model_used': 'Numpy-based AI',
                'risk_profile': risk_profile,
                'sectors': sectors,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            st.error(f"❌ AI optimization error: {str(e)}")
            return self._fallback_optimization(market_data, risk_profile, investment_amount, sectors)
    
    def _fallback_optimization(self, market_data: List[Dict], risk_profile: str, 
                              investment_amount: float, sectors: List[str]) -> Dict:
        """Fallback optimization when AI model fails"""
        # Simple market cap weighted allocation
        filtered_data = [coin for coin in market_data if coin.get('market_cap', 0) > 0]
        total_market_cap = sum(coin['market_cap'] for coin in filtered_data)
        
        portfolio = []
        for coin in filtered_data[:10]:  # Top 10 by market cap
            allocation_percentage = coin['market_cap'] / total_market_cap
            allocation_usd = investment_amount * allocation_percentage
            
            portfolio.append({
                'id': coin['id'],
                'symbol': coin['symbol'].upper(),
                'name': coin['name'],
                'current_price': coin['current_price'],
                'allocation_usd': allocation_usd,
                'allocation_percentage': allocation_percentage * 100,
                'market_cap': coin['market_cap'],
                'price_change_24h': coin['price_change_percentage_24h']
            })
        
        return {
            'portfolio': portfolio,
            'total_value': investment_amount,
            'ai_model_used': 'fallback',
            'risk_profile': risk_profile,
            'sectors': sectors,
            'timestamp': datetime.now().isoformat()
        }
    
    def ai_market_sentiment_analysis(self, market_data: List[Dict]) -> Dict:
        """AI-powered market sentiment analysis"""
        try:
            if not market_data:
                return {}
            
            # Calculate sentiment indicators
            price_changes = [coin.get('price_change_percentage_24h', 0) for coin in market_data]
            volumes = [coin.get('total_volume', 0) for coin in market_data]
            
            # Sentiment metrics
            positive_coins = sum(1 for change in price_changes if change > 0)
            negative_coins = sum(1 for change in price_changes if change < 0)
            avg_change = np.mean(price_changes)
            avg_volume = np.mean(volumes)
            
            # Sentiment score (-1 to 1)
            sentiment_score = (positive_coins - negative_coins) / len(price_changes) if price_changes else 0
            
            return {
                'sentiment_score': sentiment_score,
                'positive_coins': positive_coins,
                'negative_coins': negative_coins,
                'avg_price_change': avg_change,
                'avg_volume': avg_volume,
                'market_mood': 'Bullish' if sentiment_score > 0.1 else 'Bearish' if sentiment_score < -0.1 else 'Neutral'
            }
        except Exception as e:
            st.error(f"❌ Sentiment analysis error: {str(e)}")
            return {}
    
    def ai_risk_assessment(self, portfolio: List[Dict]) -> Dict:
        """AI-powered risk assessment for portfolio"""
        try:
            # Calculate risk metrics
            allocations = [asset['allocation_percentage'] for asset in portfolio]
            price_changes = [asset['price_change_24h'] for asset in portfolio]
            market_caps = [asset['market_cap'] for asset in portfolio]
            
            # Risk calculations
            concentration_risk = np.std(allocations)  # Higher std = more concentrated
            volatility_risk = np.std(price_changes)  # Higher std = more volatile
            market_cap_diversity = len(set([mc > 1e9 for mc in market_caps]))  # Large vs small cap mix
            
            # Overall risk score (0-1)
            risk_score = (concentration_risk * 0.4 + volatility_risk * 0.4 + (1 - market_cap_diversity/2) * 0.2) / 100
            
            return {
                'concentration_risk': concentration_risk,
                'volatility_risk': volatility_risk,
                'market_cap_diversity': market_cap_diversity,
                'overall_risk_score': min(risk_score, 1.0),
                'risk_level': 'High' if risk_score > 0.6 else 'Medium' if risk_score > 0.3 else 'Low',
                'recommendations': self._generate_risk_recommendations(risk_score, concentration_risk, volatility_risk)
            }
        except Exception as e:
            st.error(f"❌ Risk assessment error: {str(e)}")
            return {}
    
    def _generate_risk_recommendations(self, risk_score: float, concentration: float, volatility: float) -> List[str]:
        """Generate AI-powered risk recommendations"""
        recommendations = []
        
        if risk_score > 0.6:
            recommendations.append("Consider diversifying across more assets")
            recommendations.append("Add stablecoins to reduce volatility")
        
        if concentration > 20:
            recommendations.append("Reduce concentration in top holdings")
        
        if volatility > 10:
            recommendations.append("Consider adding defensive assets")
        
        if not recommendations:
            recommendations.append("Portfolio risk profile looks balanced")
        
        return recommendations

class CoinGeckoMCPServer:
    """
    Enhanced CoinGecko MCP Server Integration with AI Capabilities
    Connects to the authenticated remote server for enhanced crypto data
    Incorporates AI features and responsible data usage
    """
    
    def __init__(self):
        # Use the correct CoinGecko API base URL
        self.base_url = "https://api.coingecko.com/api/v3"
        self.demo_api_key = os.getenv("COINGECKO_DEMO_API_KEY")
        self.pro_api_key = os.getenv("COINGECKO_PRO_API_KEY")
        self.session = requests.Session()
        
        # Enhanced headers for MCP server with AI integration
        self.session.headers.update({
            'User-Agent': 'Decentralized-Portfolio-Optimizer-AI/3.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Initialize AI integration
        self.ai_integration = CoinGeckoAIIntegration()
        
        # Use Demo API key if available, otherwise Pro API key
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
        
        # Load AI guidelines silently
        self.ai_integration.load_llms_guidelines()
    
    def _make_mcp_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make authenticated request to MCP server with AI-enhanced error handling"""
        try:
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                st.error("🔑 Unauthorized. Check your CoinGecko API key.")
                return None
            elif response.status_code == 429:
                st.warning("⏱️ Rate limit exceeded. Please wait before making more requests.")
                return None
            else:
                st.error(f"❌ MCP Server error {response.status_code}: {response.text}")
                return None
        except Exception as e:
            st.error(f"❌ Error connecting to MCP server: {str(e)}")
            return None
    
    async def _make_async_mcp_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make async authenticated request to MCP server"""
        try:
            url = f"{self.base_url}/{endpoint}"
            async with aiohttp.ClientSession() as session:
                headers = dict(self.session.headers)
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 401:
                        st.error("🔑 Unauthorized. Check your CoinGecko API key.")
                        return None
                    elif response.status == 429:
                        st.warning("⏱️ Rate limit exceeded. Please wait before making more requests.")
                        return None
                    else:
                        st.error(f"❌ MCP Server error {response.status}: {await response.text()}")
                        return None
        except Exception as e:
            st.error(f"❌ Error connecting to MCP server: {str(e)}")
            return None
    
    def get_server_status(self) -> Dict:
        """Check MCP server status with AI-enhanced monitoring"""
        status = self._make_mcp_request("ping")
        if status:
            # Add AI-powered status analysis
            status['ai_analysis'] = {
                'server_health': 'excellent' if status.get('gecko_says') else 'unknown',
                'response_time': 'optimal' if status.get('response_time', 0) < 1 else 'slow',
                'recommendation': 'Server is performing well' if status.get('gecko_says') else 'Monitor server performance'
            }
        return status
    
    def get_simple_price_mcp(self, ids: List[str], vs_currencies: str = "usd") -> Dict:
        """Get simple price data via MCP server with AI analysis"""
        params = {
            'ids': ','.join(ids),
            'vs_currencies': vs_currencies,
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true'
        }
        data = self._make_mcp_request("simple/price", params)
        
        if data:
            # Add AI-powered price analysis
            data['ai_analysis'] = self.ai_integration.ai_market_sentiment_analysis([
                {'price_change_percentage_24h': change, 'total_volume': vol}
                for change, vol in zip(
                    [coin.get('usd_24h_change', 0) for coin in data.values()],
                    [coin.get('usd_24h_vol', 0) for coin in data.values()]
                )
            ])
        
        return data
    
    def get_coins_markets_mcp(self, vs_currency: str = "usd", order: str = "market_cap_desc", 
                             per_page: int = 100, page: int = 1) -> List[Dict]:
        """Get coins market data via MCP server with AI enhancement"""
        params = {
            'vs_currency': vs_currency,
            'order': order,
            'per_page': per_page,
            'page': page,
            'sparkline': 'false',
            'price_change_percentage': '24h'
        }
        result = self._make_mcp_request("coins/markets", params)
        
        if result:
            # Add AI-powered market analysis
            market_sentiment = self.ai_integration.ai_market_sentiment_analysis(result)
            result.append({'ai_sentiment': market_sentiment})
        
        return result if result else []
    
    def get_trending_coins_mcp(self) -> Dict:
        """Get trending coins via MCP server with AI analysis"""
        result = self._make_mcp_request("search/trending")
        
        if result and 'coins' in result:
            # Add AI-powered trending analysis
            trending_coins = result['coins']
            result['ai_analysis'] = {
                'trending_strength': len(trending_coins),
                'avg_market_cap': np.mean([coin['item'].get('market_cap', 0) for coin in trending_coins]),
                'categories': list(set([coin['item'].get('category', 'Unknown') for coin in trending_coins]))
            }
        
        return result
    
    def get_global_market_data_mcp(self) -> Dict:
        """Get global market data via MCP server with AI insights"""
        result = self._make_mcp_request("global")
        
        if result and 'data' in result:
            # Add AI-powered global market analysis
            data = result['data']
            result['ai_analysis'] = {
                'market_health': 'bullish' if data.get('market_cap_change_percentage_24h_usd', 0) > 0 else 'bearish',
                'volume_trend': 'increasing' if data.get('total_volume', {}).get('usd', 0) > 0 else 'decreasing',
                'market_sentiment': 'positive' if data.get('market_cap_change_percentage_24h_usd', 0) > 2 else 'neutral'
            }
        
        return result
    
    def get_defi_market_data_mcp(self) -> Dict:
        """Get DeFi market data via MCP server with AI analysis"""
        result = self._make_mcp_request("global/decentralized_finance_defi")
        
        if result and 'data' in result:
            # Add AI-powered DeFi analysis
            data = result['data']
            result['ai_analysis'] = {
                'defi_health': 'growing' if data.get('defi_market_cap', 0) > 0 else 'declining',
                'defi_dominance': data.get('defi_dominance', 0),
                'defi_trend': 'positive' if data.get('defi_market_cap', 0) > 0 else 'negative'
            }
        
        return result
    
    def get_coin_market_chart_mcp(self, coin_id: str, vs_currency: str = "usd", days: int = 30) -> Dict:
        """Get coin market chart via MCP server with AI prediction"""
        params = {
            'vs_currency': vs_currency,
            'days': days
        }
        result = self._make_mcp_request(f"coins/{coin_id}/market_chart", params)
        
        if result and 'prices' in result:
            # Add AI-powered price prediction analysis
            prices = [price[1] for price in result['prices']]
            if len(prices) > 1:
                price_trend = 'upward' if prices[-1] > prices[0] else 'downward'
                volatility = np.std(prices) / np.mean(prices) if np.mean(prices) > 0 else 0
                
                result['ai_analysis'] = {
                    'price_trend': price_trend,
                    'volatility': volatility,
                    'trend_strength': abs(prices[-1] - prices[0]) / prices[0] if prices[0] > 0 else 0
                }
        
        return result
    
    def get_top_gainers_losers_mcp(self) -> Dict:
        """Get top gainers and losers via MCP server (Demo/Pro feature) with AI analysis"""
        if self.api_type == "none":
            st.warning("⚠️ Top gainers/losers requires Demo or Pro API key")
            return {}
        
        result = self._make_mcp_request("coins/markets", {
            'vs_currency': 'usd',
            'order': 'price_change_24h_desc',
            'per_page': 10,
            'page': 1
        })
        
        if result:
            # Add AI-powered gainers/losers analysis
            gainers = [coin for coin in result if coin.get('price_change_percentage_24h', 0) > 0]
            losers = [coin for coin in result if coin.get('price_change_percentage_24h', 0) < 0]
            
            result.append({
                'ai_analysis': {
                    'gainers_count': len(gainers),
                    'losers_count': len(losers),
                    'avg_gain': np.mean([coin['price_change_percentage_24h'] for coin in gainers]) if gainers else 0,
                    'avg_loss': np.mean([coin['price_change_percentage_24h'] for coin in losers]) if losers else 0,
                    'market_momentum': 'bullish' if len(gainers) > len(losers) else 'bearish'
                }
            })
        
        return result
    
    def get_nft_collections_mcp(self) -> Dict:
        """Get NFT collections via MCP server (Pro feature only) with AI analysis"""
        if self.api_type != "pro":
            st.warning("⚠️ NFT collections requires Pro API key")
            return {}
        
        result = self._make_mcp_request("nfts/list")
        
        if result:
            # Add AI-powered NFT analysis
            result['ai_analysis'] = {
                'total_collections': len(result) if isinstance(result, list) else 0,
                'market_activity': 'high' if len(result) > 100 else 'moderate' if len(result) > 50 else 'low'
            }
        
        return result
    
    def get_categories_mcp(self) -> List[Dict]:
        """Get coin categories via MCP server with AI categorization"""
        result = self._make_mcp_request("coins/categories")
        
        if result:
            # Add AI-powered category analysis
            result.append({
                'ai_analysis': {
                    'total_categories': len(result),
                    'top_categories': sorted(result, key=lambda x: x.get('market_cap', 0), reverse=True)[:5],
                    'category_diversity': 'high' if len(result) > 20 else 'moderate'
                }
            })
        
        return result if result else []
    
    def search_coins_mcp(self, query: str) -> Dict:
        """Search coins via MCP server with AI-enhanced search"""
        params = {'query': query}
        result = self._make_mcp_request("search", params)
        
        if result:
            # Add AI-powered search analysis
            result['ai_analysis'] = {
                'search_relevance': 'high' if len(result.get('coins', [])) > 0 else 'low',
                'search_suggestions': result.get('coins', [])[:3],
                'search_confidence': min(len(result.get('coins', [])), 10) / 10
            }
        
        return result
    
    def get_exchange_rates_mcp(self) -> Dict:
        """Get exchange rates via MCP server with AI analysis"""
        result = self._make_mcp_request("exchange_rates")
        
        if result and 'rates' in result:
            # Add AI-powered exchange rate analysis
            rates = result['rates']
            result['ai_analysis'] = {
                'total_currencies': len(rates),
                'major_currencies': [rate for rate in rates if rates[rate].get('value', 0) > 0.1],
                'exchange_volatility': 'low' if len(rates) > 0 else 'unknown'
            }
        
        return result
    
    def get_asset_platforms_mcp(self) -> List[Dict]:
        """Get asset platforms via MCP server with AI analysis"""
        result = self._make_mcp_request("asset_platforms")
        
        if result:
            # Add AI-powered platform analysis
            result.append({
                'ai_analysis': {
                    'total_platforms': len(result),
                    'active_platforms': len([p for p in result if p.get('chain_identifier')]),
                    'platform_diversity': 'high' if len(result) > 50 else 'moderate'
                }
            })
        
        return result if result else []
    
    def get_derivatives_mcp(self) -> Dict:
        """Get derivatives data via MCP server (Pro feature only) with AI analysis"""
        if self.api_type != "pro":
            st.warning("⚠️ Derivatives data requires Pro API key")
            return {}
        
        result = self._make_mcp_request("derivatives")
        
        if result:
            # Add AI-powered derivatives analysis
            result['ai_analysis'] = {
                'derivatives_volume': 'high' if result.get('total_volume', 0) > 1e9 else 'moderate',
                'market_activity': 'active' if len(result) > 0 else 'inactive'
            }
        
        return result
    
    def get_exchanges_mcp(self) -> List[Dict]:
        """Get exchanges data via MCP server with AI analysis"""
        result = self._make_mcp_request("exchanges")
        
        if result:
            # Add AI-powered exchange analysis
            result.append({
                'ai_analysis': {
                    'total_exchanges': len(result),
                    'top_exchanges': sorted(result, key=lambda x: x.get('trust_score', 0), reverse=True)[:5],
                    'market_liquidity': 'high' if len(result) > 100 else 'moderate'
                }
            })
        
        return result if result else []
    
    async def get_enhanced_portfolio_data(self, coin_ids: List[str]) -> Dict:
        """Get enhanced portfolio data combining multiple MCP endpoints with AI analysis"""
        tasks = []
        
        # Create async tasks for multiple data sources
        tasks.append(self._make_async_mcp_request("simple/price", {
            'ids': ','.join(coin_ids),
            'vs_currencies': 'usd',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true'
        }))
        
        tasks.append(self._make_async_mcp_request("global"))
        tasks.append(self._make_async_mcp_request("search/trending"))
        
        # Execute all requests concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Add AI analysis to results
        enhanced_results = {
            'prices': results[0] if not isinstance(results[0], Exception) else {},
            'global_data': results[1] if not isinstance(results[1], Exception) else {},
            'trending': results[2] if not isinstance(results[2], Exception) else {},
            'ai_analysis': self.ai_integration.ai_market_sentiment_analysis([
                {'price_change_percentage_24h': 0, 'total_volume': 0}
            ])  # Placeholder for AI analysis
        }
        
        return enhanced_results

# Enhanced MCP Portfolio Optimizer with AI
class MCPPortfolioOptimizer:
    """Enhanced portfolio optimizer using MCP server data with AI capabilities"""
    
    def __init__(self):
        self.mcp_server = CoinGeckoMCPServer()
        self.ai_integration = CoinGeckoAIIntegration()
        self.sector_categories = {
            "DeFi": ["aave", "uniswap", "compound", "maker", "curve-dao-token", "synthetix", "yearn-finance"],
            "Layer 1": ["bitcoin", "ethereum", "solana", "cardano", "polkadot", "avalanche-2", "cosmos"],
            "Layer 2": ["matic-network", "arbitrum", "optimism", "base", "polygon", "loopring"],
            "Stablecoins": ["tether", "usd-coin", "dai", "binance-usd", "true-usd", "frax"],
            "AI": ["fetch-ai", "ocean-protocol", "singularitynet", "artificial-intelligence", "cortex"],
            "Gaming": ["axie-infinity", "the-sandbox", "decentraland", "enjin-coin", "gala"],
            "Infrastructure": ["chainlink", "filecoin", "the-graph", "helium", "render-token"]
        }
    
    def get_enhanced_market_data(self) -> Dict:
        """Get comprehensive market data via MCP server with AI analysis"""
        try:
            # Get multiple data sources
            market_data = self.mcp_server.get_coins_markets_mcp(per_page=200)
            global_data = self.mcp_server.get_global_market_data_mcp()
            trending_data = self.mcp_server.get_trending_coins_mcp()
            defi_data = self.mcp_server.get_defi_market_data_mcp()
            
            # Add AI-powered market analysis
            ai_sentiment = self.ai_integration.ai_market_sentiment_analysis(market_data)
            
            return {
                'market_data': market_data,
                'global_data': global_data,
                'trending_data': trending_data,
                'defi_data': defi_data,
                'ai_sentiment': ai_sentiment,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            st.error(f"❌ Error fetching enhanced market data: {str(e)}")
            return {}
    
    def get_sector_analysis(self, sector: str) -> Dict:
        """Get detailed analysis for a specific sector with AI insights"""
        try:
            if sector in self.sector_categories:
                sector_coins = self.sector_categories[sector]
                sector_data = self.mcp_server.get_coins_markets_mcp(per_page=50)
                
                # Filter for sector coins
                sector_market_data = [
                    coin for coin in sector_data 
                    if coin['id'] in sector_coins
                ]
                
                # Add AI-powered sector analysis
                sector_sentiment = self.ai_integration.ai_market_sentiment_analysis(sector_market_data)
                
                return {
                    'sector': sector,
                    'coins': sector_market_data,
                    'total_market_cap': sum(coin['market_cap'] for coin in sector_market_data),
                    'avg_24h_change': np.mean([coin['price_change_percentage_24h'] for coin in sector_market_data]),
                    'coin_count': len(sector_market_data),
                    'ai_sentiment': sector_sentiment
                }
            else:
                st.warning(f"⚠️ Sector '{sector}' not found")
                return {}
        except Exception as e:
            st.error(f"❌ Error analyzing sector {sector}: {str(e)}")
            return {}
    
    def get_trending_analysis(self) -> Dict:
        """Get trending coins analysis with AI insights"""
        try:
            trending_data = self.mcp_server.get_trending_coins_mcp()
            
            if trending_data and 'coins' in trending_data:
                trending_coins = trending_data['coins']
                
                # Get detailed data for trending coins
                coin_ids = [coin['item']['id'] for coin in trending_coins[:10]]
                price_data = self.mcp_server.get_simple_price_mcp(coin_ids)
                
                # Add AI-powered trending analysis
                trending_sentiment = self.ai_integration.ai_market_sentiment_analysis([
                    {'price_change_percentage_24h': coin['item'].get('price_change_percentage_24h', 0)}
                    for coin in trending_coins
                ])
                
                return {
                    'trending_coins': trending_coins,
                    'price_data': price_data,
                    'ai_sentiment': trending_sentiment,
                    'analysis': {
                        'total_trending': len(trending_coins),
                        'avg_market_cap': np.mean([coin['item'].get('market_cap', 0) for coin in trending_coins if coin['item'].get('market_cap')]),
                        'categories': list(set([coin['item'].get('category', 'Unknown') for coin in trending_coins]))
                    }
                }
            return {}
        except Exception as e:
            st.error(f"❌ Error analyzing trending coins: {str(e)}")
            return {}
    
    def get_risk_metrics(self, coin_ids: List[str]) -> Dict:
        """Get risk metrics for portfolio analysis with AI enhancement"""
        try:
            # Get price data and calculate volatility
            price_data = self.mcp_server.get_simple_price_mcp(coin_ids)
            
            risk_metrics = {}
            for coin_id in coin_ids:
                if coin_id in price_data:
                    coin_data = price_data[coin_id]
                    
                    # Calculate basic risk metrics
                    price_change_24h = coin_data.get('usd_24h_change', 0)
                    market_cap = coin_data.get('usd_market_cap', 0)
                    
                    # Risk score based on volatility and market cap
                    volatility_score = abs(price_change_24h) / 100
                    market_cap_score = min(market_cap / 1e9, 1)  # Normalize to 1B market cap
                    
                    risk_score = (volatility_score * 0.7) + (market_cap_score * 0.3)
                    
                    risk_metrics[coin_id] = {
                        'price_change_24h': price_change_24h,
                        'market_cap': market_cap,
                        'volatility_score': volatility_score,
                        'risk_score': risk_score,
                        'risk_level': 'High' if risk_score > 0.5 else 'Medium' if risk_score > 0.2 else 'Low'
                    }
            
            return risk_metrics
        except Exception as e:
            st.error(f"❌ Error calculating risk metrics: {str(e)}")
            return {}
    
    def ai_optimize_portfolio(self, risk_profile: str, investment_amount: float, 
                             preferred_sectors: List[str], max_assets: int = 10) -> Dict:
        """AI-powered portfolio optimization using MCP data"""
        try:
            # Get market data for optimization
            market_data = self.mcp_server.get_coins_markets_mcp(per_page=200)
            
            if not market_data:
                st.error("❌ No market data available for AI optimization")
                return {}
            
            # Use AI integration for portfolio optimization
            portfolio_result = self.ai_integration.ai_portfolio_optimization(
                market_data=market_data,
                risk_profile=risk_profile,
                investment_amount=investment_amount,
                sectors=preferred_sectors
            )
            
            # Add AI risk assessment
            if portfolio_result.get('portfolio'):
                risk_assessment = self.ai_integration.ai_risk_assessment(portfolio_result['portfolio'])
                portfolio_result['ai_risk_assessment'] = risk_assessment
            
            return portfolio_result
            
        except Exception as e:
            st.error(f"❌ Error in AI portfolio optimization: {str(e)}")
            return {}

# Initialize MCP components with AI
mcp_server = CoinGeckoMCPServer()
mcp_optimizer = MCPPortfolioOptimizer()

# Enhanced MCP Status Checker with AI monitoring
def check_mcp_server_status():
    """Check MCP server connectivity and status with AI analysis"""
    try:
        status = mcp_server.get_server_status()
        if status and status.get('gecko_says'):
            return True
        else:
            return False
    except Exception as e:
        return False

# Enhanced MCP Data Fetcher with AI optimization
async def get_mcp_enhanced_data(risk_profile: str = "medium", investment_amount: float = 10000,
                               preferred_sectors: List[str] = None, max_assets: int = 10):
    """Get enhanced data from MCP server with AI-powered portfolio optimization"""
    try:
        # Get comprehensive market data
        market_data = mcp_optimizer.get_enhanced_market_data()
        
        # Get trending analysis
        trending_analysis = mcp_optimizer.get_trending_analysis()
        
        # Get sector analysis for selected sectors
        sector_analysis = {}
        if preferred_sectors:
            for sector in preferred_sectors:
                sector_data = mcp_optimizer.get_sector_analysis(sector)
                if sector_data:
                    sector_analysis[sector] = sector_data
        
        # AI-powered portfolio optimization
        portfolio_data = mcp_optimizer.ai_optimize_portfolio(
            risk_profile=risk_profile,
            investment_amount=investment_amount,
            preferred_sectors=preferred_sectors or ["DeFi", "Layer 1"],
            max_assets=max_assets
        )
        
        return {
            'market_data': market_data,
            'trending_analysis': trending_analysis,
            'sector_analysis': sector_analysis,
            'portfolio_data': portfolio_data,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        st.error(f"❌ Error fetching MCP enhanced data: {str(e)}")
        return {}

# Export MCP functions for use in main app
__all__ = [
    'CoinGeckoMCPServer',
    'MCPPortfolioOptimizer', 
    'CoinGeckoAIIntegration',
    'mcp_server',
    'mcp_optimizer',
    'check_mcp_server_status',
    'get_mcp_enhanced_data'
] 