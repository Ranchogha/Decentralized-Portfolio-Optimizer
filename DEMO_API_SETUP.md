# 🎯 CoinGecko Demo API Key Setup Guide

## 🚀 Quick Setup for Free Demo API Key

### **Step 1: Get Your Free Demo API Key**

1. **Visit the Demo API Guide**: [CoinGecko Demo API Guide](https://support.coingecko.com/hc/en-us/articles/21880397454233-User-Guide-How-to-sign-up-for-CoinGecko-Demo-API-and-generate-an-API-key)

2. **Sign up for free Demo API key**:
   - Go to [CoinGecko API Pricing](https://www.coingecko.com/en/api/pricing)
   - Click on "Demo API" (Free tier)
   - Sign up with your email
   - Verify your email
   - Generate your Demo API key

3. **Copy your Demo API key** (it looks like: `CG-xxxxxxxxxxxxxxxxxxxxxxxx`)

### **Step 2: Configure the Demo API Key**

#### **Option A: Using .env file (Recommended)**

Create a `.env` file in your project root:

```env
COINGECKO_DEMO_API_KEY=CG-your_demo_api_key_here
```

#### **Option B: Using Environment Variable**

**Windows (PowerShell):**
```powershell
$env:COINGECKO_DEMO_API_KEY="CG-your_demo_api_key_here"
```

**Windows (Command Prompt):**
```cmd
set COINGECKO_DEMO_API_KEY=CG-your_demo_api_key_here
```

**Linux/Mac:**
```bash
export COINGECKO_DEMO_API_KEY="CG-your_demo_api_key_here"
```

### **Step 3: Test the Setup**

Run the application to verify the Demo API key is working:

```bash
streamlit run mcp_enhanced_app.py --server.port 8503
```

You should see: `✅ CoinGecko MCP Server configured with Demo API key`

## 🎯 **Demo API Features Available**

| Feature | Demo API | Status |
|---------|----------|--------|
| **Rate Limit** | 30 calls/min | ✅ |
| **Monthly Credits** | 10,000 | ✅ |
| **Historical Data** | 1 year | ✅ |
| **Simple Price API** | ✅ | ✅ |
| **Market Data** | ✅ | ✅ |
| **Trending Coins** | ✅ | ✅ |
| **Global Market Data** | ✅ | ✅ |
| **DeFi Market Data** | ✅ | ✅ |
| **Categories** | ✅ | ✅ |
| **Search** | ✅ | ✅ |
| **Exchange Rates** | ✅ | ✅ |
| **Asset Platforms** | ✅ | ✅ |
| **Exchanges** | ✅ | ✅ |
| **Top Gainers/Losers** | ✅ | ✅ |
| **NFT Collections** | ❌ | Pro Only |
| **Derivatives** | ❌ | Pro Only |

## 🚀 **Demo API Benefits**

- ✅ **Completely Free** - No credit card required
- ✅ **10,000 monthly credits** - Plenty for testing and development
- ✅ **30 calls per minute** - Good for most use cases
- ✅ **1 year historical data** - Sufficient for most analysis
- ✅ **All core features** - Everything you need for portfolio optimization
- ✅ **MCP Server access** - Full MCP integration

## 🔧 **Troubleshooting**

### **If you see "No API key found":**
1. Make sure you created the `.env` file in the project root
2. Check that the API key starts with `CG-`
3. Restart the application after adding the API key

### **If you see "Unauthorized":**
1. Verify your API key is correct
2. Make sure you copied the entire key including `CG-` prefix
3. Check that your Demo API key is active

### **If you see "Rate limit exceeded":**
1. Wait a minute before making more requests
2. Demo API has 30 calls per minute limit
3. Consider upgrading to Pro for higher limits

## 🎉 **Ready to Go!**

Once you've set up your Demo API key, you'll have access to:

- 🤖 **MCP Server Integration** - Real-time crypto data
- 🎯 **AI Portfolio Optimization** - Enhanced with MCP data
- 📊 **Market Analysis** - Comprehensive market insights
- 🔥 **Trending Analysis** - Real-time trending coins
- ⚖️ **Risk Metrics** - Advanced risk calculation
- 🏦 **DeFi Analytics** - DeFi market data
- 🔗 **Blockchain Integration** - Smart contract storage

The Demo API key gives you access to all the core features needed for a powerful crypto portfolio optimizer! 