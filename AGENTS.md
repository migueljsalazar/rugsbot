# Codex Roadmap for RUGS.FUN Trading Bot

## Sprint-0 bootstrap  ─────────────────────────────────────────

### 0.1  Switch secrets & runtime values to `.env`
Goal Load `WEBSOCKET_URI`, stake sizes, etc. from environment (or `.env`) instead of hard-coding.
Deliverables  
• Add `python-dotenv` to `requirements.txt`  
• `config.py` loads anything that starts with `RUGSBOT_` from env and falls back to defaults.  
• Update `README.md` with new section: "Environment variables".

### 0.2  Add "dev-connect" helper CLI
Goal Fast-fail if the URI or headers are wrong and dump the first 30 raw frames for inspection.
Deliverables  
• `rugsbot/dev.py` with `python -m rugsbot.dev --frames 30`  
• Pretty-prints Engine.IO / Socket.IO frame types.  
• Exit codes 0 (on success) or >0 (on failure).

---

## Sprint-1 core protocol hardening  ───────────────────────────

### 1.1  Auto-discover exact event names
Goal Replace the placeholder names in `config.py` with real ones captured from live traffic.
Steps  
1.  Use the CLI from 0.2 to record a full round while you click buy/sell manually.  
2.  Parse the outgoing "42[…placeBet…]" and incoming confirmations.  
3.  Update constants and add a docstring table mapping each constant to a sample payload.

### 1.2  Robust Socket.IO parser
Goal Remove brittle `startswith('42')` logic.  Implement a tiny parser that:
 • Handles the numeric Engine.IO prefix (0,2,3,40,42,…).  
 • Deserialises payload even when binary attachments/counts are included.  
 • Returns `(eio_type, sio_event, data)` tuples.
Acceptance test Unit test feeding known frame strings – see "tests/test_socketio.py".

### 1.3  Graceful reconnect & back-off
Goal If connection drops, the bot should back-off with jitter (max 60 s) and resume.  
Deliverables  
• Exponential back-off helper in `utils.py`.  
• `connect_and_listen()` loop wrapped so the entire bot can run for hours unattended.

---

## Sprint-2 logic correctness  ─────────────────────────────────

### 2.1  Precise profit calculation
Goal Base profit on actual entry/exit price & amount returned by server.  
• If the payload includes fee fields, subtract them.  
• Unit test with a fabricated round: bet 0.02 SOL at 1.00 → sold at 1.05 = +0.001 SOL net.

### 2.2  Stop-loss & rug detection
Goal React immediately when the flag (e.g. `rugged: true` or price → 0) appears.  
• Parameterise `STOP_LOSS_MULTIPLIER` default 0.8.  
• Add optional auto-sell on rug flag.

### 2.3  Session summary & CSV logging
Goal When the bot stops, write `runs/session-YYYYMMDD_HHMMSS.csv`
with columns `timestamp,action,price,amount,balance`.

---

## Sprint-3 ops & DX  ───────────────────────────────────────────

### 3.1  Dockerfile
Goal One-liner run: `docker run -e RUGSBOT_WEBSOCKET_URI=... rugsbot`.
Include multi-stage build (slim final image ~50 MB).

### 3.2  continuous testing
Goal Set up GitHub Actions:
```
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.11'}
      - run: pip install -r requirements.txt
      - run: pytest -q
```

### 3.3  Security / lint
Goal Run `bandit -r rugsbot` and `ruff check .` in CI, fail on high-severity issues.

---

## Stretch  ───────────────────────────────────────────────────

• Telegram / Discord webhook notifications.  
• Configurable multistrategy mode (different ceilings / profit targets).  
• Plug into Codex "ask" tasks: ask the agent to refactor the state machine into a class once all tests pass. 