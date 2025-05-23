#!/usr/bin/env python3
"""
Installation script for RUGS.FUN Trading Bot.
This script helps users set up the bot with all dependencies.
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if not in_venv:
        print("⚠️  Warning: Not in a virtual environment")
        print("It's recommended to create a virtual environment first:")
        print("  python -m venv venv")
        print("  source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        
        response = input("\nContinue anyway? [y/N]: ")
        if response.lower() != 'y':
            return False
    
    # Install dependencies
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing requirements"):
        return False
    
    return True

def create_sample_config():
    """Create sample configuration files."""
    print("\n📝 Creating sample configuration...")
    
    # Import the CLI module to use its create_sample_env function
    try:
        from rugsbot.cli import create_sample_env
        create_sample_env()
        print("✅ Sample .env.example file created")
        print("💡 Copy .env.example to .env and configure your settings")
        return True
    except ImportError as e:
        print(f"❌ Failed to create sample config: {e}")
        return False

def run_tests():
    """Run the test suite to verify installation."""
    print("\n🧪 Running tests to verify installation...")
    
    if not run_command(f"{sys.executable} -m pytest tests/ -v", "Running test suite"):
        print("⚠️  Some tests failed, but the bot might still work")
        return True  # Don't fail installation for test failures
    
    return True

def setup_cli_commands():
    """Set up convenient CLI commands."""
    print("\n🔧 Setting up CLI commands...")
    
    # Check if we can import the CLI module
    try:
        from rugsbot.cli import main
        print("✅ CLI module is working")
        
        print("\n🎯 You can now use these commands:")
        print("  python -m rugsbot.cli setup     # Run setup wizard")
        print("  python -m rugsbot.cli run       # Start the bot")
        print("  python -m rugsbot.cli dev       # Development tools")
        
        return True
    except ImportError as e:
        print(f"❌ CLI setup failed: {e}")
        return False

def main():
    """Main installation process."""
    print("🤖 RUGS.FUN Trading Bot Installer")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Installation failed at dependency installation")
        sys.exit(1)
    
    # Create sample config
    if not create_sample_config():
        print("\n⚠️  Warning: Could not create sample configuration")
    
    # Run tests
    if not run_tests():
        print("\n⚠️  Warning: Test verification incomplete")
    
    # Setup CLI
    if not setup_cli_commands():
        print("\n⚠️  Warning: CLI setup incomplete")
    
    print("\n" + "=" * 40)
    print("🎉 Installation completed!")
    print("\n📋 Next steps:")
    print("1. Copy .env.example to .env")
    print("2. Edit .env with your WebSocket URI and settings")
    print("3. Run: python -m rugsbot.cli setup")
    print("4. Run: python -m rugsbot.cli run")
    print("\n📖 For help: python -m rugsbot.cli --help")
    print("\n⚠️  Remember: Use at your own risk and start with small amounts!")

if __name__ == "__main__":
    main() 