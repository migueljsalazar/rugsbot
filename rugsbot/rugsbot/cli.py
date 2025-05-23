"""Command-line interface for the RUGS.FUN Trading Bot."""
import argparse
import asyncio
import logging
import sys
import os
from pathlib import Path

from . import config
from . import bot
from . import dev
from .validators import validate_config, validate_websocket_uri

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO", log_file: str = None):
    """Configure logging with optional file output."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatters
    console_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S"
    )
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # Setup file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        logger.info(f"Logging to file: {log_file}")


def create_sample_env():
    """Create a sample .env file for user configuration."""
    env_content = """# RUGS.FUN Trading Bot Configuration
# Copy this file to .env and update the values

# WebSocket URI - REQUIRED: Get this from RUGS.FUN website
RUGSBOT_WEBSOCKET_URI=PASTE_YOUR_WEBSOCKET_URI_HERE

# Trading Strategy
RUGSBOT_STAKE_AMOUNT=0.01
RUGSBOT_PER_TRADE_PROFIT_MULTIPLIER_TARGET=1.03
RUGSBOT_SESSION_PROFIT_TARGET_SOL=0.05
RUGSBOT_MAX_BUY_WINDOW_SECONDS=5
RUGSBOT_DYNAMIC_BUY_PRICE_CEILING=1.5

# Connection Settings
RUGSBOT_DEFAULT_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36
RUGSBOT_DEFAULT_ORIGIN=https://rugs.fun

# Bot Behavior
RUGSBOT_PING_INTERVAL_SECONDS=25
RUGSBOT_LOG_LEVEL=INFO

# Safety Features
RUGSBOT_DRY_RUN=false
RUGSBOT_MAX_DAILY_LOSS=0.1
RUGSBOT_MAX_CONSECUTIVE_LOSSES=5
"""
    
    env_file = Path(".env.example")
    env_file.write_text(env_content)
    logger.info(f"Created sample configuration file: {env_file}")
    return env_file


async def run_bot(args):
    """Run the trading bot with validation and safety checks."""
    logger.info("🤖 Starting RUGS.FUN Trading Bot...")
    
    # Validate configuration
    if not validate_config():
        logger.error("❌ Configuration validation failed!")
        return 1
    
    # Test WebSocket connection if requested
    if args.test_connection:
        logger.info("🔍 Testing WebSocket connection...")
        if not await validate_websocket_uri(config.WEBSOCKET_URI):
            logger.error("❌ WebSocket connection test failed!")
            return 1
        logger.info("✅ WebSocket connection test passed!")
        if args.test_only:
            return 0
    
    # Show configuration summary
    logger.info("📋 Bot Configuration:")
    logger.info(f"  💰 Stake Amount: {config.STAKE_AMOUNT} SOL")
    logger.info(f"  🎯 Profit Target: {config.PER_TRADE_PROFIT_MULTIPLIER_TARGET}x")
    logger.info(f"  🏆 Session Target: {config.SESSION_PROFIT_TARGET_SOL} SOL")
    logger.info(f"  ⏱️  Buy Window: {config.MAX_BUY_WINDOW_SECONDS}s")
    logger.info(f"  🚧 Price Ceiling: {config.DYNAMIC_BUY_PRICE_CEILING}")
    
    if hasattr(config, 'DRY_RUN') and config.DRY_RUN:
        logger.warning("🧪 DRY RUN MODE - No real trades will be placed!")
    
    try:
        await bot.connect_and_listen()
        return 0
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
        return 0
    except Exception as e:
        logger.error(f"💥 Bot crashed: {e}")
        return 1


def run_dev_tools(args):
    """Run development tools."""
    if args.frames:
        logger.info(f"🔍 Capturing {args.frames} WebSocket frames...")
        dev.main([f"--frames={args.frames}"])
    else:
        dev.main()


def setup_wizard():
    """Interactive setup wizard for first-time users."""
    logger.info("🧙 Welcome to the RUGS.FUN Bot Setup Wizard!")
    
    # Check if .env already exists
    if Path(".env").exists():
        response = input("\n.env file already exists. Overwrite? [y/N]: ")
        if response.lower() != 'y':
            logger.info("Setup cancelled.")
            return
    
    # Get WebSocket URI
    print("\n📡 WebSocket URI Configuration")
    print("You need to get the WebSocket URI from the RUGS.FUN website.")
    print("Look for network requests in browser dev tools when connected to the game.")
    websocket_uri = input("\nEnter WebSocket URI: ").strip()
    
    if not websocket_uri or websocket_uri == "PASTE_YOUR_WEBSOCKET_URI_HERE":
        logger.error("❌ Invalid WebSocket URI provided!")
        return
    
    # Get trading parameters
    print("\n💰 Trading Configuration")
    stake_amount = input("Stake amount per trade (SOL) [0.01]: ").strip() or "0.01"
    profit_target = input("Profit target multiplier [1.03]: ").strip() or "1.03"
    session_target = input("Session profit target (SOL) [0.05]: ").strip() or "0.05"
    
    # Create .env file
    env_content = f"""# RUGS.FUN Trading Bot Configuration
RUGSBOT_WEBSOCKET_URI={websocket_uri}
RUGSBOT_STAKE_AMOUNT={stake_amount}
RUGSBOT_PER_TRADE_PROFIT_MULTIPLIER_TARGET={profit_target}
RUGSBOT_SESSION_PROFIT_TARGET_SOL={session_target}
RUGSBOT_MAX_BUY_WINDOW_SECONDS=5
RUGSBOT_DYNAMIC_BUY_PRICE_CEILING=1.5
RUGSBOT_LOG_LEVEL=INFO
"""
    
    Path(".env").write_text(env_content)
    logger.info("✅ Configuration saved to .env file!")
    logger.info("🚀 You can now run the bot with: python -m rugsbot.cli run")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="RUGS.FUN Trading Bot CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s setup                     # Run setup wizard
  %(prog)s run                       # Start the trading bot
  %(prog)s run --test-connection     # Test connection before starting
  %(prog)s dev --frames 50          # Capture 50 WebSocket frames
  %(prog)s create-env               # Create sample .env file
        """
    )
    
    # Global options
    parser.add_argument("--log-level", default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Set logging level")
    parser.add_argument("--log-file", help="Log to file")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Run interactive setup wizard")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Start the trading bot")
    run_parser.add_argument("--test-connection", action="store_true",
                           help="Test WebSocket connection before starting")
    run_parser.add_argument("--test-only", action="store_true",
                           help="Only test connection, don't start bot")
    
    # Dev command
    dev_parser = subparsers.add_parser("dev", help="Development tools")
    dev_parser.add_argument("--frames", type=int, default=30,
                           help="Number of frames to capture")
    
    # Create-env command
    env_parser = subparsers.add_parser("create-env", help="Create sample .env file")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    
    # Handle commands
    if args.command == "setup":
        setup_wizard()
    elif args.command == "run":
        exit_code = asyncio.run(run_bot(args))
        sys.exit(exit_code)
    elif args.command == "dev":
        run_dev_tools(args)
    elif args.command == "create-env":
        create_sample_env()
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 