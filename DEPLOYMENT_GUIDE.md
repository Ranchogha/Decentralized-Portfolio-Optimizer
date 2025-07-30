# 🚀 Deployment Guide - Portfolio Storage Contract

## 📋 **Prerequisites**

1. **MetaMask Wallet** with some test ETH
2. **Remix IDE** (online or desktop)
3. **Infura Account** (for RPC endpoint)

## 🔧 **Step 1: Deploy Contract**

### **Using Remix IDE:**

1. **Open Remix**: Go to [remix.ethereum.org](https://remix.ethereum.org)

2. **Load Contract**: 
   - Copy `contracts/PortfolioStorage.sol` content
   - Paste into Remix editor

3. **Compile Contract**:
   - Go to "Solidity Compiler" tab
   - Click "Compile PortfolioStorage.sol"
   - Verify compilation success

4. **Deploy Contract**:
   - Go to "Deploy & Run Transactions" tab
   - Select "Injected Provider - MetaMask"
   - Choose network (Sepolia testnet recommended)
   - Click "Deploy"
   - Confirm transaction in MetaMask

5. **Copy Contract Address**:
   - After deployment, copy the contract address
   - Save it for your `.env` file

## 🔧 **Step 2: Configure Environment**

### **Create `.env` file:**

```env
# Ethereum Network Configuration
ETHEREUM_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID
CONTRACT_ADDRESS=0xd0214254f898F8855C73Bd1bBD080Cb5a06A131e

# Optional: For real transactions
PRIVATE_KEY=your_private_key_here

# Application Configuration
DEBUG=true
LOG_LEVEL=INFO
```

### **Get Infura Project ID:**

1. Go to [infura.io](https://infura.io)
2. Create account and new project
3. Copy your project ID
4. Replace `YOUR_INFURA_PROJECT_ID` in `.env`

## 🔧 **Step 3: Test Integration**

### **Run Test Script:**

```bash
python test_contract_integration.py
```

**Expected Output:**
```
🚀 Testing Contract Integration with Remix Build Artifacts
============================================================

✅ Build Artifacts Structure: PASSED
✅ ABI Loading: PASSED  
✅ Contract Initialization: PASSED
✅ Portfolio Data Preparation: PASSED

📊 Test Results: 4/4 tests passed
🎉 All tests passed! Contract integration is working correctly.
```

## 🔧 **Step 4: Update Web Application**

### **Update `app.py`:**

```python
# Add to your imports
from web3_integration import EthereumPortfolioManager

# Initialize portfolio manager
portfolio_manager = EthereumPortfolioManager()

# In your portfolio generation function:
if st.button("Save to Blockchain"):
    success = portfolio_manager.store_portfolio_on_blockchain(
        portfolio_data=optimized_portfolio,
        risk_profile=selected_risk_profile,
        sectors=selected_sectors
    )
    
    if success:
        st.success("✅ Portfolio saved to blockchain!")
    else:
        st.error("❌ Failed to save portfolio")
```

## 🔧 **Step 5: Run Application**

### **Start the Web App:**

```bash
python deploy.py --start
```

**Or manually:**
```bash
streamlit run app.py
```

## 🔍 **Troubleshooting**

### **Common Issues:**

1. **"Failed to connect to Ethereum network"**
   - Check your `ETHEREUM_RPC_URL` in `.env`
   - Verify Infura project is active

2. **"Contract ABI not loaded"**
   - Ensure build artifacts are in `contracts/build/`
   - Check file permissions

3. **"Transaction failed"**
   - Ensure you have test ETH in your wallet
   - Check gas settings in MetaMask

4. **"Build artifacts not found"**
   - Copy Remix build artifacts to `contracts/build/`
   - Ensure file structure is correct

### **Network Configuration:**

**Testnet Options:**
- **Sepolia**: `https://sepolia.infura.io/v3/YOUR_PROJECT_ID` (Recommended)
- **Goerli**: `https://goerli.infura.io/v3/YOUR_PROJECT_ID` (Deprecated)

**Mainnet (Production):**
- **Ethereum**: `https://mainnet.infura.io/v3/YOUR_PROJECT_ID`

## 🎯 **Production Checklist**

- [ ] Contract deployed to target network
- [ ] Contract address added to `.env`
- [ ] Infura project configured
- [ ] Test script passes (4/4 tests)
- [ ] Web application updated
- [ ] MetaMask connected to correct network
- [ ] Test transaction successful

## 🎉 **Success Indicators**

✅ **Contract Integration**: All functions working  
✅ **Web Application**: Portfolio storage functional  
✅ **Blockchain Storage**: Data saved on-chain  
✅ **Data Retrieval**: Portfolio data readable  
✅ **Error Handling**: Graceful error management  

**Your decentralized portfolio optimizer is now ready for production!** 🚀 