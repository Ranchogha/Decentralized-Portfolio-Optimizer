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
    
    /* Token Cards - Zapper Style */
    .token-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .token-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        border-color: #00d4ff;
    }
    
    /* Protocol Cards - Zapper Style */
    .protocol-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .protocol-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        border-color: #00d4ff;
    }
    
    /* AI Badge */
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
    .metric-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        border-color: #00d4ff;
    }
    
    /* Risk Analysis Cards */
    .risk-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .risk-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        border-color: #00d4ff;
    }
    
    /* Portfolio Summary Cards */
    .portfolio-summary {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .portfolio-summary:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        border-color: #00d4ff;
    }
    
    /* Blockchain Integration Cards */
    .blockchain-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .blockchain-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        border-color: #00d4ff;
    }
    
    /* Enhanced Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 212, 255, 0.3);
    }
    
    /* Enhanced Selectboxes */
    .stSelectbox > div > div > div {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 8px;
        color: white;
    }
    
    /* Enhanced Number Inputs */
    .stNumberInput > div > div > input {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 8px;
        color: white;
    }
    
    /* Enhanced Text Inputs */
    .stTextInput > div > div > input {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 8px;
        color: white;
    }
    
    /* Enhanced Sliders */
    .stSlider > div > div > div > div {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
    }
    
    /* Enhanced Checkboxes */
    .stCheckbox > div > div > div {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 8px;
    }
    
    /* Enhanced Multiselect */
    .stMultiSelect > div > div > div {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 8px;
        color: white;
    }
    
    /* Enhanced Tabs */
    .stTabs > div > div > div > div {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 8px;
        color: white;
    }
    
    /* Enhanced Sidebar */
    .css-1d391kg {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0f0f0f 100%);
    }
    
    /* Enhanced Metrics */
    .css-1wivap2 {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem;
    }
    
    /* Enhanced Success Messages */
    .stSuccess {
        background: linear-gradient(135deg, #00ff00 0%, #00cc00 100%);
        border: 1px solid #00ff00;
        border-radius: 8px;
        color: white;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Enhanced Error Messages */
    .stError {
        background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%);
        border: 1px solid #ff0000;
        border-radius: 8px;
        color: white;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Enhanced Warning Messages */
    .stWarning {
        background: linear-gradient(135deg, #ffaa00 0%, #cc8800 100%);
        border: 1px solid #ffaa00;
        border-radius: 8px;
        color: white;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Enhanced Info Messages */
    .stInfo {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
        border: 1px solid #00d4ff;
        border-radius: 8px;
        color: white;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown("""
<div class="main-header">
    <h1>🚀 Decentralized Portfolio Optimizer</h1>
    <p>AI-Powered Crypto Portfolio Management with Blockchain Integration</p>
    <div style="margin-top: 1rem;">
        <span class="ai-badge">🤖 AI Enhanced</span>
        <span class="ai-badge">🔗 Blockchain Ready</span>
        <span class="ai-badge">📊 Real-time Data</span>
    </div>
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
            st.subheader("📊 Market Sentiment Analysis")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Overall Mood", sentiment.get('market_mood', 'Unknown'))
                st.metric("Sentiment Score", f"{sentiment.get('sentiment_score', 0):.2f}")
            
            with col2:
                st.metric("Positive Coins", sentiment.get('positive_coins', 0))
                st.metric("Negative Coins", sentiment.get('negative_coins', 0))
        
        # AI predictions
        st.subheader("🔮 AI Predictions")
        predictions = ai_predictor.get_market_predictions(portfolio_data, market_data)
        
        for prediction in predictions:
            st.markdown(f"""
            <div class="ai-feature">
                <h4>🔮 {prediction['title']}</h4>
                <p>{prediction['description']}</p>
                <p><strong>Confidence:</strong> {prediction['confidence']}%</p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        st.info("Generate a portfolio first to see AI insights")

with tab4:
    # Smart Notifications Section
    st.subheader("🔔 Smart Notifications")
    
    # Notification settings
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚙️ Notification Settings")
        email_notifications = st.checkbox("📧 Email Notifications", value=True)
        push_notifications = st.checkbox("📱 Push Notifications", value=True)
        price_alerts = st.checkbox("💰 Price Alerts", value=True)
        portfolio_alerts = st.checkbox("📊 Portfolio Alerts", value=True)
    
    with col2:
        st.subheader("🎯 Alert Thresholds")
        price_change_threshold = st.slider("Price Change %", 1, 20, 5)
        portfolio_change_threshold = st.slider("Portfolio Change %", 1, 15, 3)
    
    # Test notifications
    if st.button("🧪 Test Notifications"):
        try:
            # Test different notification types
            ai_notifications.send_price_alert("BTC", 45000, 5.2)
            ai_notifications.send_portfolio_alert("Portfolio value increased by 3.5%")
            ai_notifications.send_market_alert("Market sentiment is bullish")
            
            st.success("✅ Test notifications sent successfully!")
        except Exception as e:
            st.error(f"❌ Error sending notifications: {str(e)}")
    
    # Notification history
    st.subheader("📋 Notification History")
    notifications = ai_notifications.get_notification_history()
    
    if notifications:
        for notification in notifications[:5]:  # Show last 5 notifications
            st.markdown(f"""
            <div class="notification-alert">
                <strong>{notification['type']}</strong><br>
                {notification['message']}<br>
                <small>{notification['timestamp']}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No notifications yet")

with tab5:
    # Predictive Analytics Section
    st.subheader("📈 Predictive Analytics")
    
    if 'portfolio_data' in st.session_state:
        portfolio_data = st.session_state.portfolio_data
        
        # AI-powered predictions
        st.subheader("🔮 AI Market Predictions")
        
        # Get predictions for portfolio assets
        predictions = ai_predictor.get_portfolio_predictions(portfolio_data)
        
        if predictions:
            for prediction in predictions:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Asset", prediction['asset'])
                
                with col2:
                    st.metric("Predicted Price", f"${prediction['predicted_price']:,.2f}")
                
                with col3:
                    st.metric("Confidence", f"{prediction['confidence']}%")
        
        # Risk analysis
        st.subheader("⚖️ Risk Analysis")
        
        # Calculate risk metrics
        risk_metrics = ai_predictor.calculate_risk_metrics(portfolio_data)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Average Volatility", f"{risk_metrics.get('avg_volatility', 0):.3f}")
        
        with col2:
            st.metric("Portfolio Diversity", f"{risk_metrics.get('diversity', 0)} assets")
        
        with col3:
            st.metric("Largest Position", f"{risk_metrics.get('largest_position', 0):.1f}%")
        
        # Portfolio insights
        st.subheader("ℹ️ Portfolio Insights")
        insights = ai_predictor.get_portfolio_insights(portfolio_data)
        
        for insight in insights:
            st.markdown(f"""
            <div class="ai-feature">
                <h4>💡 {insight['title']}</h4>
                <p>{insight['description']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        st.info("Generate a portfolio first to see predictive analytics")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; padding: 2rem;">
    <p>🚀 Powered by AI & Blockchain Technology</p>
    <p>Built with Streamlit, CoinGecko API, and Ethereum Smart Contracts</p>
</div>
""", unsafe_allow_html=True) 