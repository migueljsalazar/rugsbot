# RUGS.FUN Trading Bot 🤖

An automated trading bot for the RUGS.FUN Socket.IO-based trading game. This bot implements intelligent trading strategies with comprehensive safety features and risk management.

**⚠️ IMPORTANT DISCLAIMER:**
- This bot is for educational purposes only
- Trading/gambling carries significant risk of loss
- Using bots may violate RUGS.FUN Terms of Service
- Start with very small amounts to test
- Use at your own risk!

## ✨ Features

- 🚀 **Easy Setup**: Interactive setup wizard
- 🛡️ **Safety First**: Built-in risk management and stop-losses
- 🧪 **Dry Run Mode**: Test strategies without real money
- 📊 **Performance Tracking**: Detailed statistics and logging
- 🔄 **Auto-Reconnection**: Robust connection handling
- ⚙️ **Flexible Configuration**: Environment variables and .env files
- 🔍 **Development Tools**: WebSocket frame inspection
- 🧪 **Comprehensive Tests**: Unit tests for all components

## 🚀 Quick Start

### 1. Installation

**Option A: Automatic Installation (Recommended)**
```bash
git clone <your-repository-url>
cd rugsbot
python install.py
```

**Option B: Manual Installation**
```bash
git clone <your-repository-url>
cd rugsbot

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

**Interactive Setup (Easiest)**
```bash
python -m rugsbot.cli setup
```

**Manual Configuration**
```bash
# Create configuration file
python -m rugsbot.cli create-env
cp .env.example .env
# Edit .env with your settings
```

### 3. Get WebSocket URI

1. Open RUGS.FUN in your browser
2. Open Developer Tools (F12)
3. Go to Network tab
4. Connect to the game
5. Look for WebSocket connections (ws:// or wss://)
6. Copy the WebSocket URI

### 4. Run the Bot

**Test Connection First**
```bash
python -m rugsbot.cli run --test-connection
```

**Start Trading**
```bash
python -m rugsbot.cli run
```

**Dry Run Mode (Recommended for testing)**
```bash
# Set RUGSBOT_DRY_RUN=true in .env file
python -m rugsbot.cli run
```

## 📋 Configuration Options

All settings can be configured via environment variables or `.env` file:

### Core Settings
```bash
# REQUIRED: WebSocket URI from RUGS.FUN
RUGSBOT_WEBSOCKET_URI=ws://example.com/socket.io/

# Trading Strategy
RUGSBOT_STAKE_AMOUNT=0.01                           # SOL per trade
RUGSBOT_PER_TRADE_PROFIT_MULTIPLIER_TARGET=1.03     # 3% profit target
RUGSBOT_SESSION_PROFIT_TARGET_SOL=0.05              # Session profit goal
RUGSBOT_MAX_BUY_WINDOW_SECONDS=5                    # Buy window timing
RUGSBOT_DYNAMIC_BUY_PRICE_CEILING=1.5               # Max buy price

# Safety Features
RUGSBOT_DRY_RUN=false                               # Simulate trades only
RUGSBOT_MAX_DAILY_LOSS=0.1                         # Daily loss limit
RUGSBOT_MAX_CONSECUTIVE_LOSSES=5                    # Consecutive loss limit
RUGSBOT_STOP_LOSS_MULTIPLIER=0.9                   # Stop loss at 90%
RUGSBOT_MAX_POSITION_TIME_SECONDS=300               # Max hold time (5 min)

# Logging & Connection
RUGSBOT_LOG_LEVEL=INFO                              # DEBUG, INFO, WARNING, ERROR
RUGSBOT_PING_INTERVAL_SECONDS=25                    # Connection keep-alive
```

### Advanced Settings
```bash
# Reconnection
RUGSBOT_MAX_RECONNECTION_ATTEMPTS=5
RUGSBOT_RECONNECTION_DELAY_SECONDS=5
RUGSBOT_EXPONENTIAL_BACKOFF=true

# Connection Headers
RUGSBOT_DEFAULT_USER_AGENT=Mozilla/5.0...
RUGSBOT_DEFAULT_ORIGIN=https://rugs.fun

# Socket.IO Events (adjust if RUGS.FUN changes)
RUGSBOT_SOCKETIO_EVENT_PLACE_BET=placeBet
RUGSBOT_SOCKETIO_EVENT_SELL_BET=sellBet
RUGSBOT_SOCKETIO_EVENT_GAME_STATE_UPDATE=gameStateUpdate
```

## 🛠️ CLI Commands

```bash
# Setup and Configuration
python -m rugsbot.cli setup                    # Interactive setup wizard
python -m rugsbot.cli create-env              # Create sample .env file

