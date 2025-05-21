import pytest

from rugsbot.utils import parse_socketio_message


def test_engine_ping():
    event, payload = parse_socketio_message("2")
    assert event == "engine_ping"
    assert payload is None


def test_engine_pong():
    event, payload = parse_socketio_message("3")
    assert event == "engine_pong"
    assert payload is None


def test_socketio_event_frame():
    message = '42["myEvent", {"foo": "bar"}]'
    event, payload = parse_socketio_message(message)
    assert event == "myEvent"
    assert payload == {"foo": "bar"}


def test_engine_open():
    message = '0{"sid":"abc123","pingInterval":25000}'
    event, payload = parse_socketio_message(message)
    assert event == "engine_open"
    assert payload == {"sid": "abc123", "pingInterval": 25000}


def test_invalid_message_returns_none():
    event, payload = parse_socketio_message("42notjson")
    assert event is None
    assert payload is None
