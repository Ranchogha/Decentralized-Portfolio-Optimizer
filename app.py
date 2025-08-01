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
from ai_features import ai_chat, ai_predictor, ai_visualizations
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
if 'rate_limit_notified' not in st.session_state:
    st.session_state.rate_limit_notified = False

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

# Beautiful Black and White Theme with Gold Accents
st.markdown("""
<style>
    /* Clean Black and White Theme with Gold Accents */
    .stApp {
        background: #ffffff;
        color: #000000;
    }

    /* VISIBILITY FIX: Ensure subheaders and metric labels are black on white background */
    h3, [data-testid="stMetricLabel"] {
        color: #000000 !important;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f5f5f5;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #D4AF37;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #B8860B;
    }
    
    /* Main Header - Elegant Black and Gold */
    .main-header {
        background: #000000;
        border: 2px solid #D4AF37;
        border-radius: 20px;
        padding: 2.5rem;
        color: #ffffff;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(212, 175, 55, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(212,175,55,0.3)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
        opacity: 0.3;
    }
    
    .main-header::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #D4AF37, transparent);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    /* Token Cards - Black with Gold Border */
    .token-card {
        background: #000000;
        border: 1px solid #D4AF37;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        color: #ffffff;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    .token-card:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 20px 40px rgba(212, 175, 55, 0.3);
        border-color: #FFD700;
        background: #111111;
    }
    
    /* Protocol Cards - Black with Gold Accent */
    .protocol-card {
        background: #000000;
        border: 1px solid #D4AF37;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        color: #ffffff;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    .protocol-card:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 20px 40px rgba(212, 175, 55, 0.3);
        border-color: #FFD700;
        background: #111111;
    }
    
    /* AI Badge - Gold */
    .ai-badge {
        background: linear-gradient(135deg, #D4AF37 0%, #FFD700 100%);
        color: #000000;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem;
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);
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
        background: #D4AF37;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.6);
    }
    
    .status-offline { 
        background: #ff4444;
        box-shadow: 0 0 15px rgba(255, 68, 68, 0.6);
    }
    
    .status-warning { 
        background: #ffaa00;
        box-shadow: 0 0 15px rgba(255, 170, 0, 0.6);
    }
    
    @keyframes glow {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* AI Feature Cards - Black with Gold Border */
    .ai-feature {
        background: #000000;
        border: 1px solid #D4AF37;
        border-radius: 16px;
        color: #ffffff;
        padding: 1.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #D4AF37;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    .ai-feature:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 20px 40px rgba(212, 175, 55, 0.3);
        border-color: #FFD700;
        background: #111111;
    }
    
    /* Chat Container - Black with Gold Border */
    .chat-container {
        background: #000000;
        border: 1px solid #D4AF37;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        color: #ffffff;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    .chat-container:hover {
        border-color: #FFD700;
        box-shadow: 0 20px 40px rgba(212, 175, 55, 0.3);
        background: #111111;
    }
    
    /* Notification Alerts - Black with Gold Border */
    .notification-alert {
        background: #000000;
        border: 1px solid #D4AF37;
        border-radius: 12px;
        color: #ffffff;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        animation: slideIn 0.3s ease-out;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Financial Metrics Cards - Khaki with Black Border */
    .metric-card {
        background: #f0e68c;
        border: 2px solid #000000;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.5rem;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        color: #000000;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 0;
        height: 2px;
        background: #D4AF37;
        transition: width 0.4s ease;
    }
    
    .metric-card:hover::after {
        width: 80%;
    }
    
    .metric-card:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 20px 40px rgba(212, 175, 55, 0.3);
        border-color: #D4AF37;
        background: #f5e6a0;
    }
    
    /* Risk Analysis Cards - Black with Gold Border */
    .risk-card {
        background: #000000;
        border: 1px solid #D4AF37;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        color: #ffffff;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    .risk-card:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 20px 40px rgba(212, 175, 55, 0.3);
        border-color: #FFD700;
        background: #111111;
    }
    
    /* Portfolio Summary Cards - Black with Gold Border */
    .portfolio-summary {
        background: #000000;
        border: 1px solid #D4AF37;
        border-radius: 20px;
        padding: 2.5rem;
        margin: 1rem 0;
        color: #ffffff;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    .portfolio-summary:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 20px 40px rgba(212, 175, 55, 0.3);
        border-color: #FFD700;
        background: #111111;
    }
    
    /* Floating Elements Animation */
    .floating-element {
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Gold Button Style */
    .gold-button {
        background: linear-gradient(135deg, #D4AF37 0%, #FFD700 100%);
        color: #000000;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .gold-button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }
    
    .gold-button:hover::before {
        left: 100%;
    }
    
    .gold-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(212, 175, 55, 0.4);
    }
    
    /* Sidebar Styling - White Background */
    .css-1d391kg {
        background: #ffffff;
        border-right: 2px solid #D4AF37;
    }
    
    /* Tab Styling - Black and Gold */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #000000;
        border-radius: 8px;
        padding: 4px;
        border: 1px solid #D4AF37;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #000000;
        border-radius: 6px;
        color: #ffffff;
        border: 1px solid #D4AF37;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: #D4AF37;
        color: #000000;
        border-color: #FFD700;
    }
    
    /* Input Styling - Khaki Background with Black Border */
    .stTextInput > div > div > input {
        background: #f0e68c;
        border: 2px solid #000000;
        border-radius: 8px;
        color: #000000;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #D4AF37;
        box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.2);
    }
    
    /* Selectbox Styling - Khaki Background with Black Border */
    .stSelectbox > div > div {
        background: #f0e68c;
        border: 2px solid #000000;
        border-radius: 8px;
        color: #000000;
    }
    
    /* Placeholder text styling */
    .stTextInput > div > div > input::placeholder {
        color: #000000 !important;
    }
    
    /* Sidebar specific styling */
    .css-1d391kg .stTextInput > div > div > input {
        background: #f0e68c;
        border: 2px solid #000000;
        color: #000000;
    }
    
    .css-1d391kg .stTextInput > div > div > input::placeholder {
        color: #000000 !important;
    }
    
    /* Slider Styling - Gold */
    .stSlider > div > div > div > div {
        background: #D4AF37;
    }
    
    .stSlider > div > div > div > div > div {
        background: #FFD700;
    }
    
    /* Success/Info/Error Messages */
    .stSuccess {
        background: #f0e68c;
        border: 2px solid #000000;
        color: #000000;
    }
    
    .stInfo {
        background: #f0e68c;
        border: 2px solid #000000;
        color: #000000;
    }
    
    .stError {
        background: #f0e68c;
        border: 2px solid #ff4444;
        color: #000000;
    }
    
    /* Dataframe Styling - Khaki Background */
    .dataframe {
        background: #f0e68c;
        border: 2px solid #000000;
        border-radius: 8px;
        color: #000000;
    }
    
    /* Chart Container - Khaki Background */
    .js-plotly-plot {
        background: #f0e68c;
        border-radius: 8px;
        padding: 1rem;
        border: 2px solid #000000;
    }
    
    /* Enhanced Button Styling for Primary Buttons - Gold */
    .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #D4AF37 0%, #FFD700 100%);
        color: #000000;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button[data-testid="baseButton-primary"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button[data-testid="baseButton-primary"]:hover::before {
        left: 100%;
    }
    
    .stButton > button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(212, 175, 55, 0.4);
    }
    
    /* Enhanced Button Styling for Secondary Buttons - Black */
    .stButton > button[data-testid="baseButton-secondary"] {
        background: #000000;
        color: #ffffff;
        border: 2px solid #D4AF37;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button[data-testid="baseButton-secondary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(212, 175, 55, 0.3);
        border-color: #FFD700;
        background: #111111;
    }
    
    /* Floating Animation for Cards */
    .floating-element {
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Gold Shimmer Effect */
    .gold-shimmer {
        position: relative;
        overflow: hidden;
    }
    
    .gold-shimmer::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(212,175,55,0.5), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    /* Notification settings and other sections styling */
    .stCheckbox > div > div {
        background: #f0e68c;
        border: 2px solid #000000;
        color: #000000;
    }
    
    .stCheckbox > div > div > label {
        color: #000000 !important;
    }
    
    /* Ensure all text in main content area is black by default */
    .main .block-container {
        color: #000000;
    }

    /* CUSTOM STYLE FOR SIDEBAR SUBHEADER */
    .sidebar-subheader {
        color: #ffffff !important;
    }

    /* CUSTOM STYLES FOR INSIGHTS AND PREDICTIONS */
    .recommendation-card, .prediction-card, .trending-coin-card {
        background: #000000;
        border: 1px solid #D4AF37;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        color: #ffffff;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .recommendation-card:hover, .prediction-card:hover, .trending-coin-card:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 20px 40px rgba(212, 175, 55, 0.3);
        border-color: #FFD700;
        background: #111111;
    }

    .recommendation-card p, .prediction-card p, .trending-coin-card p {
        color: #ffffff;
    }
    
    .metric-value-black {
        color: #000000 !important;
    }
    
    .metric-label-black {
        color: #000000 !important;
    }
    
</style>
""", unsafe_allow_html=True)

