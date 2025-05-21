# RUGS.FUN Trading Bot

This is a Python bot designed to automate trading in the RUGS.FUN web socket game.

**Disclaimer:**
Building and using bots for online games can be against their Terms of Service. Using such a bot could lead to your account being flagged or banned. This guide is for educational purposes to understand how such a system *could* be built. Proceed at your own risk. Also, financial gambling carries risk of loss.

## Setup

1.  **Clone the repository (if applicable).**
2.  **Create and activate a Python virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    # venv\Scripts\activate
    # On macOS/Linux
    # source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure the bot:**
    *   Open `rugsbot/config.py`.
    *   Update `WEBSOCKET_URI` with the correct WebSocket address for RUGS.FUN (see Phase 2, Step 6 of the guide).
    *   Adjust other parameters like `STAKE_AMOUNT`, `SESSION_PROFIT_TARGET_SOL`, etc., as needed.

## Running the Bot

```bash
python -m rugsbot.bot
```

## Development with OpenAI Codex

This project is structured to potentially be enhanced with OpenAI Codex. You can guide Codex by creating or modifying an `AGENTS.md` file in the root of this repository to instruct it on further development tasks, such as:
*   Refining WebSocket message parsing.
*   Adding new trading strategies.
*   Improving error handling and logging.
*   Writing unit tests. 