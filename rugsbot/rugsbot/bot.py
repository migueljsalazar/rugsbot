"""
Core logic for the RUGS.FUN Trading Bot.
"""
import websockets
import asyncio
import json
import time
import logging

from . import config
from . import utils

# --- Initialize Logger ---
logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


# --- Bot State Variables ---
# These are global for simplicity in this single-file structure example.
# For more complex bots, consider encapsulating state within a class.
session_profit_accumulator = 0.0
is_bet_active = False
current_bet_entry_price = 0.0
current_bet_id = None # Optional: if the game assigns IDs to bets
game_start_time = 0 # Timestamp of when the current active round started
last_ping_time = 0 # To manage client-side PING if necessary

async def handle_game_state_update(websocket, payload):
    """Handles logic for 'gameStateUpdate' events."""
    global is_bet_active, game_start_time, current_bet_entry_price

    price = payload.get("price", 0.0)
    tick = payload.get("tick", 0)
    game_is_active_round = payload.get("active", False)
    # rugged = payload.get("rugged", False) # Assuming a 'rugged' field might appear

    logger.info(f"Game Update: Price={price:.8f}, Tick={tick}, Active={game_is_active_round}")

    current_time = time.time()

    if game_is_active_round and not getattr(handle_game_state_update, "round_started_logged", False):
        game_start_time = current_time
        logger.info(f"New round started at {game_start_time}")
        handle_game_state_update.round_started_logged = True
    elif not game_is_active_round:
        handle_game_state_update.round_started_logged = False # Reset for next round

    # --- Dynamic Buy Logic ---
    if game_is_active_round and not is_bet_active:
        elapsed_time_in_round = current_time - game_start_time
        if elapsed_time_in_round <= config.MAX_BUY_WINDOW_SECONDS:
            if price <= config.DYNAMIC_BUY_PRICE_CEILING: # Ensure this condition is meaningful for the game
                logger.info(f"BUY CONDITION MET: Price {price:.8f} <= {config.DYNAMIC_BUY_PRICE_CEILING}, Time {elapsed_time_in_round:.2f}s")
                bet_payload = {
                    "amount": config.STAKE_AMOUNT,
                    "autoSellMultiplier": None, # We handle sell logic manually
                    "stopLossMultiplier": None  # We handle sell logic manually
                }
                await utils.send_socketio_message(websocket, config.SOCKETIO_EVENT_PLACE_BET, bet_payload)
                # is_bet_active will be set to True upon receiving "betPlaced" confirmation
            else:
                logger.debug(f"Buy condition not met: Price {price:.8f} > ceiling {config.DYNAMIC_BUY_PRICE_CEILING}")
        else:
            logger.debug(f"Buy condition not met: Elapsed time {elapsed_time_in_round:.2f}s > window {config.MAX_BUY_WINDOW_SECONDS}s")

    # --- Sell Logic ---
    if game_is_active_round and is_bet_active and current_bet_entry_price > 0:
        # if rugged:
        #     logger.warning(f"RUGGED DETECTED! Attempting to sell immediately.")
        #     await utils.send_socketio_message(websocket, config.SOCKETIO_EVENT_SELL_BET, {"percentage": 100})
        #     return # Exit after sell attempt

        current_profit_multiplier = price / current_bet_entry_price
        logger.debug(f"Active Bet: Entry={current_bet_entry_price:.8f}, Current Price={price:.8f}, Target Multiplier={config.PER_TRADE_PROFIT_MULTIPLIER_TARGET}, Current Multiplier={current_profit_multiplier:.4f}")
        if current_profit_multiplier >= config.PER_TRADE_PROFIT_MULTIPLIER_TARGET:
            logger.info(f"SELL CONDITION MET: Profit Multiplier {current_profit_multiplier:.4f} >= {config.PER_TRADE_PROFIT_MULTIPLIER_TARGET}")
            await utils.send_socketio_message(websocket, config.SOCKETIO_EVENT_SELL_BET, {"percentage": 100})
            # is_bet_active will be set to False upon receiving "betSold" or "betLost" confirmation

