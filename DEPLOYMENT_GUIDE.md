# 🚀 Streamlit Cloud Deployment Guide

## 📋 Prerequisites

### 1. GitHub Account
- Create a free account at [github.com](https://github.com)
- This is required for Streamlit Cloud deployment

### 2. CoinGecko API Key (Optional but Recommended)
- Go to [coingecko.com/api](https://www.coingecko.com/api)
- Sign up for a free API key
- Free tier: 10,000 calls/month

### 3. Infura Account (Optional)
- Go to [infura.io](https://infura.io)
- Create account and get free Ethereum RPC endpoint
- Free tier: 100,000 requests/day

## 🎯 Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. **Initialize Git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Streamlit deployment"
   ```

2. **Create GitHub Repository**:
   - Go to [github.com](https://github.com)
   - Click "New repository"
   - Name it: `decentralized-portfolio-optimizer`
   - Make it **Public** (required for free Streamlit Cloud)
   - Don't initialize with README (you already have one)

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/decentralized-portfolio-optimizer.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**:
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

2. **Deploy Your App**:
   - Click "New app"
   - Select your repository: `decentralized-portfolio-optimizer`
   - Set the main file path: `app.py`
   - Click "Deploy!"

3. **Configure Environment Variables**:
   - In your app settings, go to "Secrets"
   - Add the following secrets:

   ```toml
   [COINGECKO_API_KEY]
   your_api_key_here = ""

   [ETHEREUM_RPC_URL]
   https://sepolia.infura.io/v3/YOUR_PROJECT_ID = ""

   [CONTRACT_ADDRESS]
   0xd0214254f898F8855C73Bd1bBD080Cb5a06A131e = ""

   [PRIVATE_KEY]
   your_test_wallet_private_key = ""

   [DEBUG]
   false = ""

   [LOG_LEVEL]
   INFO = ""
   ```

### Step 3: Test Your Deployment

1. **Check App Status**:
   - Your app will be available at: `https://your-app-name.streamlit.app`
   - Monitor the deployment logs for any errors

2. **Test Features**:
   - Portfolio generation
   - Market data display
   - Blockchain interactions (if configured)

## 🔧 Troubleshooting

### Common Issues:

1. **Import Errors**:
   - Make sure all dependencies are in `requirements.txt`
   - Check that all import paths are correct

2. **API Rate Limits**:
   - CoinGecko free tier: 50 calls/minute
   - Consider upgrading to paid plan for higher limits

3. **Memory Issues**:
   - Streamlit Cloud has 1GB RAM limit
   - Optimize data processing and caching

4. **Environment Variables**:
   - Double-check all secrets are set correctly
   - Use the exact variable names from your code

### Performance Tips:

1. **Add Caching**:
   ```python
   @st.cache_data(ttl=300)
   def expensive_function():
       # Your expensive computation
       pass
   ```

2. **Error Handling**:
   ```python
   try:
       # Your API calls
       pass
   except Exception as e:
       st.error(f"Error: {str(e)}")
   ```

3. **Loading States**:
   ```python
   with st.spinner("Loading data..."):
       # Your data loading code
       pass
   ```

## 🌐 Public Access

Once deployed, your app will be:
- **Publicly accessible** 24/7
- **Shareable** via URL
- **Embeddable** in other websites
- **Mobile-friendly** automatically

## 📊 Monitoring

- **Streamlit Cloud Dashboard**: Monitor app performance
- **GitHub Integration**: Automatic redeployment on code changes
- **Error Logs**: Available in Streamlit Cloud dashboard

## 🎉 Success!

Your app is now live and available for others to test at:
`https://your-app-name.streamlit.app`

Share this URL with others to let them test your decentralized portfolio optimizer! 