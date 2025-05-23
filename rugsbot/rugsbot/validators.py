"""Configuration and connection validators for the RUGS.FUN Trading Bot."""
import asyncio
import logging
import websockets
from typing import Dict, List, Tuple
from urllib.parse import urlparse

from . import config

logger = logging.getLogger(__name__)


def validate_config() -> bool:
    """Validate bot configuration settings.
    
    Returns:
        bool: True if configuration is valid, False otherwise
    """
    errors = []
    warnings = []
    
    # Validate WebSocket URI
    if not config.WEBSOCKET_URI or config.WEBSOCKET_URI == "PASTE_YOUR_WEBSOCKET_URI_HERE":
        errors.append("WebSocket URI is not configured. Please set RUGSBOT_WEBSOCKET_URI")
    else:
        try:
            parsed = urlparse(config.WEBSOCKET_URI)
            if not parsed.scheme in ['ws', 'wss']:
                errors.append(f"WebSocket URI must use ws:// or wss:// scheme, got: {parsed.scheme}")
            if not parsed.netloc:
                errors.append("WebSocket URI must include a hostname")
        except Exception as e:
            errors.append(f"Invalid WebSocket URI format: {e}")
    
    # Validate trading parameters
    if not isinstance(config.STAKE_AMOUNT, (int, float)) or config.STAKE_AMOUNT <= 0:
        errors.append(f"STAKE_AMOUNT must be a positive number, got: {config.STAKE_AMOUNT}")
    
    if not isinstance(config.PER_TRADE_PROFIT_MULTIPLIER_TARGET, (int, float)) or config.PER_TRADE_PROFIT_MULTIPLIER_TARGET <= 1.0:
        errors.append(f"PER_TRADE_PROFIT_MULTIPLIER_TARGET must be > 1.0, got: {config.PER_TRADE_PROFIT_MULTIPLIER_TARGET}")
    
    if not isinstance(config.SESSION_PROFIT_TARGET_SOL, (int, float)) or config.SESSION_PROFIT_TARGET_SOL <= 0:
        errors.append(f"SESSION_PROFIT_TARGET_SOL must be positive, got: {config.SESSION_PROFIT_TARGET_SOL}")
    
    if not isinstance(config.MAX_BUY_WINDOW_SECONDS, (int, float)) or config.MAX_BUY_WINDOW_SECONDS <= 0:
        errors.append(f"MAX_BUY_WINDOW_SECONDS must be positive, got: {config.MAX_BUY_WINDOW_SECONDS}")
    
    if not isinstance(config.DYNAMIC_BUY_PRICE_CEILING, (int, float)) or config.DYNAMIC_BUY_PRICE_CEILING <= 0:
        errors.append(f"DYNAMIC_BUY_PRICE_CEILING must be positive, got: {config.DYNAMIC_BUY_PRICE_CEILING}")
    
    # Validate timing parameters
    if not isinstance(config.PING_INTERVAL_SECONDS, (int, float)) or config.PING_INTERVAL_SECONDS <= 0:
        errors.append(f"PING_INTERVAL_SECONDS must be positive, got: {config.PING_INTERVAL_SECONDS}")
    
    # Validate string parameters
    if not config.DEFAULT_USER_AGENT:
        warnings.append("DEFAULT_USER_AGENT is empty, this might cause connection issues")
    
    if not config.DEFAULT_ORIGIN:
        warnings.append("DEFAULT_ORIGIN is empty, this might cause connection issues")
    
    # Check for reasonable values
    if config.STAKE_AMOUNT > 1.0:
        warnings.append(f"STAKE_AMOUNT is quite high ({config.STAKE_AMOUNT} SOL). Consider starting smaller.")
    
    if config.PER_TRADE_PROFIT_MULTIPLIER_TARGET > 2.0:
        warnings.append(f"Profit target is quite ambitious ({config.PER_TRADE_PROFIT_MULTIPLIER_TARGET}x). Consider more conservative targets.")
    
    if config.MAX_BUY_WINDOW_SECONDS > 30:
        warnings.append(f"Buy window is quite long ({config.MAX_BUY_WINDOW_SECONDS}s). This might miss early opportunities.")
    
    # Check for safety features
    if hasattr(config, 'MAX_DAILY_LOSS'):
        if not isinstance(config.MAX_DAILY_LOSS, (int, float)) or config.MAX_DAILY_LOSS <= 0:
            errors.append(f"MAX_DAILY_LOSS must be positive, got: {config.MAX_DAILY_LOSS}")
    
    if hasattr(config, 'MAX_CONSECUTIVE_LOSSES'):
        if not isinstance(config.MAX_CONSECUTIVE_LOSSES, int) or config.MAX_CONSECUTIVE_LOSSES <= 0:
            errors.append(f"MAX_CONSECUTIVE_LOSSES must be a positive integer, got: {config.MAX_CONSECUTIVE_LOSSES}")
    
    # Display results
    if warnings:
        logger.warning("⚠️  Configuration Warnings:")
        for warning in warnings:
            logger.warning(f"  • {warning}")
    
    if errors:
        logger.error("❌ Configuration Errors:")
        for error in errors:
            logger.error(f"  • {error}")
        return False
    
    logger.info("✅ Configuration validation passed")
    return True


