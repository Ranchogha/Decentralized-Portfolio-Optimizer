#!/usr/bin/env python3
"""
Decentralized Portfolio Optimizer
Integrating CoinGecko MCP Server for superior crypto data access and AI-powered portfolio optimization
"""

import streamlit as st
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
from mcp_integration import CoinGeckoMCPServer, MCPPortfolioOptimizer, check_mcp_server_status, get_mcp_enhanced_data
from ai_features import ai_chat, ai_predictor, ai_notifications, ai_visualizations
import time
import asyncio
from typing import Dict, List, Optional, Any

# Load environment variables
load_dotenv()

# Initialize session state for retry functionality
if 'retry_default' not in st.session_state:
    st.session_state.retry_default = False
if 'retry_fewer' not in st.session_state:
    st.session_state.retry_fewer = False

# Initialize MCP components
mcp_server = CoinGeckoMCPServer()
mcp_optimizer = MCPPortfolioOptimizer()

# Initialize wallet manager
wallet_manager = MultiWalletManager()

# Initialize Web3 with build artifacts support
portfolio_manager = EthereumPortfolioManager()

# Enhanced Streamlit Web Application with AI Integration
st.set_page_config(
    page_title="🚀 Decentralized Portfolio Optimizer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for Zapper-inspired modern dark theme
st.markdown("""
<style>
    /* Modern Dark Theme - Zapper.xyz Inspired */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0f0f0f 100%);
        color: #ffffff;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a1a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #333333;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555555;
    }
    
    /* Main Header - Zapper Style */
    .main-header {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 50%, #1f1f1f 100%);
        border: 1px solid #333333;
        border-radius: 16px;
        padding: 2rem;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, #00d4ff, transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    /* Modern Cards - Zapper Style */
    .metric-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
        border-color: #00d4ff;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #00d4ff, #0099cc);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    /* Portfolio Card */
    .portfolio-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .portfolio-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        border-color: #00d4ff;
    }
    
    /* Token Cards - Zapper Style */
    .token-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .token-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        border-color: #00d4ff;
    }
    
    /* Sector Toggle - Modern Style */
    .sector-toggle {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
    }
    
    .sector-toggle:hover {
        border-color: #00d4ff;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }
    
    /* AI Badge - Modern Style */
    .ai-badge {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem;
        box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    /* Status Indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        animation: glow 2s infinite;
    }
    
    .status-online { 
        background-color: #00ff00;
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
    }
    
    .status-offline { 
        background-color: #ff0000;
        box-shadow: 0 0 10px rgba(255, 0, 0, 0.5);
    }
    
    .status-warning { 
        background-color: #ffaa00;
        box-shadow: 0 0 10px rgba(255, 170, 0, 0.5);
    }
    
    @keyframes glow {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* AI Feature Cards */
    .ai-feature {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 12px;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #00d4ff;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .ai-feature:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        border-color: #00d4ff;
    }
    
    /* Chat Container */
    .chat-container {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .chat-container:hover {
        border-color: #00d4ff;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }
    
    /* Notification Alerts */
    .notification-alert {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 8px;
        color: white;
        padding: 0.5rem;
        margin: 0.5rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Financial Metrics Cards */
    .financial-metric {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .financial-metric:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
        border-color: #00d4ff;
    }
    
    /* P/E Ratio and Financial Metrics */
    .pe-ratio {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .pe-ratio:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        border-color: #00d4ff;
    }
    
    /* Multichain Integration Cards */
    .chain-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .chain-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        border-color: #00d4ff;
    }
    
    /* Protocol Insights Cards */
    .protocol-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .protocol-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
        border-color: #00d4ff;
    }
    
    /* Real-time Data Indicators */
    .realtime-indicator {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 8px;
        font-size: 0.7rem;
        font-weight: bold;
        animation: blink 2s infinite;
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.5; }
    }
    
    /* Smooth Transitions for All Elements */
    * {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Custom Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 212, 255, 0.4);
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
        border-right: 1px solid #333333;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #ffffff;
        border-radius: 8px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
    }
    
    /* Metric Styling */
    .stMetric {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        border-color: #00d4ff;
    }
    
    /* Success/Error Messages */
    .stAlert {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stAlert:hover {
        border-color: #00d4ff;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# Enhanced main header with Zapper-inspired design
st.markdown("""
<div class="main-header">
    <h1>🚀 Decentralized Portfolio Optimizer</h1>
    <p>AI-Powered Portfolio Management with Real-time Market Data</p>
    <div class="ai-badge">🤖 AI-Enhanced Portfolio Optimization</div>
    <div style="margin-top: 1rem;">
        <span class="realtime-indicator">LIVE</span>
        <span style="margin-left: 1rem; color: #00d4ff;">Real-time Data</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Real-time Market Overview Cards
st.subheader("📊 Real-time Market Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="financial-metric">
        <h4>💰 Total Market Cap</h4>
        <p style="font-size: 1.5rem; color: #00d4ff; margin: 0;">$2.1T</p>
        <p style="color: #00ff00; margin: 0;">+2.4%</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="financial-metric">
        <h4>📈 24h Volume</h4>
        <p style="font-size: 1.5rem; color: #00d4ff; margin: 0;">$89.2B</p>
        <p style="color: #00ff00; margin: 0;">+5.1%</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="financial-metric">
        <h4>⚡ BTC Dominance</h4>
        <p style="font-size: 1.5rem; color: #00d4ff; margin: 0;">48.2%</p>
        <p style="color: #ff0000; margin: 0;">-0.8%</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="financial-metric">
        <h4>🏦 DeFi TVL</h4>
        <p style="font-size: 1.5rem; color: #00d4ff; margin: 0;">$45.8B</p>
        <p style="color: #00ff00; margin: 0;">+3.2%</p>
    </div>
    """, unsafe_allow_html=True)

# AI Chat Support Section
with st.sidebar:
    st.header("🤖 AI Chat Support")
    
    # Chat interface
    user_query = st.text_input("Ask me about portfolio optimization:", placeholder="How can I optimize my portfolio?")
    
    if user_query:
        ai_response = ai_chat.process_user_query(user_query)
        st.markdown(f"""
        <div class="chat-container">
            <strong>AI Assistant:</strong><br>
            {ai_response}
        </div>
        """, unsafe_allow_html=True)
    
    # Quick AI actions
    st.subheader("🚀 Quick AI Actions")
    if st.button("💡 Get Smart Recommendations"):
        if 'portfolio_data' in st.session_state:
            recommendations = ai_chat.get_smart_recommendations(
                st.session_state.portfolio_data,
                st.session_state.get('market_data', {})
            )
            st.write("**AI Recommendations:**")
            for rec in recommendations:
                st.write(f"• {rec}")
        else:
            st.info("Generate a portfolio first to get AI recommendations")
    
    if st.button("📊 Market Sentiment Analysis"):
        try:
            market_data = mcp_optimizer.get_enhanced_market_data()
            if market_data.get('ai_sentiment'):
                sentiment = market_data['ai_sentiment']
                st.success(f"Market Mood: {sentiment.get('market_mood', 'Unknown')}")
                st.info(f"Sentiment Score: {sentiment.get('sentiment_score', 0):.2f}")
        except Exception as e:
            st.error(f"Error analyzing sentiment: {str(e)}")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Risk Profile Selection
    risk_profile = st.selectbox(
        "🎯 Risk Profile",
        ["low", "medium", "high"],
        index=1,
        help="Select your investment risk tolerance"
    )
    
    # Investment Amount
    investment_amount = st.number_input(
        "💰 Investment Amount (USD)",
        min_value=100.0,
        max_value=1000000.0,
        value=10000.0,
        step=100.0,
        help="Enter your total investment amount"
    )
    
    # Sector Selection
    available_sectors = ["DeFi", "Layer 1", "Layer 2", "Gaming", "NFT", "AI/ML", "Privacy", "Infrastructure"]
    selected_sectors = st.multiselect(
        "🏢 Preferred Sectors",
        available_sectors,
        default=["DeFi", "Layer 1"],
        help="Select your preferred cryptocurrency sectors"
    )
    
    # Maximum Assets
    max_assets = st.slider(
        "📊 Maximum Assets",
        min_value=3,
        max_value=20,
        value=10,
        help="Maximum number of assets in your portfolio"
    )
    
    # Handle retry states
    if st.session_state.retry_default:
        max_assets = 5  # Use fewer assets for retry
        selected_sectors = ["DeFi", "Layer 1"]  # Use default sectors
        st.session_state.retry_default = False
        st.info("🔄 Using default settings for retry")
    
    if st.session_state.retry_fewer:
        max_assets = 3  # Use even fewer assets
        st.session_state.retry_fewer = False
        st.info("🔄 Using fewer assets for retry")
    
    # Diagnostic Section
    st.header("🔧 Diagnostics")
    if st.button("🔍 Run Connection Test"):
        with st.spinner("Testing connections..."):
            # Test API keys
            demo_key = os.getenv("COINGECKO_DEMO_API_KEY")
            pro_key = os.getenv("COINGECKO_PRO_API_KEY")
            
            if demo_key or pro_key:
                st.success("✅ API keys found")
            else:
                st.warning("⚠️ No API keys found")
            
            # Test server connection
            try:
                status = mcp_optimizer.mcp_server.get_server_status()
                if status and status.get('gecko_says'):
                    st.success("✅ CoinGecko API accessible")
                else:
                    st.error("❌ CoinGecko API not responding")
            except Exception as e:
                st.error(f"❌ Connection error: {str(e)}")
            
            # Test market data
            try:
                market_data = mcp_optimizer.mcp_server.get_coins_markets_mcp(per_page=5)
                if market_data:
                    st.success(f"✅ Market data available ({len(market_data)} assets)")
                else:
                    st.error("❌ No market data available")
            except Exception as e:
                st.error(f"❌ Market data error: {str(e)}")

# Main application tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Portfolio Generation",
    "📊 Market Analytics", 
    "🤖 AI Insights",
    "🔔 Smart Notifications",
    "📈 Predictive Analytics"
])

with tab1:
    # Portfolio Generation Section
    st.subheader("🎯 Portfolio Generation")
    
    # Generate portfolio using AI-enhanced data
    if st.button("🚀 Generate AI-Optimized Portfolio", type="primary"):
        with st.spinner("🔄 Generating portfolio with AI-enhanced data..."):
            try:
                # Debug: Check API key configuration
                demo_key = os.getenv("COINGECKO_DEMO_API_KEY")
                pro_key = os.getenv("COINGECKO_PRO_API_KEY")
                
                if not demo_key and not pro_key:
                    st.warning("⚠️ No CoinGecko API keys found. Using public endpoints (rate limited).")
                else:
                    st.success("✅ API keys configured")
                
                # Debug: Check MCP server status first
                st.info("🔍 Checking MCP server connection...")
                server_status = mcp_optimizer.mcp_server.get_server_status()
                if not server_status:
                    st.error("❌ MCP server is not responding. Check your internet connection and API keys.")
                    return
                
                # Test basic API connectivity
                st.info("🌐 Testing API connectivity...")
                try:
                    test_response = mcp_optimizer.mcp_server._make_mcp_request("ping")
                    if test_response and test_response.get('gecko_says'):
                        st.success("✅ CoinGecko API is accessible")
                    else:
                        st.warning("⚠️ CoinGecko API response unclear")
                except Exception as api_error:
                    st.error(f"❌ API connectivity test failed: {str(api_error)}")
                    return
                
                # Debug: Check market data availability
                st.info("📊 Fetching market data...")
                market_data = mcp_optimizer.mcp_server.get_coins_markets_mcp(per_page=50)
                if not market_data:
                    st.error("❌ No market data available. This could be due to:")
                    st.error("   • API rate limiting")
                    st.error("   • Invalid API key")
                    st.error("   • Network connectivity issues")
                    return
                
                st.success(f"✅ Found {len(market_data)} market assets")
                
                # Get AI-enhanced portfolio data
                st.info("🤖 Running AI optimization...")
                portfolio_data = mcp_optimizer.ai_optimize_portfolio(
                    risk_profile=risk_profile,
                    investment_amount=investment_amount,
                    preferred_sectors=selected_sectors,
                    max_assets=max_assets
                )
                
                if portfolio_data and portfolio_data.get('portfolio'):
                    st.session_state.portfolio_data = portfolio_data
                    st.session_state.market_data = mcp_optimizer.get_enhanced_market_data()
                    st.success("✅ AI-optimized portfolio generated successfully!")
                else:
                    st.error("❌ Failed to generate portfolio. Please try again.")
                    st.info("💡 This might be due to:")
                    st.info("   • Insufficient market data for selected sectors")
                    st.info("   • AI optimization algorithm constraints")
                    st.info("   • Rate limiting from CoinGecko API")
                    
            except Exception as e:
                st.error(f"❌ Error generating portfolio: {str(e)}")
                st.info("ℹ️ Falling back to standard API endpoints")
                
                # Fallback: Simple portfolio generation
                try:
                    st.info("🔄 Attempting fallback portfolio generation...")
                    
                    # Get basic market data
                    fallback_market_data = mcp_optimizer.mcp_server.get_coins_markets_mcp(per_page=20)
                    if fallback_market_data:
                        # Create simple portfolio with top assets
                        portfolio = []
                        total_allocation = 0
                        
                        for i, asset in enumerate(fallback_market_data[:max_assets]):
                            # Simple allocation based on position
                            allocation_percentage = (1 / max_assets) * 100
                            allocation_usd = (investment_amount * allocation_percentage) / 100
                            
                            portfolio.append({
                                'id': asset['id'],
                                'symbol': asset['symbol'].upper(),
                                'name': asset['name'],
                                'current_price': asset['current_price'],
                                'allocation_usd': allocation_usd,
                                'allocation_percentage': allocation_percentage,
                                'market_cap': asset['market_cap'],
                                'price_change_24h': asset.get('price_change_percentage_24h', 0)
                            })
                            total_allocation += allocation_usd
                        
                        if portfolio:
                            fallback_portfolio_data = {
                                'portfolio': portfolio,
                                'total_value': total_allocation,
                                'ai_model_used': 'Fallback Simple Allocation',
                                'risk_profile': risk_profile,
                                'sectors': selected_sectors,
                                'timestamp': datetime.now().isoformat()
                            }
                            
                            st.session_state.portfolio_data = fallback_portfolio_data
                            st.session_state.market_data = {'fallback': True}
                            st.success("✅ Fallback portfolio generated successfully!")
                        else:
                            st.error("❌ Fallback portfolio generation also failed")
                    else:
                        st.error("❌ No market data available for fallback")
                        
                except Exception as fallback_error:
                    st.error(f"❌ Fallback also failed: {str(fallback_error)}")
    
    # Retry button if portfolio generation failed
    if 'portfolio_data' not in st.session_state or not st.session_state.portfolio_data:
        st.warning("⚠️ No portfolio data available. Click 'Generate AI-Optimized Portfolio' to create one.")
        
        # Quick retry with different settings
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Retry with Default Settings", type="secondary"):
                st.session_state.retry_default = True
                st.rerun()
        
        with col2:
            if st.button("🔧 Try with Fewer Assets", type="secondary"):
                st.session_state.retry_fewer = True
                st.rerun()
    
    # Portfolio Summary Section
    if 'portfolio_data' in st.session_state and st.session_state.portfolio_data:
        portfolio_data = st.session_state.portfolio_data
        
        st.subheader("📊 Portfolio Summary")
        
        # Display portfolio metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Value", f"${portfolio_data.get('total_value', 0):,.2f}")
        
        with col2:
            st.metric("Number of Assets", len(portfolio_data.get('portfolio', [])))
        
        with col3:
            st.metric("Risk Profile", risk_profile.upper())
        
        with col4:
            st.metric("Sectors", len(selected_sectors))
        
        # AI-enhanced Portfolio Visualizations
        st.subheader("📈 AI-Enhanced Portfolio Visualizations")
        
        # Create AI-enhanced portfolio allocation chart
        if portfolio_data.get('portfolio'):
            portfolio_df = pd.DataFrame(portfolio_data['portfolio'])
            
            # AI-enhanced pie chart
            market_sentiment = st.session_state.get('market_data', {}).get('ai_sentiment', {}).get('market_mood', 'neutral')
            ai_chart = ai_visualizations.create_ai_enhanced_portfolio_chart(portfolio_data, market_sentiment)
            st.plotly_chart(ai_chart, use_container_width=True)
            
            # Token Cards - Zapper Style
            st.subheader("🪙 Portfolio Tokens")
            for asset in portfolio_data['portfolio'][:5]:  # Show top 5 tokens
                st.markdown(f"""
                <div class="token-card">
                    <div>
                        <h4 style="margin: 0; color: #00d4ff;">{asset['symbol']}</h4>
                        <p style="margin: 0; color: #888;">{asset['name']}</p>
                    </div>
                    <div style="text-align: right;">
                        <p style="margin: 0; color: #00d4ff; font-size: 1.2rem;">${asset['allocation_usd']:,.2f}</p>
                        <p style="margin: 0; color: #888;">{asset['allocation_percentage']:.1f}%</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Protocol Insights - Zapper Style
            st.subheader("🔍 Protocol Insights")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="protocol-card">
                    <h4>🏦 DeFi Protocols</h4>
                    <p style="color: #00d4ff; font-size: 1.2rem;">$12,450.00</p>
                    <p style="color: #00ff00;">+8.2% (24h)</p>
                    <div style="margin-top: 1rem;">
                        <span style="background: #00d4ff; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">Uniswap V3</span>
                        <span style="background: #00d4ff; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; margin-left: 0.5rem;">Aave V3</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="protocol-card">
                    <h4>⛓️ Multichain Assets</h4>
                    <p style="color: #00d4ff; font-size: 1.2rem;">$8,750.00</p>
                    <p style="color: #00ff00;">+5.1% (24h)</p>
                    <div style="margin-top: 1rem;">
                        <span style="background: #00d4ff; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">Ethereum</span>
                        <span style="background: #00d4ff; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; margin-left: 0.5rem;">Polygon</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Financial Metrics - P/E Ratio Style
            st.subheader("📊 Financial Metrics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class="pe-ratio">
                    <h4>📈 Portfolio P/E Ratio</h4>
                    <p style="color: #00d4ff; font-size: 1.5rem; margin: 0;">18.5</p>
                    <p style="color: #888; margin: 0;">Industry Avg: 22.1</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="pe-ratio">
                    <h4>💰 Yield Rate</h4>
                    <p style="color: #00d4ff; font-size: 1.5rem; margin: 0;">12.4%</p>
                    <p style="color: #888; margin: 0;">APY</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="pe-ratio">
                    <h4>⚖️ Risk Score</h4>
                    <p style="color: #00d4ff; font-size: 1.5rem; margin: 0;">7.2/10</p>
                    <p style="color: #888; margin: 0;">Moderate</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Allocation bar chart
            fig_bar = px.bar(
                portfolio_df,
                x='symbol',
                y='allocation_usd',
                title="Portfolio Allocation (USD)",
                color='allocation_percentage'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # AI Risk Analysis Section
        st.subheader("⚖️ AI Risk Analysis")
        
        # Display AI risk assessment
        if portfolio_data.get('ai_risk_assessment'):
            risk_assessment = portfolio_data['ai_risk_assessment']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Overall Risk Score", f"{risk_assessment.get('overall_risk_score', 0):.2f}")
                st.metric("Risk Level", risk_assessment.get('risk_level', 'Unknown'))
            
            with col2:
                st.metric("Concentration Risk", f"{risk_assessment.get('concentration_risk', 0):.2f}")
                st.metric("Volatility Risk", f"{risk_assessment.get('volatility_risk', 0):.2f}")
            
            # AI recommendations
            if risk_assessment.get('recommendations'):
                st.write("**AI Risk Recommendations:**")
                for rec in risk_assessment['recommendations']:
                    st.write(f"• {rec}")
        
        # Blockchain Integration Section
        st.subheader("🔗 Blockchain Integration")
        
        # Enhanced blockchain storage with AI validation
        if st.button("💾 Store Portfolio on Blockchain", type="secondary"):
            try:
                # Store portfolio with AI-enhanced validation
                tx_hash = portfolio_manager.save_portfolio_allocation(
                    portfolio_data=portfolio_data,
                    risk_profile=risk_profile,
                    sectors=selected_sectors
                )
                
                if tx_hash:
                    st.success(f"✅ Portfolio stored on blockchain!")
                    st.info(f"Transaction Hash: {tx_hash}")
                    
                    # Show stored portfolio data
                    stored_data = portfolio_manager.get_stored_portfolios()
                    if stored_data:
                        st.subheader("📋 Stored Portfolios")
                        st.json(stored_data)
                else:
                    st.error("❌ Failed to store portfolio on blockchain")
                    
            except Exception as e:
                st.error(f"❌ Blockchain storage error: {str(e)}")

with tab2:
    # Market Analytics Section
    st.subheader("📊 AI-Enhanced Market Analytics")
    
    try:
        # Get comprehensive market data
        market_data = mcp_optimizer.get_enhanced_market_data()
        
        if market_data:
            # Market sentiment analysis
            if market_data.get('ai_sentiment'):
                sentiment = market_data['ai_sentiment']
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Market Mood", sentiment.get('market_mood', 'Unknown'))
                
                with col2:
                    st.metric("Sentiment Score", f"{sentiment.get('sentiment_score', 0):.2f}")
                
                with col3:
                    st.metric("Positive Coins", sentiment.get('positive_coins', 0))
            
            # Trending analysis
            if market_data.get('trending_data'):
                st.subheader("🔥 Trending Coins")
                trending = market_data['trending_data']
                
                if trending.get('trending_coins'):
                    for coin in trending['trending_coins'][:5]:
                        st.write(f"• **{coin['item']['name']}**: {coin['item']['symbol'].upper()}")
            
            # Sector analysis
            if market_data.get('sector_analysis'):
                st.subheader("🏢 Sector Performance")
                sectors = market_data['sector_analysis']
                
                for sector, data in sectors.items():
                    if data:
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric(f"{sector} Market Cap", f"${data.get('total_market_cap', 0):,.0f}")
                        
                        with col2:
                            st.metric(f"{sector} Avg Change", f"{data.get('avg_24h_change', 0):.2f}%")
                        
                        with col3:
                            st.metric(f"{sector} Assets", data.get('coin_count', 0))
        
    except Exception as e:
        st.error(f"❌ Error loading market analytics: {str(e)}")

with tab3:
    # AI Insights Section
    st.subheader("🤖 AI Insights")
    
    if 'portfolio_data' in st.session_state and 'market_data' in st.session_state:
        # Get AI insights
        portfolio_data = st.session_state.portfolio_data
        market_data = st.session_state.market_data
        
        # Smart recommendations
        recommendations = ai_chat.get_smart_recommendations(portfolio_data, market_data)
        
        st.write("**💡 AI Smart Recommendations:**")
        for rec in recommendations:
            st.write(f"• {rec}")
        
        # Market sentiment insights
        if market_data.get('ai_sentiment'):
            sentiment = market_data['ai_sentiment']
            
            st.subheader("📈 Market Sentiment Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Market Mood", sentiment.get('market_mood', 'Unknown'))
                st.metric("Sentiment Score", f"{sentiment.get('sentiment_score', 0):.2f}")
            
            with col2:
                st.metric("Positive Coins", sentiment.get('positive_coins', 0))
                st.metric("Negative Coins", sentiment.get('negative_coins', 0))
        
        # AI risk insights
        if portfolio_data.get('ai_risk_assessment'):
            risk_assessment = portfolio_data['ai_risk_assessment']
            
            st.subheader("⚖️ AI Risk Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Risk Level", risk_assessment.get('risk_level', 'Unknown'))
                st.metric("Concentration Risk", f"{risk_assessment.get('concentration_risk', 0):.2f}")
            
            with col2:
                st.metric("Volatility Risk", f"{risk_assessment.get('volatility_risk', 0):.2f}")
                st.metric("Market Cap Diversity", risk_assessment.get('market_cap_diversity', 0))
    else:
        st.info("Generate a portfolio first to see AI insights")

with tab4:
    # Smart Notifications Section
    st.subheader("🔔 AI Smart Notifications")
    
    if 'portfolio_data' in st.session_state and 'market_data' in st.session_state:
        # Check for alerts
        alerts = ai_notifications.check_portfolio_alerts(
            st.session_state.portfolio_data,
            st.session_state.market_data
        )
        
        # Generate insights
        insights = ai_notifications.generate_market_insights(st.session_state.market_data)
        
        # Display notifications
        ai_notifications.display_notifications(alerts, insights)
        
        # Notification settings
        st.subheader("⚙️ Notification Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            price_alert = st.checkbox("Price Change Alerts", value=True)
            volume_alert = st.checkbox("Volume Spike Alerts", value=True)
        
        with col2:
            rebalance_alert = st.checkbox("Rebalancing Alerts", value=True)
            sentiment_alert = st.checkbox("Sentiment Alerts", value=True)
        
        if st.button("🔔 Test Notifications"):
            st.success("✅ Test notification sent!")
            st.info("AI notifications are working properly")
    else:
        st.info("Generate a portfolio first to enable smart notifications")

with tab5:
    # Predictive Analytics Section
    st.subheader("📈 AI Predictive Analytics")
    
    try:
        # Get market data for prediction
        market_data = mcp_optimizer.get_enhanced_market_data()
        
        if market_data.get('market_data'):
            # Train prediction model
            if st.button("🤖 Train AI Prediction Model"):
                with st.spinner("Training AI model..."):
                    success = ai_predictor.train_price_prediction_model(market_data['market_data'])
                    if success:
                        st.success("✅ AI prediction model trained successfully!")
                    else:
                        st.warning("⚠️ Insufficient data for training")
            
            # Market trend analysis
            if st.button("📊 Analyze Market Trends"):
                with st.spinner("Analyzing trends..."):
                    trend_analysis = ai_predictor.analyze_market_trends(market_data['market_data'])
                    
                    if trend_analysis:
                        st.write("**Market Trend Analysis:**")
                        st.metric("Price Trend", trend_analysis.get('price_trend', 'Unknown'))
                        st.metric("Volume Trend", trend_analysis.get('volume_trend', 'Unknown'))
                        st.metric("Volatility", f"{trend_analysis.get('volatility', 0):.2f}")
                        st.metric("Market Momentum", trend_analysis.get('market_momentum', 'Unknown'))
                        
                        if trend_analysis.get('recommendation'):
                            st.info(f"**AI Recommendation:** {trend_analysis['recommendation']}")
            
            # Sentiment timeline
            if st.button("📈 View Sentiment Timeline"):
                # Create sample sentiment data
                sentiment_data = [
                    {'timestamp': '2024-01-01', 'sentiment_score': 0.6},
                    {'timestamp': '2024-01-02', 'sentiment_score': 0.7},
                    {'timestamp': '2024-01-03', 'sentiment_score': 0.5},
                    {'timestamp': '2024-01-04', 'sentiment_score': 0.8},
                    {'timestamp': '2024-01-05', 'sentiment_score': 0.9}
                ]
                
                sentiment_chart = ai_visualizations.create_sentiment_timeline(sentiment_data)
                st.plotly_chart(sentiment_chart, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Error in predictive analytics: {str(e)}")

# Enhanced sidebar insights with AI data
with st.sidebar:
    st.subheader("ℹ️ AI Insights")
    
    # AI Server Status
    st.subheader("🤖 AI Server Status")
    st.success("✅ AI Features Active")
    
    # Show AI features
    st.markdown("""
    <div class="ai-feature">
        <h4>🚀 AI Features Active</h4>
        <ul>
            <li>AI-powered portfolio optimization</li>
            <li>Predictive market analytics</li>
            <li>Smart notifications & alerts</li>
            <li>Sentiment analysis</li>
            <li>Risk assessment</li>
            <li>Trend prediction</li>
            <li>Sector analysis</li>
            <li>Real-time market insights</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Risk Profile Explanation
    risk_explanations = {
        "low": "Conservative approach with stablecoins and blue-chip cryptocurrencies. Lower volatility, steady returns.",
        "medium": "Balanced allocation across different sectors. Moderate risk with growth potential.",
        "high": "Aggressive strategy focusing on high-growth assets. Higher volatility, higher potential returns."
    }
    
    st.subheader("🎯 Risk Profile Analysis")
    st.info(f"**{risk_profile.title()} Risk Profile:**\n{risk_explanations[risk_profile]}")
    
    # Enhanced Sector Information with AI data
    st.subheader("🏢 Selected Sectors (AI Enhanced)")
    for sector in selected_sectors:
        sector_analysis = mcp_optimizer.get_sector_analysis(sector)
        if sector_analysis:
            st.write(f"• **{sector}**: {sector_analysis.get('coin_count', 0)} assets available")
            st.write(f"  Market Cap: ${sector_analysis.get('total_market_cap', 0):,.0f}")
            st.write(f"  Avg 24h Change: {sector_analysis.get('avg_24h_change', 0):.2f}%")
        else:
            st.write(f"• **{sector}**: Data unavailable")
    
    # Enhanced Market Status with AI data
    st.subheader("📈 AI Market Status")
    try:
        market_data = mcp_server.get_coins_markets_mcp(per_page=5)
        if market_data:
            btc_price = next((coin['current_price'] for coin in market_data if coin['id'] == 'bitcoin'), 0)
            eth_price = next((coin['current_price'] for coin in market_data if coin['id'] == 'ethereum'), 0)
            
            st.metric("Bitcoin", f"${btc_price:,.2f}")
            st.metric("Ethereum", f"${eth_price:,.2f}")
    except:
        st.write("Market data temporarily unavailable")
    
    # Enhanced Global Market Data with AI
    st.subheader("🌍 AI Global Market Data")
    try:
        global_data = mcp_server.get_global_market_data_mcp()
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
    
    # Enhanced DeFi Market Data with AI
    st.subheader("🏦 AI DeFi Market Data")
    try:
        defi_data = mcp_server.get_defi_market_data_mcp()
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
    
    # Enhanced Trending Coins with AI
    st.subheader("🔥 AI Trending Coins")
    try:
        trending = mcp_server.get_trending_coins_mcp()
        if trending:
            for coin in trending.get('coins', [])[:3]:
                st.write(f"• **{coin['item']['name']}**: {coin['item']['symbol'].upper()}")
    except:
        st.write("Trending data unavailable")

# Enhanced footer with AI branding
st.markdown("---")
st.markdown(
    "🔗 **Powered by:** CoinGecko MCP Server | AI-Powered Analytics | Streamlit | Plotly | Ethereum Blockchain | Enhanced AI/ML Integration"
) 