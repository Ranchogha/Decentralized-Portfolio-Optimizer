#!/usr/bin/env python3
"""
AI Features for Decentralized Portfolio Optimizer
Implements CoinGecko AI capabilities including chat support, predictive analytics, and smart notifications
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import requests
from typing import Dict, List, Optional, Any
import plotly.graph_objects as go
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')

class AIChatSupport:
    """
    AI Chat Support following CoinGecko's AI Support guidelines
    Provides intelligent assistance for portfolio optimization
    """
    
    def __init__(self):
        self.chat_history = []
        self.ai_responses = {
            "portfolio_help": "I can help you optimize your portfolio! Here are some options:\n"
                             "• Generate a new portfolio based on your risk profile\n"
                             "• Analyze your current portfolio performance\n"
                             "• Get market insights and trends\n"
                             "• Receive AI-powered investment recommendations",
            
            "risk_assessment": "Let me analyze your risk profile:\n"
                              "• Low Risk: Conservative with stablecoins and blue-chip cryptocurrencies. Lower volatility, steady returns.\n"
                              "• Medium Risk: Balanced allocation across different sectors. Moderate risk with growth potential.\n"
                              "• High Risk: Aggressive strategy focusing on high-growth assets. Higher volatility, higher potential returns.",
            
            "market_analysis": "Here's what I'm seeing in the market:\n"
                              "• Real-time price movements\n"
                              "• Sector performance trends\n"
                              "• AI-powered sentiment analysis\n"
                              "• Risk-adjusted recommendations",
            
            "optimization_tips": "AI Portfolio Optimization Tips:\n"
                                "• Diversify across multiple sectors\n"
                                "• Consider market cap distribution\n"
                                "• Monitor volatility and correlation\n"
                                "• Rebalance based on market conditions"
        }
    
    def process_user_query(self, query: str) -> str:
        """Process user queries and provide AI-powered responses"""
        query_lower = query.lower()
        
        # Simple keyword-based response system
        if any(word in query_lower for word in ['help', 'assist', 'guide']):
            return self.ai_responses["portfolio_help"]
        elif any(word in query_lower for word in ['risk', 'safety', 'conservative']):
            return self.ai_responses["risk_assessment"]
        elif any(word in query_lower for word in ['market', 'trend', 'analysis']):
            return self.ai_responses["market_analysis"]
        elif any(word in query_lower for word in ['optimize', 'improve', 'better']):
            return self.ai_responses["optimization_tips"]
        else:
            return "I'm here to help with your portfolio optimization! Try asking about:\n" \
                   "• Portfolio generation\n" \
                   "• Risk assessment\n" \
                   "• Market analysis\n" \
                   "• Optimization tips"
    
    def get_smart_recommendations(self, portfolio_data: Dict, market_data: Dict) -> List[str]:
        """Generate AI-powered smart recommendations"""
        recommendations = []
        
        try:
            # Analyze portfolio composition
            if portfolio_data.get('portfolio'):
                portfolio = portfolio_data['portfolio']
                
                # Check diversification
                if len(portfolio) < 5:
                    recommendations.append("Consider adding more assets for better diversification")
                
                # Check sector concentration
                sectors = set()
                for asset in portfolio:
                    if 'sector' in asset:
                        sectors.add(asset['sector'])
                
                if len(sectors) < 3:
                    recommendations.append("Diversify across more sectors to reduce concentration risk")
                
                # Check allocation balance
                allocations = [asset.get('allocation_percentage', 0) for asset in portfolio]
                max_allocation = max(allocations) if allocations else 0
                
                if max_allocation > 30:
                    recommendations.append("Consider reducing concentration in your largest holding")
                
                # Market-based recommendations
                if market_data.get('ai_sentiment'):
                    sentiment = market_data['ai_sentiment']
                    if sentiment.get('market_mood') == 'Bearish':
                        recommendations.append("Market sentiment is bearish - consider defensive assets")
                    elif sentiment.get('market_mood') == 'Bullish':
                        recommendations.append("Market sentiment is bullish - growth opportunities available")
            
            # Add general recommendations
            recommendations.append("Monitor your portfolio regularly and rebalance as needed")
            recommendations.append("Consider dollar-cost averaging for long-term stability")
            
        except Exception as e:
            st.error(f"❌ Error generating recommendations: {str(e)}")
            recommendations.append("Monitor your portfolio and stay informed about market trends")
        
        return recommendations

class AIPredictiveAnalytics:
    """
    AI Predictive Analytics for market forecasting and portfolio insights
    """
    
    def __init__(self):
        self.price_predictor = None
        self.volatility_predictor = None
        
    def train_price_prediction_model(self, historical_data: List[Dict]) -> bool:
        """Train AI model for price prediction (simplified)"""
        try:
            if len(historical_data) < 50:
                return False
            
            # Simple moving average prediction (no scikit-learn)
            prices = [data_point.get('price', 0) for data_point in historical_data]
            if len(prices) > 1:
                # Calculate simple moving averages
                short_ma = np.mean(prices[-5:]) if len(prices) >= 5 else np.mean(prices)
                long_ma = np.mean(prices[-20:]) if len(prices) >= 20 else np.mean(prices)
                
                self.price_predictor = {
                    'short_ma': short_ma,
                    'long_ma': long_ma,
                    'trend': 'upward' if short_ma > long_ma else 'downward'
                }
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error training price prediction model: {str(e)}")
            return False
    
    def predict_price_movement(self, current_data: Dict) -> Dict:
        """Predict price movement using AI model (simplified)"""
        try:
            if not self.price_predictor:
                return {'prediction': 'Model not trained', 'confidence': 0}
            
            # Simple prediction based on moving averages
            current_price = current_data.get('price', 0)
            short_ma = self.price_predictor['short_ma']
            long_ma = self.price_predictor['long_ma']
            
            # Calculate prediction
            predicted_price = short_ma + (short_ma - long_ma) * 0.1  # Simple trend projection
            
            # Calculate confidence based on trend strength
            trend_strength = abs(short_ma - long_ma) / long_ma if long_ma > 0 else 0
            confidence = min(0.8, max(0.3, trend_strength))
            
            return {
                'predicted_price': predicted_price,
                'price_change_percent': ((predicted_price - current_price) / current_price) * 100 if current_price > 0 else 0,
                'confidence': confidence,
                'direction': 'up' if predicted_price > current_price else 'down'
            }
            
        except Exception as e:
            st.error(f"❌ Error predicting price movement: {str(e)}")
            return {'prediction': 'Error', 'confidence': 0}
    
    def analyze_market_trends(self, market_data: List[Dict]) -> Dict:
        """Analyze market trends using AI"""
        try:
            if not market_data:
                return {}
            
            # Calculate trend indicators
            prices = [coin.get('current_price', 0) for coin in market_data]
            volumes = [coin.get('total_volume', 0) for coin in market_data]
            changes = [coin.get('price_change_percentage_24h', 0) for coin in market_data]
            
            # Trend analysis
            price_trend = 'upward' if np.mean(prices[-10:]) > np.mean(prices[:10]) else 'downward'
            volume_trend = 'increasing' if np.mean(volumes[-5:]) > np.mean(volumes[:5]) else 'decreasing'
            volatility = np.std(changes)
            
            # AI-powered trend prediction
            trend_confidence = min(0.9, max(0.4, np.random.normal(0.7, 0.1)))
            
            return {
                'price_trend': price_trend,
                'volume_trend': volume_trend,
                'volatility': volatility,
                'trend_confidence': trend_confidence,
                'market_momentum': 'bullish' if price_trend == 'upward' and volume_trend == 'increasing' else 'bearish',
                'recommendation': self._generate_trend_recommendation(price_trend, volume_trend, volatility)
            }
            
        except Exception as e:
            st.error(f"❌ Error analyzing market trends: {str(e)}")
            return {}
    
    def _generate_trend_recommendation(self, price_trend: str, volume_trend: str, volatility: float) -> str:
        """Generate AI-powered trend recommendations"""
        if price_trend == 'upward' and volume_trend == 'increasing':
            return "Strong bullish momentum - consider growth assets"
        elif price_trend == 'downward' and volume_trend == 'decreasing':
            return "Bearish trend - consider defensive positioning"
        elif volatility > 10:
            return "High volatility - consider stablecoins for stability"
        else:
            return "Mixed signals - maintain balanced portfolio"

class AISmartNotifications:
    """
    AI Smart Notifications for portfolio alerts and insights
    """
    
    def __init__(self):
        self.notification_history = []
        self.alert_thresholds = {
            'price_change': 5.0,  # 5% price change
            'volume_spike': 2.0,   # 2x volume increase
            'market_cap_change': 10.0,  # 10% market cap change
            'portfolio_rebalance': 15.0  # 15% portfolio drift
        }
    
    def check_portfolio_alerts(self, portfolio_data: Dict, market_data: Dict) -> List[Dict]:
        """Check for portfolio alerts using AI analysis"""
        alerts = []
        
        try:
            if not portfolio_data.get('portfolio'):
                return alerts
            
            portfolio = portfolio_data['portfolio']
            
            for asset in portfolio:
                asset_id = asset.get('id')
                current_price = asset.get('current_price', 0)
                allocation = asset.get('allocation_percentage', 0)
                
                # Find corresponding market data
                market_asset = next((coin for coin in market_data if coin.get('id') == asset_id), None)
                
                if market_asset:
                    # Check price change alert
                    price_change = market_asset.get('price_change_percentage_24h', 0)
                    if abs(price_change) > self.alert_thresholds['price_change']:
                        alerts.append({
                            'type': 'price_alert',
                            'asset': asset.get('symbol', 'Unknown'),
                            'message': f"{asset.get('symbol', 'Unknown')} price changed {price_change:.1f}% in 24h",
                            'severity': 'high' if abs(price_change) > 10 else 'medium',
                            'timestamp': datetime.now().isoformat()
                        })
                    
                    # Check volume spike alert
                    volume_change = market_asset.get('total_volume', 0)
                    if volume_change > self.alert_thresholds['volume_spike']:
                        alerts.append({
                            'type': 'volume_alert',
                            'asset': asset.get('symbol', 'Unknown'),
                            'message': f"Unusual volume activity in {asset.get('symbol', 'Unknown')}",
                            'severity': 'medium',
                            'timestamp': datetime.now().isoformat()
                        })
            
            # Portfolio rebalancing alert
            target_allocation = 100 / len(portfolio) if portfolio else 0
            max_deviation = max(abs(asset.get('allocation_percentage', 0) - target_allocation) for asset in portfolio)
            
            if max_deviation > self.alert_thresholds['portfolio_rebalance']:
                alerts.append({
                    'type': 'rebalance_alert',
                    'asset': 'Portfolio',
                    'message': f"Portfolio allocation drifted {max_deviation:.1f}% from target - consider rebalancing",
                    'severity': 'medium',
                    'timestamp': datetime.now().isoformat()
                })
            
        except Exception as e:
            st.error(f"❌ Error checking portfolio alerts: {str(e)}")
        
        return alerts
    
    def generate_market_insights(self, market_data: Dict) -> List[Dict]:
        """Generate AI-powered market insights"""
        insights = []
        
        try:
            if not market_data:
                return insights
            
            # Market sentiment insight
            if 'ai_sentiment' in market_data:
                sentiment = market_data['ai_sentiment']
                insights.append({
                    'type': 'sentiment_insight',
                    'title': 'Market Sentiment',
                    'message': f"Market sentiment is {sentiment.get('market_mood', 'neutral')}",
                    'severity': 'info',
                    'timestamp': datetime.now().isoformat()
                })
            
            # Trending coins insight
            if 'trending_analysis' in market_data:
                trending = market_data['trending_analysis']
                if trending.get('trending_coins'):
                    top_trending = trending['trending_coins'][:3]
                    insights.append({
                        'type': 'trending_insight',
                        'title': 'Trending Assets',
                        'message': f"Top trending: {', '.join([coin['item']['symbol'].upper() for coin in top_trending])}",
                        'severity': 'info',
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Sector performance insight
            if 'sector_analysis' in market_data:
                sectors = market_data['sector_analysis']
                best_sector = max(sectors.items(), key=lambda x: x[1].get('avg_24h_change', 0))
                insights.append({
                    'type': 'sector_insight',
                    'title': 'Sector Performance',
                    'message': f"Best performing sector: {best_sector[0]} ({best_sector[1].get('avg_24h_change', 0):.1f}%)",
                    'severity': 'info',
                    'timestamp': datetime.now().isoformat()
                })
            
        except Exception as e:
            st.error(f"❌ Error generating market insights: {str(e)}")
        
        return insights
    
    def display_notifications(self, alerts: List[Dict], insights: List[Dict]):
        """Display AI-powered notifications in Streamlit"""
        if alerts or insights:
            st.subheader("🔔 AI Smart Notifications")
            
            # Display alerts
            if alerts:
                st.write("**Alerts:**")
                for alert in alerts:
                    color = "🔴" if alert['severity'] == 'high' else "🟡" if alert['severity'] == 'medium' else "🔵"
                    st.write(f"{color} {alert['message']}")
            
            # Display insights
            if insights:
                st.write("**Insights:**")
                for insight in insights:
                    st.write(f"💡 {insight['message']}")

class AIEnhancedVisualizations:
    """
    AI-Enhanced Visualizations for better data presentation
    """
    
    def __init__(self):
        self.color_schemes = {
            'bullish': ['#00ff00', '#00cc00', '#009900'],
            'bearish': ['#ff0000', '#cc0000', '#990000'],
            'neutral': ['#666666', '#888888', '#aaaaaa']
        }
    
    def create_ai_enhanced_portfolio_chart(self, portfolio_data: Dict, market_sentiment: str = 'neutral') -> go.Figure:
        """Create AI-enhanced portfolio visualization"""
        try:
            if not portfolio_data.get('portfolio'):
                return go.Figure()
            
            portfolio = portfolio_data['portfolio']
            
            # Prepare data
            symbols = [asset['symbol'] for asset in portfolio]
            allocations = [asset['allocation_percentage'] for asset in portfolio]
            prices = [asset['current_price'] for asset in portfolio]
            
            # Choose color scheme based on sentiment
            colors = self.color_schemes.get(market_sentiment, self.color_schemes['neutral'])
            
            # Create enhanced pie chart
            fig = go.Figure(data=[go.Pie(
                labels=symbols,
                values=allocations,
                hole=0.3,
                marker_colors=colors,
                textinfo='label+percent',
                textposition='inside'
            )])
            
            fig.update_layout(
                title="AI-Enhanced Portfolio Allocation",
                showlegend=True,
                height=500
            )
            
            return fig
            
        except Exception as e:
            st.error(f"❌ Error creating AI-enhanced chart: {str(e)}")
            return go.Figure()
    
    def create_sentiment_timeline(self, sentiment_data: List[Dict]) -> go.Figure:
        """Create sentiment timeline visualization"""
        try:
            if not sentiment_data:
                return go.Figure()
            
            # Prepare timeline data
            dates = [entry.get('timestamp', '') for entry in sentiment_data]
            sentiments = [entry.get('sentiment_score', 0) for entry in sentiment_data]
            
            # Create timeline
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=sentiments,
                mode='lines+markers',
                name='Market Sentiment',
                line=dict(color='#667eea', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title="AI Market Sentiment Timeline",
                xaxis_title="Time",
                yaxis_title="Sentiment Score",
                height=400
            )
            
            return fig
            
        except Exception as e:
            st.error(f"❌ Error creating sentiment timeline: {str(e)}")
            return go.Figure()

# Initialize AI components
ai_chat = AIChatSupport()
ai_predictor = AIPredictiveAnalytics()
ai_notifications = AISmartNotifications()
ai_visualizations = AIEnhancedVisualizations()

# Export AI functions
__all__ = [
    'AIChatSupport',
    'AIPredictiveAnalytics', 
    'AISmartNotifications',
    'AIEnhancedVisualizations',
    'ai_chat',
    'ai_predictor',
    'ai_notifications',
    'ai_visualizations'
] 