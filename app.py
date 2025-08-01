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

# Beautiful Black and White Theme with Gold Accents
st.markdown("""
<style>
    /* Clean Black and White Theme with Gold Accents */
    .stApp {
        background: #ffffff;
        color: #000000;
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
    st.subheader("🚀 Quick AI Actions")
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

# Beautiful Black and White Theme with Gold Accents
st.markdown("""
<style>
    /* Clean Black and White Theme with Gold Accents */
    .stApp {
        background: #ffffff;
        color: #000000;
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
    st.subheader("🚀 Quick AI Actions")
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
