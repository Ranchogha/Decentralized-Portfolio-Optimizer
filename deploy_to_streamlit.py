#!/usr/bin/env python3
"""
Deployment Helper Script for Streamlit Cloud
Automates the deployment process for the Decentralized Portfolio Optimizer
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_git_status():
    """Check if git is initialized and has changes"""
    try:
        result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            return True
        else:
            print("ℹ️ No changes to commit")
            return False
    except:
        return False

def main():
    print("🚀 Streamlit Cloud Deployment Helper")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ Error: app.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Step 1: Check git status
    print("\n📋 Step 1: Checking Git Status")
    if not Path(".git").exists():
        print("ℹ️ Git not initialized. Initializing...")
        if not run_command("git init", "Initializing git repository"):
            sys.exit(1)
    
    # Step 2: Add all files
    print("\n📋 Step 2: Adding Files to Git")
    if not run_command("git add .", "Adding all files to git"):
        sys.exit(1)
    
    # Step 3: Commit changes
    print("\n📋 Step 3: Committing Changes")
    commit_message = "Deploy to Streamlit Cloud - Decentralized Portfolio Optimizer"
    if not run_command(f'git commit -m "{commit_message}"', "Committing changes"):
        sys.exit(1)
    
    # Step 4: Check remote
    print("\n📋 Step 4: Checking Remote Repository")
    result = subprocess.run("git remote -v", shell=True, capture_output=True, text=True)
    
    if not result.stdout.strip():
        print("⚠️  No remote repository configured.")
        print("\n📝 Next Steps:")
        print("1. Create a GitHub repository at: https://github.com/new")
        print("2. Name it: decentralized-portfolio-optimizer")
        print("3. Make it PUBLIC (required for free Streamlit Cloud)")
        print("4. Run the following commands:")
        print("   git remote add origin https://github.com/YOUR_USERNAME/decentralized-portfolio-optimizer.git")
        print("   git branch -M main")
        print("   git push -u origin main")
        print("\n5. Then deploy to Streamlit Cloud at: https://share.streamlit.io")
    else:
        print("✅ Remote repository found")
        print("\n📝 Next Steps:")
        print("1. Push to GitHub:")
        print("   git push origin main")
        print("\n2. Deploy to Streamlit Cloud:")
        print("   - Go to: https://share.streamlit.io")
        print("   - Connect your GitHub repository")
        print("   - Set main file path to: app.py")
        print("   - Configure environment variables")
    
    print("\n🎯 Deployment Checklist:")
    print("✅ Git repository initialized")
    print("✅ Files added and committed")
    print("⏳ Create GitHub repository (if needed)")
    print("⏳ Push to GitHub")
    print("⏳ Deploy to Streamlit Cloud")
    print("⏳ Configure environment variables")
    
    print("\n📚 For detailed instructions, see: DEPLOYMENT_GUIDE.md")
    print("🌐 Your app will be available at: https://your-app-name.streamlit.app")

if __name__ == "__main__":
    main() 