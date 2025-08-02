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
        border: 1px solid #D4AF37;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .stButton > button[data-testid="baseButton-secondary"]:hover {
        transform: translateY(-2px);
        background: #111111;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    }
    
    /* Gold Accent Border for Streamlit elements */
    .stMarkdown, .stAlert, .stSelectbox, .stTextInput, .stMultiSelect, .stProgress, .stTable, .stDataFrame, .stExpander, .stJson {
        border-radius: 8px;
        border: 1px solid #D4AF37;
        padding: 1rem;
        margin-bottom: 1rem;
        background: #f9f9f9;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Custom Styling for Portfolio Insights Cards */
    .portfolio-insight-card {
        background: #f0e68c; /* Khaki background for readability */
        border: 2px solid #000000;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        color: #000000; /* Ensure text is black */
    }

    .portfolio-insight-card h4 {
        color: #000000;
        margin-top: 0;
    }
    
    /* Custom Styling for Trending Coins Cards */
    .trending-coin-card {
        background: #000000; /* Black background */
        color: #ffffff; /* White text */
        border: 1px solid #D4AF37; /* Gold border */
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .trending-coin-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(212, 175, 55, 0.3);
        background: #111111;
    }
    
    .trending-coin-card h5 {
        color: #D4AF37; /* Gold heading */
        margin: 0;
    }
    
    /* Fix for Streamlit's default text input label color */
    .stTextInput > label, .stSelectbox > label {
        color: #000000; /* Explicitly set label color to black */
    }

    /* Adjust the rate limit alert to be more readable */
    .rate-limit-alert {
        background-color: #ffaa00; /* A readable yellow/orange color */
        color: #000000; /* Black text for contrast */
        border: 2px solid #ffaa00;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: bold;
    }
    
</style>
""", unsafe_allow_html=True)


st.markdown("<div class='main-header'><h1>🚀 Decentralized Portfolio Optimizer</h1></div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: black; font-weight: bold;'>Your AI-powered gateway to intelligent crypto portfolio management and analysis.</p>", unsafe_allow_html=True)

# Sidebar for AI Chat
with st.sidebar:
    st.markdown("<div class='ai-feature'><h3>AI Crypto Assistant <span class='ai-badge'>LIVE</span></h3></div>", unsafe_allow_html=True)
    ai_chat()

# Check MCP Server Status in Sidebar
with st.sidebar:
    st.subheader("MCP Server Status")
    status_placeholder = st.empty()
    if st.button("Check Status", key="mcp_status_button", help="Click to check the live status of the CoinGecko MCP Server"):
        server_status = check_mcp_server_status(mcp_server)
        if server_status == "online":
            status_placeholder.markdown(f"<p class='status-indicator status-online'></p> <span style='color:black;'>Status: Online</span>", unsafe_allow_html=True)
        else:
            status_placeholder.markdown(f"<p class='status-indicator status-offline'></p> <span style='color:black;'>Status: Offline</span>", unsafe_allow_html=True)

# Main tabs for different functionalities
tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Market Trends", "AI Optimizer", "Transactions"])

with tab1:
    st.header("Dashboard")
    
    # Portfolio Summary
    st.subheader("📊 Portfolio Summary")
    
    # Placeholder for portfolio data
    portfolio_data = portfolio_manager.get_portfolio_data()
    
    if portfolio_data and not portfolio_data.empty:
        # Calculate key metrics
        total_value = portfolio_data['Value'].sum()
        total_profit_loss = portfolio_data['Profit/Loss'].sum()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='metric-card'><h4>Total Portfolio Value</h4><p>{total_value:,.2f} USD</p></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-card'><h4>Total Profit/Loss</h4><p>{total_profit_loss:,.2f} USD</p></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='metric-card'><h4>Asset Count</h4><p>{len(portfolio_data)}</p></div>", unsafe_allow_html=True)
        
        st.subheader("Asset Breakdown")
        
        # Pie chart for asset distribution
        fig_pie = px.pie(
            portfolio_data,
            values='Value',
            names='Symbol',
            title='Asset Distribution by Value',
            hole=0.4,
            template="plotly_dark",
            color_discrete_sequence=px.colors.sequential.Agsunset,
            width=500,
            height=500
        )
        st.plotly_chart(fig_pie)
        
        st.subheader("Portfolio Performance (last 30 days)")
        
        # Line chart for portfolio performance
        performance_data = portfolio_manager.get_historical_performance()
        if performance_data and not performance_data.empty:
            fig_perf = px.line(
                performance_data,
                x='Date',
                y='Total Value',
                title='Portfolio Value Over Time',
                template="plotly_dark"
            )
            st.plotly_chart(fig_perf)
        else:
            st.info("No historical performance data available.")
        
        st.subheader("Portfolio Volatility Analysis")
        risk_data = portfolio_manager.get_risk_metrics()
        if risk_data:
            st.markdown(f"""
            <div class='risk-card'>
                <h4>Risk Metrics</h4>
                <p><strong>Beta (vs. Market)</strong>: {risk_data['beta']:.2f}</p>
                <p><strong>Sharpe Ratio</strong>: {risk_data['sharpe_ratio']:.2f}</p>
                <p><strong>VaR (95%)</strong>: {risk_data['var_95']:.2f} USD</p>
                <p><strong>Expected Shortfall</strong>: {risk_data['es_95']:.2f} USD</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No risk analysis data available.")
            
    else:
        st.info("Your portfolio is empty. Add a wallet or token to get started!")

    # Fix for duplicated "Analytics" section - removed the extra code block.
    st.header("Analytics")
    st.markdown("<p style='color:black;'>Dive deep into your portfolio's performance with advanced analytics.</p>", unsafe_allow_html=True)
    ai_visualizations()


with tab2:
    st.header("Market Trends and Insights")
    
    # Check MCP server status and handle rate limits
    if not st.session_state.rate_limit_notified:
        try:
            mcp_server.check_status()
        except Exception as e:
            if "rate limit exceeded" in str(e).lower():
                st.session_state.rate_limit_notified = True
                st.markdown("<div class='rate-limit-alert'>Rate limit exceeded. Please wait a few seconds before retrying.</div>", unsafe_allow_html=True)

    if st.session_state.rate_limit_notified:
        st.markdown("<div class='rate-limit-alert'>Rate limit exceeded. Please wait a few seconds before retrying.</div>", unsafe_allow_html=True)
    else:
        # Trending Coins
        st.subheader("🔥 Trending Coins")
        trending_coins = mcp_server.get_trending_coins()
        if trending_coins:
            for coin in trending_coins:
                st.markdown(f"""
                <div class="trending-coin-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1;">
                            <h5>{coin['name']} ({coin['symbol'].upper()})</h5>
                            <p style="font-size: 0.9em; color: #D4AF37;">Rank: {coin['market_cap_rank']}</p>
                        </div>
                        <div style="text-align: right;">
                            <p style="font-size: 1.1em; font-weight: bold;">{coin['price_change_percentage_24h']:.2f}%</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Could not fetch trending coins.")
        
        # Top Performing Sectors
        st.subheader("🏆 Top Performing Sectors")
        top_sectors = mcp_server.get_top_sectors()
        if top_sectors:
            col1, col2 = st.columns(2)
            with col1:
                st.info("Top 5 Sectors (24h Change)")
                for sector in top_sectors[:5]:
                    st.markdown(f"""
                        <div class="sector-card">
                            <p><strong>{sector['name']}</strong>: {sector['price_change_24h']:.2f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
            with col2:
                st.info("Bottom 5 Sectors (24h Change)")
                for sector in top_sectors[-5:]:
                    st.markdown(f"""
                        <div class="sector-card">
                            <p><strong>{sector['name']}</strong>: {sector['price_change_24h']:.2f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.warning("Could not fetch sector data.")

with tab3:
    st.header("AI-Powered Portfolio Optimizer")
    
    st.subheader("🌟 Optimal Portfolio Configuration")
    
    portfolio_value = st.number_input("Enter your total portfolio value (USD):", min_value=100.0, value=10000.0)
    
    st.markdown("---")
    
    if st.button("Generate Optimized Portfolio", key="optimize_button", type="primary"):
        with st.spinner("Generating optimal portfolio..."):
            optimized_allocations = mcp_optimizer.optimize_portfolio(portfolio_value)
            st.success("Optimization Complete!")
            
            # Display results
            if optimized_allocations:
                # Assuming optimized_allocations is a dictionary like {'bitcoin': 0.5, 'ethereum': 0.3, ...}
                df_allocations = pd.DataFrame(
                    list(optimized_allocations.items()),
                    columns=['Token', 'Allocation (%)']
                )
                df_allocations['Allocation (%)'] = df_allocations['Allocation (%)'] * 100
                st.write(df_allocations)
                
                fig_alloc = px.bar(
                    df_allocations,
                    x='Token',
                    y='Allocation (%)',
                    title='Optimal Asset Allocation',
                    color='Token',
                    template="plotly_dark",
                    labels={'Allocation (%)': 'Allocation Percentage'}
                )
                st.plotly_chart(fig_alloc)
            else:
                st.error("Failed to generate an optimized portfolio. Please try again later.")

with tab4:
    st.header("Transaction History and Details")
    
    st.subheader("🔗 Connect Wallets")
    
    # Wallet management
    if st.button("Add New Wallet", key="add_wallet_button"):
        with st.form("new_wallet_form"):
            address = st.text_input("Wallet Address")
            name = st.text_input("Name (optional)")
            submitted = st.form_submit_button("Add Wallet")
            if submitted:
                wallet_manager.add_wallet(address, name)
                st.success(f"Wallet {name or address} added!")
    
    wallets = wallet_manager.get_all_wallets()
    if wallets:
        st.subheader("Your Connected Wallets")
        for wallet in wallets:
            st.write(f"**{wallet['name'] or wallet['address']}**: `{wallet['address']}`")
    
    st.subheader("📋 Transaction History")
    
    selected_wallet = st.selectbox(
        "Select Wallet to view transactions:",
        options=[w['address'] for w in wallets] if wallets else ["-"],
        format_func=lambda x: wallet_manager.get_wallet_by_address(x)['name'] or x if x != "-" else "No wallets connected"
    )
    
    if selected_wallet and selected_wallet != "-":
        transactions = portfolio_manager.get_transactions(selected_wallet)
        if transactions:
            df_transactions = pd.DataFrame(transactions)
            st.dataframe(df_transactions, use_container_width=True)
        else:
            st.info("No transactions found for this wallet.")
    
    st.subheader("ℹ️ Portfolio Insights")
    
    insights = get_mcp_enhanced_data()
    if insights:
        for insight in insights:
            st.markdown(f"""
            <div class="portfolio-insight-card">
                <h4>{insight.get('title', 'No Title')}</h4>
                <p>{insight.get('content', 'No Content')}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No AI insights available at this time.")