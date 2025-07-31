# 🔐 Streamlit Cloud Secrets Configuration

## 📋 Required Environment Variables

When deploying to Streamlit Cloud, you need to configure these secrets in your app settings:

### 1. **CoinGecko API Key** (Optional but Recommended)
```toml
[COINGECKO_API_KEY]
your_api_key_here = ""
```
- **Get it from**: [coingecko.com/api](https://www.coingecko.com/api)
- **Free tier**: 10,000 calls/month
- **Without it**: App uses public API (50 calls/minute limit)

### 2. **Ethereum RPC URL** (Optional)
```toml
[ETHEREUM_RPC_URL]
https://sepolia.infura.io/v3/YOUR_PROJECT_ID = ""
```
- **Get it from**: [infura.io](https://infura.io)
- **Free tier**: 100,000 requests/day
- **Network**: Sepolia testnet (for testing)

### 3. **Smart Contract Address** (Optional)
```toml
[CONTRACT_ADDRESS]
0xd0214254f898F8855C73Bd1bBD080Cb5a06A131e = ""
```
- **Default**: Pre-deployed contract on Sepolia
- **Purpose**: Portfolio storage on blockchain

### 4. **Private Key** (Optional - for testing only)
```toml
[PRIVATE_KEY]
your_test_wallet_private_key = ""
```
- **⚠️ WARNING**: Use only test wallet private keys
- **Purpose**: Blockchain transactions for testing
- **Security**: Never use real wallet keys

### 5. **Application Settings** (Optional)
```toml
[DEBUG]
false = ""

[LOG_LEVEL]
INFO = ""
```

## 🎯 How to Set Secrets in Streamlit Cloud

### Step 1: Access Your App Settings
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Find your deployed app
3. Click on the app name
4. Go to "Settings" tab

### Step 2: Configure Secrets
1. Scroll down to "Secrets" section
2. Click "Edit secrets"
3. Add the configuration in TOML format:

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

### Step 3: Save and Redeploy
1. Click "Save"
2. Your app will automatically redeploy
3. Check the deployment logs for any errors

## 🔧 Testing Without Secrets

If you don't want to set up API keys immediately, your app will still work with:

- **Public CoinGecko API** (limited to 50 calls/minute)
- **Demo mode** for blockchain features
- **Basic portfolio optimization**

## 🚨 Security Notes

1. **Never commit secrets to Git**
2. **Use only test wallets for private keys**
3. **Free API keys are sufficient for testing**
4. **Monitor your API usage**

## 📊 Monitoring Usage

### CoinGecko API Limits:
- **Free tier**: 10,000 calls/month
- **Public API**: 50 calls/minute
- **Monitor at**: [coingecko.com/api](https://www.coingecko.com/api)

### Infura Limits:
- **Free tier**: 100,000 requests/day
- **Monitor at**: [infura.io](https://infura.io)

## 🎉 Ready to Deploy!

Once you've configured your secrets, your app will be:
- ✅ **Fully functional** with all features
- ✅ **24/7 available** for public testing
- ✅ **Rate-limited** appropriately
- ✅ **Secure** with proper error handling

Your app URL will be: `https://your-app-name.streamlit.app` 