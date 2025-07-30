#!/usr/bin/env python3
"""
CoinGecko API Clients Demo
Demonstrates the comprehensive integration of CoinGecko API clients
Shows official Swagger JSON, unofficial Python wrappers, and enhanced features
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# Import the CoinGecko clients integration
try:
    from coingecko_clients_integration import (
        CoinGeckoSwaggerClient,
        PyCoinGeckoClient,
        PyCGAPIClient,
        CoinGeckoClientManager,
        get_enhanced_coingecko_data,
        get_portfolio_optimization_data,
        get_swagger_documentation
    )
    COINGECKO_CLIENTS_AVAILABLE = True
except ImportError:
    COINGECKO_CLIENTS_AVAILABLE = False
    st.error("❌ CoinGecko clients integration not available. Please install required dependencies.")

def main():
    st.set_page_config(
        page_title="CoinGecko API Clients Demo",
        page_icon="🚀",
        layout="wide"
    )
    
    st.title("🚀 CoinGecko API Clients Integration Demo")
    st.markdown("**Comprehensive demonstration of CoinGecko API clients and resources**")
    
    if not COINGECKO_CLIENTS_AVAILABLE:
        st.error("""
        ❌ **CoinGecko clients integration not available**
        
        Please install the required dependencies:
        ```bash
        pip install pycoingecko coingecko
        ```
        """)
        return
    
    # Sidebar for navigation
    st.sidebar.title("🎯 Demo Sections")
    demo_section = st.sidebar.selectbox(
        "Choose a demo section:",
        [
            "📊 Overview",
            "🔗 Official Swagger JSON",
            "🐍 Python Wrappers",
            "⚡ Enhanced Clients",
            "📈 Portfolio Optimization",
            "🔍 API Documentation"
        ]
    )
    
    if demo_section == "📊 Overview":
        show_overview()
    elif demo_section == "🔗 Official Swagger JSON":
        show_swagger_demo()
    elif demo_section == "🐍 Python Wrappers":
        show_python_wrappers_demo()
    elif demo_section == "⚡ Enhanced Clients":
        show_enhanced_clients_demo()
    elif demo_section == "📈 Portfolio Optimization":
        show_portfolio_optimization_demo()
    elif demo_section == "🔍 API Documentation":
        show_api_documentation_demo()

def show_overview():
    """Show overview of CoinGecko clients integration"""
    st.header("📊 CoinGecko API Clients Overview")
    
    st.markdown("""
    ### 🔗 **Official Resources Integrated**
    
    **Source**: [CoinGecko API Documentation](https://docs.coingecko.com/v3.0.1/docs/clients-unofficial)
    
    #### **1. Official Swagger JSON (OpenAPI Specifications)**
    - **Public API**: `https://api.coingecko.com/api/v3/swagger.json`
    - **Pro API**: `https://api.coingecko.com/api/v3/pro/swagger.json`
    - **Onchain DEX API**: `https://api.coingecko.com/api/v3/onchain-dex/swagger.json`
    
    #### **2. Unofficial Python Wrappers**
    - **coingecko (khooizhz)**: Simple and lightweight
    - **pycoingecko (man-c)**: Feature-rich and well-maintained
    - **pycgapi (nathanramoscfa)**: Enhanced with caching and analytics
    
    ### 🏗️ **Enhanced Architecture**
    """)
    
    # Architecture diagram
    st.code("""
┌─────────────────────────────────────────────────────────────────┐
│                    COINGECKO CLIENT MANAGER                    │
├─────────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   SWAGGER       │    │   PYTHON        │    │   ENHANCED  │ │
│  │   CLIENT        │    │   WRAPPERS      │    │   CLIENT    │ │
│  │                 │    │                 │    │             │ │
│  │ • OpenAPI Specs │    │ • coingecko     │    │ • Caching   │ │
│  │ • Documentation │    │ • pycoingecko   │    │ • Analysis  │ │
│  │ • Validation    │    │ • pycgapi       │    │ • Insights  │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
│           │                       │                       │     │
│           │                       │                       │     │
│           ▼                       ▼                       ▼     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              UNIFIED DATA INTERFACE                        │ │
│  │                                                           │ │
│  │ • Cross-client validation                                 │ │
│  │ • Enhanced analytics                                      │ │
│  │ • Portfolio optimization                                  │ │
│  │ • Real-time insights                                      │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
    """)
    
    st.markdown("""
    ### 🎯 **Key Features**
    
    - ✅ **Multi-Client Integration**: Combines multiple client libraries
    - ✅ **Official API Specs**: Uses OpenAPI/Swagger specifications
    - ✅ **Enhanced Analytics**: Built-in market analysis and insights
    - ✅ **Intelligent Caching**: 5-minute cache with automatic expiration
    - ✅ **Rate Limiting**: Built-in rate limit management
    - ✅ **Portfolio Optimization**: Specialized data for portfolio analysis
    - ✅ **Cross-Client Validation**: Data consistency across clients
    - ✅ **Error Handling**: Graceful error handling with user feedback
    
    ### 📊 **Data Sources**
    
    1. **Real-time Market Data**: Live prices, volumes, market caps
    2. **Historical Data**: Charts, OHLC, price history
    3. **Trending Analysis**: Popular coins and market momentum
    4. **Global Metrics**: Total market cap, volume, sentiment
    5. **DeFi Data**: DeFi-specific metrics and analytics
    6. **Portfolio Insights**: Risk assessment and optimization
    """)

def show_swagger_demo():
    """Demo the Swagger JSON client"""
    st.header("🔗 Official Swagger JSON Client Demo")
    
    try:
        # Initialize Swagger client
        swagger_client = CoinGeckoSwaggerClient()
        
        # Get API documentation
        with st.spinner("📖 Fetching Swagger documentation..."):
            docs = swagger_client.get_api_documentation()
        
        if docs:
            st.success("✅ Successfully fetched Swagger documentation")
            
            # Display available API types
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'public' in docs:
                    st.metric("Public API", "Available")
                    public_spec = docs['public']
                    st.write(f"**Version**: {public_spec.get('version', 'Unknown')}")
                    st.write(f"**Endpoints**: {len(public_spec.get('endpoints', []))}")
            
            with col2:
                if 'pro' in docs:
                    st.metric("Pro API", "Available")
                    pro_spec = docs['pro']
                    st.write(f"**Version**: {pro_spec.get('version', 'Unknown')}")
                    st.write(f"**Endpoints**: {len(pro_spec.get('endpoints', []))}")
            
            with col3:
                if 'onchain_dex' in docs:
                    st.metric("Onchain DEX API", "Available")
                    dex_spec = docs['onchain_dex']
                    st.write(f"**Version**: {dex_spec.get('version', 'Unknown')}")
                    st.write(f"**Endpoints**: {len(dex_spec.get('endpoints', []))}")
            
            # Show endpoint details
            st.subheader("📋 Available Endpoints")
            
            if 'public' in docs and docs['public'].get('endpoints'):
                endpoints = docs['public']['endpoints'][:10]  # Show first 10
                
                endpoint_data = []
                for endpoint in endpoints:
                    endpoint_data.append({
                        'Method': endpoint.get('method', ''),
                        'Path': endpoint.get('path', ''),
                        'Summary': endpoint.get('summary', '')[:50] + '...' if len(endpoint.get('summary', '')) > 50 else endpoint.get('summary', ''),
                        'Tags': ', '.join(endpoint.get('tags', []))
                    })
                
                df = pd.DataFrame(endpoint_data)
                st.dataframe(df, use_container_width=True)
            
            # Show API key status
            st.subheader("🔑 API Key Status")
            api_status = {
                'Demo API Key': '✅ Available' if swagger_client.demo_api_key else '❌ Not Set',
                'Pro API Key': '✅ Available' if swagger_client.pro_api_key else '❌ Not Set',
                'API Type': swagger_client.api_type.upper()
            }
            
            for key, value in api_status.items():
                st.write(f"**{key}**: {value}")
        
        else:
            st.error("❌ Failed to fetch Swagger documentation")
    
    except Exception as e:
        st.error(f"❌ Error in Swagger demo: {str(e)}")

def show_python_wrappers_demo():
    """Demo the Python wrapper clients"""
    st.header("🐍 Python Wrappers Demo")
    
    try:
        # Initialize Python client
        py_client = PyCoinGeckoClient()
        
        # Test different endpoints
        st.subheader("📊 Market Data")
        
        with st.spinner("🔄 Fetching market data..."):
            market_data = py_client.get_coins_markets(per_page=20)
        
        if market_data and len(market_data) > 1:  # Last item is analysis
            # Remove analysis item for display
            display_data = [item for item in market_data if not isinstance(item, dict) or 'analysis' not in item]
            
            if display_data:
                # Create DataFrame for display
                df_data = []
                for coin in display_data[:10]:  # Show first 10
                    df_data.append({
                        'Rank': coin.get('market_cap_rank', 'N/A'),
                        'Name': coin.get('name', 'N/A'),
                        'Symbol': coin.get('symbol', 'N/A').upper(),
                        'Price (USD)': f"${coin.get('current_price', 0):,.2f}",
                        'Market Cap': f"${coin.get('market_cap', 0):,.0f}",
                        '24h Change': f"{coin.get('price_change_percentage_24h', 0):.2f}%",
                        '24h Volume': f"${coin.get('total_volume', 0):,.0f}"
                    })
                
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True)
                
                # Show market analysis
                if len(market_data) > 1 and isinstance(market_data[-1], dict) and 'market_analysis' in market_data[-1]:
                    analysis = market_data[-1]['market_analysis']
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Coins", analysis.get('total_coins', 0))
                    with col2:
                        st.metric("Positive", analysis.get('positive_coins', 0))
                    with col3:
                        st.metric("Negative", analysis.get('negative_coins', 0))
                    with col4:
                        sentiment = analysis.get('market_sentiment', 'neutral')
                        st.metric("Sentiment", sentiment.title())
        
        st.subheader("🔥 Trending Coins")
        
        with st.spinner("🔄 Fetching trending coins..."):
            trending_data = py_client.get_trending_coins()
        
        if trending_data and 'coins' in trending_data:
            trending_coins = trending_data['coins'][:5]  # Show top 5
            
            trending_df_data = []
            for coin in trending_coins:
                item = coin['item']
                trending_df_data.append({
                    'Name': item.get('name', 'N/A'),
                    'Symbol': item.get('symbol', 'N/A').upper(),
                    'Market Cap Rank': item.get('market_cap_rank', 'N/A'),
                    'Score': item.get('score', 0),
                    'Category': item.get('category', 'N/A')
                })
            
            if trending_df_data:
                trending_df = pd.DataFrame(trending_df_data)
                st.dataframe(trending_df, use_container_width=True)
        
        st.subheader("🌍 Global Market Data")
        
        with st.spinner("🔄 Fetching global data..."):
            global_data = py_client.get_global_market_data()
        
        if global_data and 'data' in global_data:
            data = global_data['data']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Market Cap", f"${data.get('total_market_cap', {}).get('usd', 0):,.0f}B")
            with col2:
                st.metric("24h Volume", f"${data.get('total_volume', {}).get('usd', 0):,.0f}B")
            with col3:
                change_24h = data.get('market_cap_change_percentage_24h_usd', 0)
                st.metric("24h Change", f"{change_24h:.2f}%")
            with col4:
                st.metric("Active Coins", data.get('active_cryptocurrencies', 0))
    
    except Exception as e:
        st.error(f"❌ Error in Python wrappers demo: {str(e)}")

def show_enhanced_clients_demo():
    """Demo the enhanced clients"""
    st.header("⚡ Enhanced Clients Demo")
    
    try:
        # Initialize enhanced client
        pycg_client = PyCGAPIClient()
        
        # Test enhanced coins data
        st.subheader("📊 Enhanced Coins Data")
        
        # Sample coin IDs for demo
        demo_coins = ['bitcoin', 'ethereum', 'cardano', 'solana', 'polkadot']
        
        with st.spinner("🔄 Fetching enhanced data..."):
            enhanced_data = pycg_client.get_enhanced_coins_data(demo_coins)
        
        if enhanced_data:
            st.success("✅ Successfully fetched enhanced data")
            
            # Show data components
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**📈 Price Data**")
                if enhanced_data.get('price_data'):
                    price_data = enhanced_data['price_data']
                    price_df_data = []
                    for coin_id, data in price_data.items():
                        if 'usd' in data:
                            price_df_data.append({
                                'Coin': coin_id.title(),
                                'Price (USD)': f"${data['usd']:,.2f}",
                                'Market Cap': f"${data.get('usd_market_cap', 0):,.0f}",
                                '24h Volume': f"${data.get('usd_24h_vol', 0):,.0f}",
                                '24h Change': f"{data.get('usd_24h_change', 0):.2f}%"
                            })
                    
                    if price_df_data:
                        price_df = pd.DataFrame(price_df_data)
                        st.dataframe(price_df, use_container_width=True)
            
            with col2:
                st.write("**📊 Analysis**")
                if enhanced_data.get('analysis'):
                    analysis = enhanced_data['analysis']
                    
                    st.metric("Total Coins", analysis.get('total_coins', 0))
                    st.metric("Data Quality", analysis.get('data_quality', 'Unknown'))
                    
                    if 'portfolio_insights' in analysis:
                        insights = analysis['portfolio_insights']
                        st.write(f"**Diversification Score**: {insights.get('diversification_score', 0):.2f}")
                        st.write(f"**Market Sentiment**: {insights.get('market_sentiment', 'Unknown')}")
                        st.write(f"**Risk Level**: {insights.get('risk_level', 'Unknown')}")
        
        # Show caching information
        st.subheader("💾 Caching System")
        st.info("""
        **Intelligent Caching Features:**
        - ✅ **5-minute cache duration** for optimal performance
        - ✅ **Automatic cache expiration** to ensure fresh data
        - ✅ **Cache key generation** based on request parameters
        - ✅ **Memory-efficient storage** with timestamp tracking
        """)
    
    except Exception as e:
        st.error(f"❌ Error in enhanced clients demo: {str(e)}")

def show_portfolio_optimization_demo():
    """Demo portfolio optimization features"""
    st.header("📈 Portfolio Optimization Demo")
    
    try:
        # Initialize client manager
        client_manager = CoinGeckoClientManager()
        
        # Demo coin selection
        st.subheader("🎯 Portfolio Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            risk_profile = st.selectbox(
                "Risk Profile:",
                ["low", "medium", "high"],
                index=1
            )
            
            investment_amount = st.number_input(
                "Investment Amount (USD):",
                min_value=1000,
                max_value=1000000,
                value=10000,
                step=1000
            )
        
        with col2:
            demo_coins = ['bitcoin', 'ethereum', 'cardano', 'solana', 'polkadot']
            selected_coins = st.multiselect(
                "Select Coins:",
                demo_coins,
                default=demo_coins[:3]
            )
            
            if not selected_coins:
                st.warning("⚠️ Please select at least one coin")
                return
        
        # Get portfolio optimization data
        with st.spinner("🔄 Optimizing portfolio..."):
            portfolio_data = client_manager.get_portfolio_optimization_data(
                selected_coins, risk_profile
            )
        
        if portfolio_data:
            st.success("✅ Portfolio optimization completed")
            
            # Display portfolio insights
            st.subheader("📊 Portfolio Insights")
            
            if 'optimization_insights' in portfolio_data:
                insights = portfolio_data['optimization_insights']
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**🎯 Recommended Allocation**")
                    if 'recommended_allocation' in insights:
                        allocation = insights['recommended_allocation']
                        for cap_type, percentage in allocation.items():
                            st.write(f"• {cap_type.replace('_', ' ').title()}: {percentage}%")
                
                with col2:
                    st.write("**⏰ Market Timing**")
                    if 'market_timing' in insights:
                        timing = insights['market_timing']
                        st.write(f"• Recommendation: {timing.get('recommendation', 'Unknown')}")
                        st.write(f"• Action: {timing.get('action', 'Unknown')}")
                        st.write(f"• Confidence: {timing.get('confidence', 0):.2f}")
                
                with col3:
                    st.write("**💡 Diversification Tips**")
                    if 'diversification_tips' in insights:
                        tips = insights['diversification_tips']
                        for tip in tips[:3]:  # Show first 3 tips
                            st.write(f"• {tip}")
            
            # Show market sentiment
            if 'market_sentiment' in portfolio_data:
                sentiment = portfolio_data['market_sentiment']
                
                st.subheader("📈 Market Sentiment")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Sentiment Score", f"{sentiment.get('sentiment_score', 0):.2f}")
                with col2:
                    st.metric("Positive Coins", sentiment.get('positive_coins', 0))
                with col3:
                    st.metric("Negative Coins", sentiment.get('negative_coins', 0))
                with col4:
                    mood = sentiment.get('market_mood', 'neutral')
                    st.metric("Market Mood", mood.title())
        
        else:
            st.error("❌ Failed to optimize portfolio")
    
    except Exception as e:
        st.error(f"❌ Error in portfolio optimization demo: {str(e)}")

def show_api_documentation_demo():
    """Demo API documentation features"""
    st.header("🔍 API Documentation Demo")
    
    try:
        # Get comprehensive documentation
        with st.spinner("📖 Fetching API documentation..."):
            docs = get_swagger_documentation()
        
        if docs:
            st.success("✅ Successfully fetched API documentation")
            
            # Show documentation overview
            st.subheader("📋 Documentation Overview")
            
            for api_type, spec in docs.items():
                with st.expander(f"📚 {api_type.upper()} API Documentation"):
                    st.write(f"**Version**: {spec.get('version', 'Unknown')}")
                    st.write(f"**Endpoints**: {len(spec.get('endpoints', []))}")
                    
                    # Show sample endpoints
                    if spec.get('endpoints'):
                        st.write("**Sample Endpoints:**")
                        for endpoint in spec['endpoints'][:5]:  # Show first 5
                            st.code(f"{endpoint.get('method', 'GET')} {endpoint.get('path', '')}")
                            if endpoint.get('summary'):
                                st.write(f"*{endpoint.get('summary')}*")
                            st.write("---")
            
            # Show useful links
            st.subheader("🔗 Useful Links")
            
            links = {
                "CoinGecko API Documentation": "https://docs.coingecko.com/v3.0.1/docs/clients-unofficial",
                "Public API Swagger JSON": "https://api.coingecko.com/api/v3/swagger.json",
                "Pro API Swagger JSON": "https://api.coingecko.com/api/v3/pro/swagger.json",
                "Onchain DEX API Swagger JSON": "https://api.coingecko.com/api/v3/onchain-dex/swagger.json",
                "API Status": "https://status.coingecko.com/",
                "Rate Limits": "https://docs.coingecko.com/docs/rate-limits"
            }
            
            for name, url in links.items():
                st.write(f"• [{name}]({url})")
        
        else:
            st.error("❌ Failed to fetch API documentation")
    
    except Exception as e:
        st.error(f"❌ Error in API documentation demo: {str(e)}")

if __name__ == "__main__":
    main() 