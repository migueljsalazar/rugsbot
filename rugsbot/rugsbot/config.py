"""
Configuration settings for the RUGS.FUN Trading Bot.
"""

# --- WebSocket Connection Settings ---
WEBSOCKET_URI = "PASTE_YOUR_WEBSOCKET_URI_HERE"  # Replace with actual RUGS.FUN WebSocket URI
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
DEFAULT_ORIGIN = "https://rugs.fun"  # The domain of the game

# --- Trading Strategy Settings ---
STAKE_AMOUNT = 0.01  # Amount of SOL (or game currency) to bet per trade
PER_TRADE_PROFIT_MULTIPLIER_TARGET = 1.03  # e.g., 1.03 for a 3% profit target on the trade
SESSION_PROFIT_TARGET_SOL = 0.05  # Total SOL profit to aim for before stopping the bot
MAX_BUY_WINDOW_SECONDS = 5  # How many seconds into a new round the bot is allowed to buy
DYNAMIC_BUY_PRICE_CEILING = 1.5  # Don't buy if initial price is already > X (relative to some baseline, or absolute if known)

# --- Socket.IO Event Names (Confirm these with RUGS.FUN actual messages) ---
SOCKETIO_EVENT_PLACE_BET = "placeBet"
SOCKETIO_EVENT_SELL_BET = "sellBet"
SOCKETIO_EVENT_GAME_STATE_UPDATE = "gameStateUpdate"
SOCKETIO_EVENT_BET_PLACED = "betPlaced"        # Confirmation that your bet was accepted
SOCKETIO_EVENT_BET_SOLD = "betSold"          # Confirmation that your bet was sold
SOCKETIO_EVENT_BET_LOST = "betLost"          # Confirmation if a bet is explicitly lost (e.g., rugged)

# --- Bot Behavior Settings ---
PING_INTERVAL_SECONDS = 25 # Interval to send PING to keep connection alive (if server expects client PINGs)
# Note: The provided example code handles server PINGs by sending PONGs.
# This PING_INTERVAL_SECONDS would be for client-initiated PINGs if required.

LOG_LEVEL = "INFO" # Logging level (e.g., DEBUG, INFO, WARNING, ERROR)

# It's good practice to load sensitive data like API keys from environment variables or a .env file
# For this bot, the primary sensitive item is the WebSocket URI if it contains session tokens,
# but usually, the main URI is public, and authentication happens via headers or initial messages if needed. 