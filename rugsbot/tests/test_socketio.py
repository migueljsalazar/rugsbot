import pytest
import json
from rugsbot.utils import parse_socketio_message

def test_engine_io_ping():
    """Test parsing Engine.IO PING messages"""
    event, payload = parse_socketio_message("2")
    assert event == "engine_ping"
    assert payload is None

def test_engine_io_pong():
    """Test parsing Engine.IO PONG messages"""
    event, payload = parse_socketio_message("3")
    assert event == "engine_pong"
    assert payload is None

def test_engine_io_open():
    """Test parsing Engine.IO OPEN messages"""
    message = '0{"sid":"123abc","upgrades":[],"pingInterval":25000,"pingTimeout":5000}'
    event, payload = parse_socketio_message(message)
    assert event == "engine_open"
    assert payload == {"sid":"123abc","upgrades":[],"pingInterval":25000,"pingTimeout":5000}

def test_socketio_event_message():
    """Test parsing Socket.IO event messages"""
    frame = '42["myEvent", {"foo": "bar"}]'
    event, payload = parse_socketio_message(frame)
    assert event == "myEvent"
    assert payload == {"foo": "bar"}

def test_socketio_game_state_update():
    """Test parsing game state update event"""
    frame = '42["gameStateUpdate",{"price":1.25,"active":true}]'
    event, payload = parse_socketio_message(frame)
    assert event == "gameStateUpdate"
    assert payload == {"price": 1.25, "active": True}

def test_unrecognized_message_returns_none():
    """Test that unrecognized messages return None for both event and payload"""
    event, payload = parse_socketio_message("foobar")
    assert event is None
    assert payload is None 