async def connect_and_listen():
    """Connects to the WebSocket and handles incoming messages and bot logic."""
    global session_profit_accumulator, is_bet_active, current_bet_entry_price, current_bet_id, last_ping_time

    custom_headers = {
        "User-Agent": config.DEFAULT_USER_AGENT,
        "Origin": config.DEFAULT_ORIGIN
        # Add any other necessary headers, e.g., Authorization, Cookie, if required by RUGS.FUN
    }

    logger.info(f"Attempting to connect to WebSocket: {config.WEBSOCKET_URI}")
    try:
        async with websockets.connect(config.WEBSOCKET_URI, extra_headers=custom_headers) as websocket:
            logger.info("Successfully connected to WebSocket!")
            last_ping_time = time.time()

            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=config.PING_INTERVAL_SECONDS + 5) # Timeout slightly longer than ping interval
                    event_name, payload = utils.parse_socketio_message(message)

                    if event_name == 'engine_ping':
                        logger.debug("Received Engine.IO PING, sending PONG.")
                        await websocket.send('3') # Send Engine.IO PONG
                        last_ping_time = time.time()
                        continue
                    elif event_name == 'engine_pong':
                        logger.debug("Received Engine.IO PONG.")
                        last_ping_time = time.time() # Update time on received PONG too
                        continue
                    elif event_name == 'engine_open':
                        logger.info(f"Engine.IO connection opened: {payload}")
                        # sid = payload.get('sid') # Session ID, might be useful
                        # PING_INTERVAL_SECONDS = payload.get('pingInterval', 25000) / 1000 # Server might dictate ping interval
                        # config.PING_TIMEOUT_SECONDS = payload.get('pingTimeout', 20000) / 1000
                        continue

                    if not event_name:
                        if message: #If parse_socketio_message returned (None,None) but there was a message string
                            logger.debug(f"Received unhandled message: {message[:100]}...")
                        continue # Skip if not a recognized event or type

                    logger.debug(f"Received Event: '{event_name}', Payload: {payload if payload else 'N/A'}")

                    if event_name == config.SOCKETIO_EVENT_GAME_STATE_UPDATE:
                        await handle_game_state_update(websocket, payload)
                    
                    elif event_name == config.SOCKETIO_EVENT_BET_PLACED:
                        # IMPORTANT: Confirm the structure of this payload from RUGS.FUN
                        # This is a guess based on common patterns.
                        is_bet_active = True
                        # Assuming the payload directly contains the entry price of our bet.
                        # If not, we might need to use the price from the gameStateUpdate at the time of betting.
                        # Or, the server might send a more detailed bet object.
                        actual_entry_price = payload.get("entryPrice", payload.get("price", current_bet_entry_price))
                        bet_amount = payload.get("amount", config.STAKE_AMOUNT)
                        
                        if actual_entry_price: # Ensure we got an entry price
                            current_bet_entry_price = actual_entry_price
                        else:
                            logger.warning("'betPlaced' confirmation received, but no entry price found in payload. Using last known price.")
                            # This might be inaccurate; ideally, the server provides the executed price.

                        current_bet_id = payload.get("id", current_bet_id) # Update bet ID if provided
                        logger.info(f"BET PLACED: Amount={bet_amount}, Entry Price={current_bet_entry_price:.8f}, Bet ID={current_bet_id}")

                    elif event_name == config.SOCKETIO_EVENT_BET_SOLD:
                        # IMPORTANT: Confirm the structure of this payload from RUGS.FUN
                        payout = payload.get("payout", 0.0)
                        # profit = payload.get("profit") # Alternative, if server sends profit directly
                        # If server sends profit directly, use it. Otherwise, calculate from payout and stake.
                        # This assumes payout includes the initial stake.
                        trade_profit = payout - config.STAKE_AMOUNT 
                        
                        session_profit_accumulator += trade_profit
                        is_bet_active = False
                        logger.info(f"BET SOLD: Payout={payout:.8f}, Trade Profit={trade_profit:.8f}, Session Profit={session_profit_accumulator:.8f}")
                        current_bet_entry_price = 0 # Reset for next bet
                        current_bet_id = None

                        if session_profit_accumulator >= config.SESSION_PROFIT_TARGET_SOL:
                            logger.info(f"SESSION PROFIT TARGET REACHED: {session_profit_accumulator:.8f} >= {config.SESSION_PROFIT_TARGET_SOL}. Stopping bot.")
                            break # Exit the main listening loop

                    elif event_name == config.SOCKETIO_EVENT_BET_LOST:
                        # IMPORTANT: Confirm the structure of this payload from RUGS.FUN
                        # This event might occur on a rug pull or if a bet is liquidated by the game mechanics
                        lost_amount = payload.get("amount", config.STAKE_AMOUNT) # Amount lost, usually the stake
                        session_profit_accumulator -= lost_amount # Subtract the stake
                        is_bet_active = False
                        logger.info(f"BET LOST: Amount Lost={lost_amount:.8f}, Session Profit={session_profit_accumulator:.8f}")
                        current_bet_entry_price = 0 # Reset for next bet
                        current_bet_id = None
                        # Check session target again, in case of losses (though less likely to hit target via loss)
                        if session_profit_accumulator >= config.SESSION_PROFIT_TARGET_SOL:
                            logger.info(f"SESSION PROFIT TARGET REACHED (unexpectedly after loss): {session_profit_accumulator:.8f} >= {config.SESSION_PROFIT_TARGET_SOL}. Stopping bot.")
                            break

                    # Optional: Client-side PING if server doesn't send PINGs or expects them more frequently
                    # current_time = time.time()
                    # if (current_time - last_ping_time) > config.PING_INTERVAL_SECONDS:
                    #     await websocket.send('2') # Send Engine.IO PING
                    #     last_ping_time = current_time
                    #     logger.debug("Sent client-side Engine.IO PING")

                except asyncio.TimeoutError:
                    logger.warning(f"WebSocket receive timeout after {config.PING_INTERVAL_SECONDS + 5}s. No message from server (or PING).")
                    # Consider sending a PING here if the server might have just gone quiet
                    current_time = time.time()
                    if (current_time - last_ping_time) > config.PING_INTERVAL_SECONDS: # Check if we haven't PINGed recently
                        logger.info("Timeout, sending PING to check connection.")
                        await websocket.send('2') # Send Engine.IO PING
                        last_ping_time = time.time()
                    # If this happens repeatedly, the connection might be dead. The `async with` block will eventually exit.
                except websockets.exceptions.ConnectionClosedOK:
                    logger.info("WebSocket connection closed normally.")
                    break
                except websockets.exceptions.ConnectionClosedError as e:
                    logger.error(f"WebSocket connection closed with error: {e}")
                    break
                except Exception as e:
                    logger.exception(f"Error in WebSocket loop: {e}")
                    await asyncio.sleep(1) # Avoid rapid looping on persistent error

            logger.info("Exited WebSocket listening loop.")

    except websockets.exceptions.InvalidURI:
        logger.error(f"Invalid WebSocket URI: {config.WEBSOCKET_URI}. Please check config.py.")
    except websockets.exceptions.WebSocketException as e:
        logger.error(f"Failed to connect to WebSocket: {e}")
    except ConnectionRefusedError:
        logger.error(f"Connection refused by the server for URI: {config.WEBSOCKET_URI}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred during connection or setup: {e}")
    finally:
        logger.info("Bot shutting down.")

if __name__ == "__main__":
    logger.info("Starting RUGS.FUN Bot...")
    try:
        asyncio.run(connect_and_listen())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (KeyboardInterrupt).")
    except Exception as e:
        logger.critical(f"Unhandled exception at top level: {e}", exc_info=True)
    finally:
        logger.info("RUGS.FUN Bot has finished execution.") 