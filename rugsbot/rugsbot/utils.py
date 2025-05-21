"""
Utility functions for the RUGS.FUN Trading Bot.
"""
import json
import logging

logger = logging.getLogger(__name__)

async def send_socketio_message(websocket, event_name: str, payload: dict):
    """Constructs and sends a Socket.IO message (event type '42')."""
    if not websocket or not websocket.open:
        logger.warning(f"WebSocket not open. Cannot send {event_name}.")
        return

    try:
        message_data = [event_name, payload]
        socketio_message = f"42{json.dumps(message_data)}"
        logger.debug(f"Sending Socket.IO message: {socketio_message}")
        await websocket.send(socketio_message)
        logger.info(f"Sent: Event='{event_name}', Payload={payload}")
    except Exception as e:
        logger.error(f"Error sending Socket.IO message {event_name} with payload {payload}: {e}")

def parse_socketio_message(message: str):
    """
    Parses a Socket.IO message string.
    Returns a tuple (event_name, payload_dict) or (None, None) if parsing fails or not an event.
    Handles Engine.IO PING ('2') and PONG ('3') as special cases, returning (message_type, None).
    """
    if message == '2': # Engine.IO PING from server
        return 'engine_ping', None
    if message == '3': # Engine.IO PONG from server (or our PONG ack)
        return 'engine_pong', None

    if message.startswith('42'): # Socket.IO event message (JSON array)
        try:
            data_str = message[2:] # Remove the '42'
            event_name, payload = json.loads(data_str)
            return event_name, payload
        except json.JSONDecodeError:
            logger.warning(f"Could not decode JSON from Socket.IO message: {message}")
            return None, None
        except ValueError: # If json.loads(data_str) doesn't return a list of 2 elements
             logger.warning(f"Socket.IO message data is not a list of two elements: {data_str}")
             return None, None
    elif message.startswith('0{'): # Engine.IO OPEN message with session info
        try:
            payload = json.loads(message[1:])
            return 'engine_open', payload
        except json.JSONDecodeError:
            logger.warning(f"Could not decode JSON from Engine.IO OPEN message: {message}")
            return None, None
    
    logger.debug(f"Received non-standard message or unhandled Engine.IO message: {message[:50]}...")
    return None, None # Not a recognized Socket.IO event message or Engine.IO PING/PONG/OPEN 