# Main Header with Floating Elements
st.markdown("""
<div class="main-header gold-shimmer">
    <h1 style="color: #ffffff;">🚀 Decentralized Portfolio Optimizer</h1>
    <p style="color: #ffffff;">AI-Powered Crypto Portfolio Management with Blockchain Integration</p>
    <div style="margin-top: 1rem;">
        <span class="ai-badge floating-element">🤖 AI Enhanced</span>
        <span class="ai-badge floating-element" style="animation-delay: 0.5s;">🔗 Blockchain Ready</span>
        <span class="ai-badge floating-element" style="animation-delay: 1s;">📊 Real-time Data</span>
    </div>
    <div style="position: absolute; top: 20px; right: 20px; opacity: 0.1;">
        <div class="floating-element" style="width: 20px; height: 20px; background: #D4AF37; border-radius: 50%; margin: 5px;"></div>
        <div class="floating-element" style="width: 15px; height: 15px; background: #FFD700; border-radius: 50%; margin: 5px; animation-delay: 0.3s;"></div>
        <div class="floating-element" style="width: 25px; height: 25px; background: #B8860B; border-radius: 50%; margin: 5px; animation-delay: 0.7s;"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# SEARCH Section
with st.sidebar:
    st.header("🔍 SEARCH")
    
    # Search interface
    user_query = st.text_input("Ask me about portfolio optimization:", placeholder="How can I optimize my portfolio?")
    
    if user_query:
        ai_response = ai_chat.process_user_query(user_query)
        st.markdown(f"""
        <div class="chat-container">
            <strong>AI Assistant:</strong><br>
            {ai_response}
        </div>
        """, unsafe_allow_html=True)
    
    # Quick AI actions with metallic button styling
    st.markdown('<h3 class="sidebar-subheader">🚀 Quick AI Actions</h3>', unsafe_allow_html=True)
    if st.button("💡 Get Smart Recommendations", key="smart_rec_btn"):
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
    
    if st.button("📊 Market Sentiment Analysis", key="sentiment_btn"):
        try:
            market_data = mcp_optimizer.get_enhanced_market_data()
            if market_data.get('ai_sentiment'):
                sentiment = market_data['ai_sentiment']
                st.success(f"Market Mood: {sentiment.get('market_mood', 'Unknown')}")
                st.info(f"Sentiment Score: {sentiment.get('sentiment_score', 0):.2f}")
        except Exception as e:
            st.error("Error analyzing sentiment")

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
    
    if st.session_state.retry_fewer:
        max_assets = 3  # Use even fewer assets
        st.session_state.retry_fewer = False
    
    # Diagnostic Section
    st.header("🔧 Diagnostics")
    if st.button("🔍 Run Connection Test"):
        with st.spinner("Testing connections..."):
            # Test API keys
            demo_key = os.getenv("COINGECKO_DEMO_API_KEY")
            pro_key = os.getenv("COINGECKO_PRO_API_KEY")
            
            # Test server connection
            try:
                status = mcp_optimizer.mcp_server.get_server_status()
                if status and status.get('gecko_says'):
                    st.success("✅ Connection successful")
                else:
                    st.error("❌ Connection failed")
            except Exception as e:
                st.error("❌ Connection failed")
            
            # Test market data
            try:
                market_data = mcp_optimizer.mcp_server.get_coins_markets_mcp(per_page=5)
                if market_data:
                    st.success("✅ Data available")
                else:
                    st.error("❌ No data available")
            except Exception as e:
                st.error("❌ Data error")

# Main application tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Portfolio Generation",
    "📊 Market Analytics", 
    "🤖 AI Insights",
    "📈 Predictive Analytics"
])

with tab1:
    # Portfolio Generation Section
    st.subheader("🎯 Portfolio Generation")
    
    # Generate portfolio using AI-enhanced data with metallic styling
    if st.button("🚀 Generate AI-Optimized Portfolio", type="primary", key="generate_portfolio_btn"):
        with st.spinner("🔄 Generating portfolio with AI-enhanced data..."):
            try:
                # Get AI-enhanced portfolio data
                portfolio_data = mcp_optimizer.ai_optimize_portfolio(
                    risk_profile=risk_profile,
                    investment_amount=investment_amount,
                    preferred_sectors=selected_sectors,
                    max_assets=max_assets
                )
                
                if portfolio_data and portfolio_data.get('portfolio'):
                    st.session_state.portfolio_data = portfolio_data
                    st.session_state.market_data = mcp_optimizer.get_enhanced_market_data()
                else:
                    st.error("❌ Failed to generate portfolio. Please try again.")
                    
            except Exception as e:
                st.error("❌ Error generating portfolio")
                st.stop()
    
    # Retry button if portfolio generation failed
    if 'portfolio_data' not in st.session_state or not st.session_state.portfolio_data:
        st.markdown("""
        <div style="background: #f0e68c; border: 2px solid #000000; border-radius: 8px; padding: 1rem; color: #000000;">
            ⚠️ No portfolio data available. Click 'Generate AI-Optimized Portfolio' to create one.
        </div>
        """, unsafe_allow_html=True)
        
        # Quick retry with different settings
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Retry with Default Settings", type="secondary", key="retry_default_btn"):
                st.session_state.retry_default = True
                st.rerun()
        
        with col2:
            if st.button("🔧 Try with Fewer Assets", type="secondary", key="retry_fewer_btn"):
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
            try:
                market_sentiment = st.session_state.get('market_data', {}).get('ai_sentiment', {}).get('market_mood', 'neutral')
                ai_chart = ai_visualizations.create_ai_enhanced_portfolio_chart(portfolio_data, market_sentiment)
                st.plotly_chart(ai_chart, use_container_width=True)
            except Exception as e:
                st.error("❌ Error creating portfolio chart")
                # Fallback to simple chart
                if portfolio_df.shape[0] > 0:
                    fig = px.pie(portfolio_df, values='allocation_percentage', names='symbol', 
                                title='Portfolio Allocation')
                    st.plotly_chart(fig, use_container_width=True)
            
            # Token Cards - Black and White Style
            st.subheader("🪙 Portfolio Tokens")
            for asset in portfolio_data['portfolio'][:5]:  # Show top 5 tokens
                st.markdown(f"""
                <div class="token-card floating-element">
                    <div>
                        <h4 style="margin: 0; color: #D4AF37;">{asset['symbol']}</h4>
                        <p style="margin: 0; color: #ffffff;">{asset['name']}</p>
                    </div>
                    <div style="text-align: right;">
                        <p style="margin: 0; color: #D4AF37; font-size: 1.2rem;">${asset['allocation_usd']:,.2f}</p>
                        <p style="margin: 0; color: #ffffff;">{asset['allocation_percentage']:.1f}%</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Protocol Insights - Black and White Style
            st.subheader("🔍 Protocol Insights")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="protocol-card floating-element">
                    <h4>🏦 DeFi Protocols</h4>
                    <p style="color: #D4AF37; font-size: 1.2rem;">$12,450.00</p>
                    <p style="color: #FFD700;">+8.2% (24h)</p>
                    <div style="margin-top: 1rem;">
                        <span style="background: #D4AF37; color: #000000; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">Uniswap V3</span>
                        <span style="background: #D4AF37; color: #000000; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; margin-left: 0.5rem;">Aave V3</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="protocol-card floating-element">
                    <h4>⛓️ Multichain Assets</h4>
                    <p style="color: #D4AF37; font-size: 1.2rem;">$8,750.00</p>
                    <p style="color: #FFD700;">+5.1% (24h)</p>
                    <div style="margin-top: 1rem;">
                        <span style="background: #D4AF37; color: #000000; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">Ethereum</span>
                        <span style="background: #D4AF37; color: #000000; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; margin-left: 0.5rem;">Polygon</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Blockchain Integration Section
        st.subheader("🔗 Blockchain Integration")
        
        # Enhanced blockchain storage with AI validation
        if st.button("💾 Store Portfolio on Blockchain", type="secondary", key="store_blockchain_btn"):
            try:
                # Store portfolio with AI-enhanced validation
                tx_hash = portfolio_manager.save_portfolio_allocation(
                    portfolio_data=portfolio_data,
                    risk_profile=risk_profile,
                    sectors=selected_sectors
                )
                
                if tx_hash:
                    st.success("✅ Portfolio stored successfully!")
                else:
                    st.error("❌ Failed to store portfolio")
                    
            except Exception as e:
                st.error("❌ Storage error")

with tab2:
    st.subheader("📊 AI-Enhanced Market Analytics")
    try:
        market_data = mcp_optimizer.get_enhanced_market_data()
        if market_data:
            if market_data.get('ai_sentiment'):
                sentiment = market_data['ai_sentiment']
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Market Mood", sentiment.get('market_mood', 'Unknown'))
                with col2:
                    st.metric("Sentiment Score", f"{sentiment.get('sentiment_score', 0):.2f}")
                with col3:
                    st.metric("Positive Coins", sentiment.get('positive_coins', 0))
            
            if market_data.get('trending_data'):
                st.subheader("🔥 Trending Coins")
                trending = market_data['trending_data']
                if trending.get('coins'):
                    for coin in trending['coins'][:6]:
                        coin_data = coin['item']
                        st.markdown(f"""
                        <div class="trending-coin-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <h4 style="margin: 0; color: #D4AF37;">{coin_data['name']} ({coin_data['symbol'].upper()})</h4>
                                    <p style="margin: 0; color: #ffffff; font-size: 0.9rem;">Rank: #{coin_data.get('market_cap_rank', 'N/A')}</p>
                                </div>
                                <div style="text-align: right;">
                                    <p style="margin: 0; color: #D4AF37; font-size: 1.1rem;">{coin_data.get('price_btc', 0):.8f} BTC</p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
    except Exception as e:
        if "rate limit" in str(e).lower() and not st.session_state.rate_limit_notified:
            st.markdown(f'<p style="color: #ffffff;">⏱️ Rate limit exceeded. Please wait before making more requests.</p>', unsafe_allow_html=True)
            st.session_state.rate_limit_notified = True
        else:
            st.error("❌ Error loading market analytics")

with tab3:
    # AI Insights Section
    st.subheader("🤖 AI Insights")
    
    if 'portfolio_data' in st.session_state and 'market_data' in st.session_state:
        # Get AI insights
        portfolio_data = st.session_state.portfolio_data
        market_data = st.session_state.market_data
        
        # Smart recommendations
        recommendations = ai_chat.get_smart_recommendations(portfolio_data, market_data)
        
        st.subheader("💡 AI Smart Recommendations")
        if recommendations:
            st.markdown('<div class="card-grid">', unsafe_allow_html=True)
            for i, rec in enumerate(recommendations):
                # Ensure the text is visible on the background
                st.markdown(f"""
                <div class="recommendation-card">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="color: #D4AF37; font-size: 1.2rem;">💡</span>
                        <p style="margin: 0; color: #ffffff; font-size: 1rem;">{rec}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("""
                <p style="color: #000000;">Diversify across more sectors to reduce concentration risk</p>
                <p style="color: #000000;">Market sentiment is bearish - consider defensive assets</p>
                <p style="color: #000000;">Monitor your portfolio regularly and rebalance as needed</p>
                <p style="color: #000000;">Consider dollar-cost averaging for long-term stability</p>
            """, unsafe_allow_html=True)
        else:
            st.info("No recommendations available")
        
        # Market sentiment insights
        if market_data.get('ai_sentiment'):
            sentiment = market_data['ai_sentiment']
            st.subheader("📊 Market Sentiment Analysis")
            
            st.markdown('<div class="card-grid">', unsafe_allow_html=True)
            
            # Overall Mood Card
            mood_color = '#FFD700' if sentiment.get('market_mood') == 'bullish' else '#ff4444' if sentiment.get('market_mood') == 'bearish' else '#D4AF37'
            st.markdown(f"""
            <div class="metric-card">
                <h5 style="margin: 0; color: #000000; font-size: 0.8rem;">Overall Mood</h5>
                <p style="margin: 0; color: #000000; font-size: 1.2rem; font-weight: bold;">{sentiment.get('market_mood', 'Unknown')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Sentiment Score Card
            score = sentiment.get('sentiment_score', 0)
            score_color = '#FFD700' if score > 0.5 else '#ff4444' if score < -0.5 else '#D4AF37'
            st.markdown(f"""
            <div class="metric-card">
                <h5 style="margin: 0; color: #000000; font-size: 0.8rem;">Sentiment Score</h5>
                <p style="margin: 0; color: #000000; font-size: 1.2rem; font-weight: bold;">{score:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Positive Coins Card
            st.markdown(f"""
            <div class="metric-card">
                <h5 style="margin: 0; color: #000000; font-size: 0.8rem;">Positive Coins</h5>
                <p style="margin: 0; color: #000000; font-size: 1.2rem; font-weight: bold;">{sentiment.get('positive_coins', 0)}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Negative Coins Card
            st.markdown(f"""
            <div class="metric-card">
                <h5 style="margin: 0; color: #000000; font-size: 0.8rem;">Negative Coins</h5>
                <p style="margin: 0; color: #000000; font-size: 1.2rem; font-weight: bold;">{sentiment.get('negative_coins', 0)}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # AI predictions
        st.subheader("🔮 AI Predictions")
        try:
            predictions = ai_predictor.get_portfolio_predictions(portfolio_data)
            
            if predictions:
                st.markdown('<div class="card-grid">', unsafe_allow_html=True)
                for prediction in predictions:
                    confidence_color = '#FFD700' if prediction['confidence'] > 60 else '#D4AF37' if prediction['confidence'] > 40 else '#ff4444'
                    trend_color = '#FFD700' if prediction['trend'] == 'bullish' else '#ff4444'
                    
                    st.markdown(f"""
                    <div class="prediction-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                            <h4 style="margin: 0; color: #D4AF37; font-size: 1.2rem;">{prediction['asset']}</h4>
                            <span style="color: {trend_color}; font-size: 1.1rem;">{prediction['trend'].upper()}</span>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                            <div class="metric-card">
                                <h5 style="margin: 0; color: #ffffff; font-size: 0.8rem;">Predicted Price</h5>
                                <p style="margin: 0; color: #000000; font-size: 1.1rem;">${prediction['predicted_price']:,.2f}</p>
                            </div>
                            <div class="metric-card">
                                <h5 style="margin: 0; color: #ffffff; font-size: 0.8rem;">Confidence</h5>
                                <p style="margin: 0; color: #000000; font-size: 1.1rem;">{prediction['confidence']}%</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No predictions available")
        except Exception as e:
            st.error("❌ Error generating predictions")
    
    else:
        st.markdown("""
        <div style="background: #f0e68c; border: 2px solid #000000; border-radius: 8px; padding: 1rem; color: #000000;">
            Generate a portfolio first to see AI insights
        </div>
        """, unsafe_allow_html=True)

with tab4:
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
        
        if insights:
            for insight in insights:
                st.info(insight)
        else:
            st.info("No detailed insights available for this portfolio.")
    
    else:
        st.markdown("""
        <div style="background: #f0e68c; border: 2px solid #000000; border-radius: 8px; padding: 1rem; color: #000000;">
            Generate a portfolio first to see predictive analytics
        </div>
        """, unsafe_allow_html=True)