async def validate_websocket_uri(uri: str, timeout: float = 10.0) -> bool:
    """Test WebSocket connection to verify URI is working.
    
    Args:
        uri: WebSocket URI to test
        timeout: Connection timeout in seconds
        
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        headers = {
            "User-Agent": config.DEFAULT_USER_AGENT,
            "Origin": config.DEFAULT_ORIGIN
        }
        
        async with asyncio.timeout(timeout):
            async with websockets.connect(uri, extra_headers=headers) as websocket:
                # Try to receive one message to verify the connection is active
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    logger.debug(f"Received test message: {message[:100]}...")
                    return True
                except asyncio.TimeoutError:
                    # No message received, but connection was successful
                    logger.debug("Connection successful but no immediate message received")
                    return True
                    
    except asyncio.TimeoutError:
        logger.error(f"Connection timeout after {timeout}s")
        return False
    except websockets.exceptions.InvalidURI:
        logger.error(f"Invalid WebSocket URI format: {uri}")
        return False
    except websockets.exceptions.WebSocketException as e:
        logger.error(f"WebSocket error: {e}")
        return False
    except ConnectionRefusedError:
        logger.error(f"Connection refused by server")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during connection test: {e}")
        return False


def validate_event_names() -> List[str]:
    """Validate Socket.IO event names are configured.
    
    Returns:
        List of validation warnings
    """
    warnings = []
    
    event_configs = [
        ("SOCKETIO_EVENT_PLACE_BET", config.SOCKETIO_EVENT_PLACE_BET),
        ("SOCKETIO_EVENT_SELL_BET", config.SOCKETIO_EVENT_SELL_BET),
        ("SOCKETIO_EVENT_GAME_STATE_UPDATE", config.SOCKETIO_EVENT_GAME_STATE_UPDATE),
        ("SOCKETIO_EVENT_BET_PLACED", config.SOCKETIO_EVENT_BET_PLACED),
        ("SOCKETIO_EVENT_BET_SOLD", config.SOCKETIO_EVENT_BET_SOLD),
        ("SOCKETIO_EVENT_BET_LOST", config.SOCKETIO_EVENT_BET_LOST),
    ]
    
    for name, value in event_configs:
        if not value:
            warnings.append(f"{name} is empty - bot may not respond to this event type")
        elif not isinstance(value, str):
            warnings.append(f"{name} should be a string, got {type(value)}")
    
    return warnings


def get_config_summary() -> Dict[str, any]:
    """Get a summary of current configuration for display.
    
    Returns:
        Dictionary with configuration summary
    """
    return {
        "websocket_uri_configured": bool(config.WEBSOCKET_URI and config.WEBSOCKET_URI != "PASTE_YOUR_WEBSOCKET_URI_HERE"),
        "stake_amount": config.STAKE_AMOUNT,
        "profit_target": config.PER_TRADE_PROFIT_MULTIPLIER_TARGET,
        "session_target": config.SESSION_PROFIT_TARGET_SOL,
        "buy_window": config.MAX_BUY_WINDOW_SECONDS,
        "price_ceiling": config.DYNAMIC_BUY_PRICE_CEILING,
        "ping_interval": config.PING_INTERVAL_SECONDS,
        "log_level": config.LOG_LEVEL,
        "dry_run": getattr(config, 'DRY_RUN', False),
        "max_daily_loss": getattr(config, 'MAX_DAILY_LOSS', None),
        "max_consecutive_losses": getattr(config, 'MAX_CONSECUTIVE_LOSSES', None),
    } 