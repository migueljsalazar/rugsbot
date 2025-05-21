import json
import pytest

from rugsbot.rugsbot.utils import parse_socketio_message


def test_engine_io_ping():
    assert parse_socketio_message("2") == ("engine_ping", None)


def test_engine_io_pong():
    assert parse_socketio_message("3") == ("engine_pong", None)


def test_engine_io_open():
    frame = '0{"sid":"123abc","upgrades":[],"pingInterval":25000,"pingTimeout":5000}'
    event, payload = parse_socketio_message(frame)
    assert event == "engine_open"
    assert payload == {
        "sid": "123abc",
        "upgrades": [],
        "pingInterval": 25000,
        "pingTimeout": 5000,
    }


def test_socketio_event_message():
    frame = '42["betPlaced",{"amount":0.1,"entryPrice":1.23}]'
    event, payload = parse_socketio_message(frame)
    assert event == "betPlaced"
    assert payload == {"amount": 0.1, "entryPrice": 1.23}


def test_socketio_game_state_update():
    frame = '42["gameStateUpdate",{"price":1.25,"active":true}]'
    event, payload = parse_socketio_message(frame)
    assert event == "gameStateUpdate"
    assert payload == {"price": 1.25, "active": True}


def test_unrecognized_message_returns_none():
    assert parse_socketio_message("foobar") == (None, None)
