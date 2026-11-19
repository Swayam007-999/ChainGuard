"""Agent CLI entrypoint for ChainGuard access log tailer."""

import logging
import signal
import sys

from agent.config import config
from agent.detector import AttackDetector
from agent.parser import LogParser
from agent.tailer import LogTailer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (ChainGuard-Agent) %(message)s",
)
logger = logging.getLogger("chainguard-agent")


def main() -> None:
    logger.info("Initializing ChainGuard Log Agent...")
    logger.info("Target log file: %s", config.LOG_FILE_PATH)
    logger.info("Target backend:  %s", config.BACKEND_URL)

    detector = AttackDetector(fingerprint_key=config.FINGERPRINT_KEY)
    parser = LogParser(detector=detector)
    tailer = LogTailer(parser=parser)

    def handle_shutdown(signum, frame):  # type: ignore[no-untyped-def]
        logger.info("Shutdown signal received. Flushing pending events and exiting...")
        tailer.is_running = False
        tailer.flush_batch()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    try:
        tailer.start_tailing()
    except Exception:
        logger.exception("Fatal error in Log Agent tailer")
        sys.exit(1)


if __name__ == "__main__":
    main()
