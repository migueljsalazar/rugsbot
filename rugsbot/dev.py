"""Command-line helper for inspecting the WebSocket stream."""
from .rugsbot.dev import main as _main

def main(argv=None):
    """Entry point wrapper that delegates to :mod:`rugsbot.rugsbot.dev`."""
    _main(argv)

if __name__ == "__main__":
    main()
