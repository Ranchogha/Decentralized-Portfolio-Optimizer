#!/usr/bin/env python3
"""
Multi-Wallet Manager for Decentralized Portfolio Optimizer
Supports MetaMask, WalletConnect, and other popular wallets
"""

import streamlit as st
import json
import time
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

class MultiWalletManager:
    """Multi-wallet manager supporting various wallet types"""
    
    def __init__(self):
        self.w3 = None
        self.connected_wallet = None
        self.wallet_type = None
        self.account_address = None
        self.chain_id = None
        self.network_name = None
        
        # Initialize Web3 connection
        self._initialize_web3()
        
        # Supported wallet types
        self.supported_wallets = {
            'metamask': {
                'name': 'MetaMask',
                'icon': '🦊',
                'description': 'Browser extension wallet',
                'supported': True
            },
            'walletconnect': {
                'name': 'WalletConnect',
                'icon': '🔗',
                'description': 'Mobile wallet connection',
                'supported': True
            },
            'coinbase': {
                'name': 'Coinbase Wallet',
                'icon': '🪙',
                'description': 'Coinbase exchange wallet',
                'supported': True
            },
            'trust': {
                'name': 'Trust Wallet',
                'icon': '🛡️',
                'description': 'Binance mobile wallet',
                'supported': True
            },
            'phantom': {
                'name': 'Phantom',
                'icon': '👻',
                'description': 'Solana wallet (Ethereum support)',
                'supported': False  # Limited Ethereum support
            }
        }
    
    def _initialize_web3(self):
        """Initialize Web3 connection to Ethereum network"""
        try:
            rpc_url = os.getenv("ETHEREUM_RPC_URL")
            if not rpc_url:
                return
            
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
            
            # Note: PoA middleware removed for compatibility
            
            if self.w3.is_connected():
                self.chain_id = self.w3.eth.chain_id
                self.network_name = self._get_network_name(self.chain_id)
            else:
                pass
                
        except Exception as e:
            pass
    
    def _get_network_name(self, chain_id):
        """Get network name from chain ID"""
        networks = {
            1: "Ethereum Mainnet",
            11155111: "Sepolia Testnet",
            5: "Goerli Testnet",
            137: "Polygon",
            56: "Binance Smart Chain",
            42161: "Arbitrum One"
        }
        return networks.get(chain_id, f"Unknown Network ({chain_id})")
    
    def get_supported_wallets(self):
        """Get list of supported wallets"""
        return {k: v for k, v in self.supported_wallets.items() if v['supported']}
    
    def render_wallet_connection_ui(self):
        """Render wallet connection UI in Streamlit"""
        st.subheader("🔗 Connect Your Wallet")
        
        # Check if already connected
        if self.is_connected():
            self._render_connected_wallet_ui()
            return
        
        # Show wallet options
        st.write("Choose your wallet to connect:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🦊 MetaMask", use_container_width=True):
                self._connect_metamask()
        
        with col2:
            if st.button("🔗 WalletConnect", use_container_width=True):
                self._connect_walletconnect()
        
        # Additional wallet options
        st.write("Other supported wallets:")
        
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button("🪙 Coinbase Wallet", use_container_width=True):
                self._connect_coinbase()
        
        with col4:
            if st.button("🛡️ Trust Wallet", use_container_width=True):
                self._connect_trust()
        
        # Manual connection option
        st.divider()
        st.write("**Manual Connection (Advanced Users):**")
        
        with st.expander("🔧 Manual Wallet Setup"):
            private_key = st.text_input("Private Key (for testing only)", type="password")
            if st.button("Connect with Private Key"):
                if private_key:
                    self._connect_with_private_key(private_key)
                else:
                    st.error("Please enter a private key")
    
    def _render_connected_wallet_ui(self):
        """Render UI for connected wallet"""
        st.success(f"✅ Connected to {self.wallet_type}")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"**Address:** `{self.account_address}`")
            st.write(f"**Network:** {self.network_name}")
        
        with col2:
            if st.button("Disconnect"):
                self.disconnect()
                st.rerun()
        
        # Show wallet actions
        st.subheader("💼 Wallet Actions")
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            if st.button("💰 Check Balance"):
                self._show_balance()
        
        with col4:
            if st.button("📊 View Portfolios"):
                self._show_portfolios()
        
        with col5:
            if st.button("⚙️ Settings"):
                self._show_wallet_settings()
    
    def _connect_metamask(self):
        """Connect to MetaMask wallet"""
        try:
            st.info("🦊 MetaMask Connection")
            st.write("1. Make sure MetaMask is installed in your browser")
            st.write("2. Click 'Connect' in the MetaMask popup")
            st.write("3. Select your account and approve the connection")
            
            # For now, we'll simulate the connection
            # In a real implementation, you'd use web3.js or similar
            if st.button("Simulate MetaMask Connection"):
                self._simulate_wallet_connection("MetaMask")
                
        except Exception as e:
            st.error(f"❌ MetaMask connection failed: {str(e)}")
    
    def _connect_walletconnect(self):
        """Connect to WalletConnect"""
        try:
            st.info("🔗 WalletConnect Connection")
            st.write("1. Scan the QR code with your mobile wallet")
            st.write("2. Approve the connection in your wallet")
            st.write("3. Wait for the connection to establish")
            
            # Generate QR code (placeholder)
            st.write("📱 QR Code would appear here")
            
            if st.button("Simulate WalletConnect"):
                self._simulate_wallet_connection("WalletConnect")
                
        except Exception as e:
            st.error(f"❌ WalletConnect connection failed: {str(e)}")
    
    def _connect_coinbase(self):
        """Connect to Coinbase Wallet"""
        try:
            st.info("🪙 Coinbase Wallet Connection")
            st.write("1. Open Coinbase Wallet app")
            st.write("2. Scan the QR code or use deep link")
            st.write("3. Approve the connection")
            
            if st.button("Simulate Coinbase Connection"):
                self._simulate_wallet_connection("Coinbase Wallet")
                
        except Exception as e:
            st.error(f"❌ Coinbase Wallet connection failed: {str(e)}")
    
    def _connect_trust(self):
        """Connect to Trust Wallet"""
        try:
            st.info("🛡️ Trust Wallet Connection")
            st.write("1. Open Trust Wallet app")
            st.write("2. Go to Settings > WalletConnect")
            st.write("3. Scan the QR code")
            
            if st.button("Simulate Trust Wallet Connection"):
                self._simulate_wallet_connection("Trust Wallet")
                
        except Exception as e:
            st.error(f"❌ Trust Wallet connection failed: {str(e)}")
    
    def _connect_with_private_key(self, private_key):
        """Connect using private key (for testing)"""
        try:
            # Validate private key
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key
            
            account = self.w3.eth.account.from_key(private_key)
            self.account_address = account.address
            self.wallet_type = "Private Key"
            self.connected_wallet = account
            
            st.success(f"✅ Connected with private key")
            st.info(f"**Address:** `{self.account_address}`")
            
        except Exception as e:
            st.error(f"❌ Invalid private key: {str(e)}")
    
    def _simulate_wallet_connection(self, wallet_name):
        """Simulate wallet connection for demo purposes"""
        # Generate a demo address
        demo_address = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
        
        self.account_address = demo_address
        self.wallet_type = wallet_name
        self.connected_wallet = {"address": demo_address, "type": wallet_name}
        
        st.success(f"✅ Successfully connected to {wallet_name}")
        st.info(f"**Demo Address:** `{demo_address}`")
        st.warning("⚠️ This is a simulation. In production, use real wallet connections.")
    
    def is_connected(self):
        """Check if wallet is connected"""
        return self.connected_wallet is not None and self.account_address is not None
    
    def get_account_address(self):
        """Get connected account address"""
        return self.account_address
    
    def get_wallet_type(self):
        """Get connected wallet type"""
        return self.wallet_type
    
    def disconnect(self):
        """Disconnect wallet"""
        self.connected_wallet = None
        self.account_address = None
        self.wallet_type = None
        st.success("✅ Wallet disconnected")
    
    def _show_balance(self):
        """Show wallet balance"""
        if not self.is_connected():
            st.error("❌ No wallet connected")
            return
        
        try:
            balance_wei = self.w3.eth.get_balance(self.account_address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            
            st.metric("💰 ETH Balance", f"{balance_eth:.4f} ETH")
            
            # Show in USD (approximate)
            # You could get real-time ETH price here
            eth_price_usd = 2000  # Placeholder
            balance_usd = float(balance_eth) * eth_price_usd
            
            st.metric("💵 USD Value", f"${balance_usd:.2f}")
            
        except Exception as e:
            st.error(f"❌ Error getting balance: {str(e)}")
    
    def _show_portfolios(self):
        """Show user's portfolios"""
        if not self.is_connected():
            st.error("❌ No wallet connected")
            return
        
        st.info("📊 Portfolio Management")
        st.write("This feature will show your stored portfolios on the blockchain.")
        st.write("Coming soon...")
    
    def _show_wallet_settings(self):
        """Show wallet settings"""
        if not self.is_connected():
            st.error("❌ No wallet connected")
            return
        
        st.info("⚙️ Wallet Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Wallet Type:** {self.wallet_type}")
            st.write(f"**Network:** {self.network_name}")
            st.write(f"**Chain ID:** {self.chain_id}")
        
        with col2:
            st.write(f"**Address:** `{self.account_address}`")
            st.write("**Status:** Connected")
            st.write("**Last Connected:** Now")

# Global wallet manager instance
wallet_manager = MultiWalletManager() 