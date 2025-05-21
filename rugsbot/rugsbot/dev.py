"""Development helper CLI for connecting to RUGS.FUN and dumping raw frames."""
import argparse
import asyncio
import logging
import websockets
import sys

from . import config
from . import utils

logging.basicConfig(level="INFO", format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

async def _dump_frames(num_frames: int) -> int:
    """Connect to ``config.WEBSOCKET_URI`` and print the first ``num_frames`` frames.

    Returns an exit status code.
    """
    try:
        headers = {
            "User-Agent": config.DEFAULT_USER_AGENT,
            "Origin": config.DEFAULT_ORIGIN,
        }
        async with websockets.connect(
            config.WEBSOCKET_URI, extra_headers=headers
        ) as ws:
            for i in range(num_frames):
                msg = await ws.recv()
                event, payload = utils.parse_socketio_message(msg)
                if payload is None:
                    logger.info("%d: %s", i + 1, event if event else msg)
                    print(f"{i+1}: {event if event else msg}")
                else:
                    logger.info("%d: %s %s", i + 1, event, payload)
                    print(f"{i+1}: {event} {payload}")
        return 0
    except Exception as exc:
        logger.error("Error during connection: %s", exc)
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Dump raw Socket.IO frames")
    parser.add_argument("--frames", type=int, default=30, help="Number of frames to capture")
    args = parser.parse_args(argv)

    exit_code = asyncio.run(_dump_frames(args.frames))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