# Running the Bot
python -m rugsbot.cli run                     # Start trading
python -m rugsbot.cli run --test-connection   # Test connection first
python -m rugsbot.cli run --test-only         # Only test, don't trade

# Development Tools
python -m rugsbot.cli dev --frames 50         # Capture WebSocket frames
python -m rugsbot.dev --frames 30             # Alternative dev command

# Logging
python -m rugsbot.cli run --log-level DEBUG   # Verbose logging
python -m rugsbot.cli run --log-file bot.log  # Log to file
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_socketio.py -v

# Test with coverage
python -m pytest tests/ --cov=rugsbot --cov-report=html
```

## 🛡️ Safety Features

### Risk Management
- **Daily Loss Limits**: Automatic stop when daily losses exceed threshold
- **Consecutive Loss Protection**: Stop after too many losses in a row
- **Stop Loss Orders**: Automatic sell at 90% of entry price (configurable)
- **Position Time Limits**: Force close positions after maximum hold time
- **Emergency Stop**: Manual or automatic emergency shutdown

### Dry Run Mode
- Test strategies without real money
- Full simulation of trading logic
- Performance tracking and statistics
- Perfect for strategy development

### Connection Safety
- Automatic reconnection with exponential backoff
- Connection health monitoring
- Graceful error handling
- WebSocket validation before trading

## 📊 Monitoring and Logging

### Real-time Statistics
- Win/loss ratios
- Profit/loss tracking
- Trade performance metrics
- Session summaries

### Logging Levels
- **DEBUG**: Detailed technical information
- **INFO**: General operation status
- **WARNING**: Potential issues
- **ERROR**: Critical problems

### Log Formats
```
2025-01-XX 10:30:15 - INFO - 🤖 Starting RUGS.FUN Trading Bot...
2025-01-XX 10:30:16 - INFO - ✅ Configuration validation passed
2025-01-XX 10:30:17 - INFO - 📋 Bot Configuration:
2025-01-XX 10:30:18 - INFO - 💰 Trade started - Entry: 1.234567, Stake: 0.010000
2025-01-XX 10:30:25 - INFO - ✅ Trade PROFIT: 0.000300 SOL (1.030x) in 7.2s
```

## 🔧 Development

### Project Structure
```
rugsbot/
├── rugsbot/
│   ├── __init__.py
│   ├── bot.py           # Main trading logic
│   ├── cli.py           # Command-line interface
│   ├── config.py        # Configuration management
│   ├── dev.py           # Development tools
│   ├── safety.py        # Risk management
│   ├── utils.py         # Socket.IO utilities
│   └── validators.py    # Configuration validation
├── tests/
│   └── test_socketio.py # Unit tests
├── requirements.txt     # Dependencies
├── install.py          # Installation script
└── README.md           # This file
```

### Adding Custom Strategies
1. Extend the `handle_game_state_update` function in `bot.py`
2. Add new configuration options in `config.py`
3. Implement safety checks in `safety.py`
4. Add tests in `tests/`

### Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📈 Trading Strategies

### Current Strategy: Momentum Following
- Buy within first N seconds of a round
- Sell at 3% profit target (configurable)
- Stop loss at 90% of entry (configurable)
- Price ceiling protection

### Strategy Customization
Modify these settings to adjust strategy:
- `PER_TRADE_PROFIT_MULTIPLIER_TARGET`: Profit target
- `MAX_BUY_WINDOW_SECONDS`: Entry timing
- `DYNAMIC_BUY_PRICE_CEILING`: Entry price limit
- `STOP_LOSS_MULTIPLIER`: Loss protection

## ❓ Troubleshooting

### Common Issues

**"WebSocket URI not configured"**
- Set `RUGSBOT_WEBSOCKET_URI` in your `.env` file
- Get the URI from RUGS.FUN browser dev tools

**"Connection refused"**
- Check if RUGS.FUN is accessible
- Verify WebSocket URI is correct
- Check firewall/proxy settings

**"Module not found" errors**
- Run from the correct directory
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**Bot not placing trades**
- Check if dry run mode is enabled
- Verify safety limits aren't triggered
- Check trading conditions in logs

### Debug Mode
```bash
python -m rugsbot.cli run --log-level DEBUG
```

### Connection Testing
```bash
python -m rugsbot.cli run --test-only
```

## 📞 Support

- Check logs for detailed error information
- Run tests to verify installation
- Use dry run mode to test safely
- Start with very small stake amounts

## 📄 License

This project is for educational purposes only. Use at your own risk.

---

**Remember: Never risk more than you can afford to lose! 🎯** 