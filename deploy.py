#!/usr/bin/env python3
"""
Deployment script for Decentralized Portfolio Optimizer
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_api_connectivity():
    """Test CoinGecko API connectivity"""
    print("🔍 Testing CoinGecko API connectivity...")
    try:
        response = requests.get("https://api.coingecko.com/api/v3/ping", timeout=10)
        if response.status_code == 200:
            print("✅ CoinGecko API is accessible")
            return True
        else:
            print(f"⚠️ CoinGecko API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to CoinGecko API: {e}")
        return False

def setup_environment():
    """Setup environment variables"""
    print("🔧 Setting up environment...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file...")
        with open(env_file, "w") as f:
            f.write("# CoinGecko API Configuration\n")
            f.write("COINGECKO_API_KEY=your_api_key_here\n\n")
            f.write("# Ethereum Network Configuration\n")
            f.write("ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID\n\n")
            f.write("# Smart Contract Configuration\n")
            f.write("CONTRACT_ADDRESS=0xd0214254f898F8855C73Bd1bBD080Cb5a06A131e\n\n")
            f.write("# Private Key for Blockchain Transactions\n")
            f.write("PRIVATE_KEY=your_private_key_here\n\n")
            f.write("# Application Configuration\n")
            f.write("DEBUG=true\n")
            f.write("LOG_LEVEL=INFO\n")
        print("✅ .env file created")
    else:
        print("✅ .env file already exists")

def check_streamlit():
    """Check if Streamlit is properly installed"""
    print("🔍 Checking Streamlit installation...")
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} is installed")
        return True
    except ImportError:
        print("❌ Streamlit is not installed")
        return False

def run_application():
    """Run the Streamlit application"""
    print("🚀 Starting Decentralized Portfolio Optimizer...")
    print("📱 The application will be available at: http://localhost:8501")
    print("🔄 Press Ctrl+C to stop the application")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")

def main():
    """Main deployment function"""
    print("🚀 Decentralized Portfolio Optimizer - Deployment Script")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check Streamlit
    if not check_streamlit():
        print("❌ Streamlit installation failed")
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Check API connectivity
    if not check_api_connectivity():
        print("⚠️ API connectivity issues detected, but continuing...")
    
    print("\n" + "=" * 60)
    print("✅ Deployment completed successfully!")
    print("📋 Next steps:")
    print("   1. Configure your .env file with API keys")
    print("   2. Run: python deploy.py --start")
    print("   3. Open http://localhost:8501 in your browser")
    print("=" * 60)
    
    # Check if user wants to start the application
    if len(sys.argv) > 1 and sys.argv[1] == "--start":
        run_application()

if __name__ == "__main__":
    main() 