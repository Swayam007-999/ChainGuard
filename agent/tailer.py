"""Log file tailer with log rotation handling, batching, and HTTP push."""

import logging
import os
import time
from typing import Any

import httpx

from agent.config import config
from agent.parser import LogParser

logger = logging.getLogger("chainguard-agent")


class LogTailer:
    """Tails access log, parses lines, batches events, and posts to backend."""

    def __init__(
        self,
        parser: LogParser,
        log_file_path: str | None = None,
        backend_url: str | None = None,
        api_key: str | None = None,
        batch_size: int | None = None,
        batch_interval: float | None = None,
    ) -> None:
        self.parser = parser
        self.log_file_path = log_file_path or config.LOG_FILE_PATH
        self.backend_url = (backend_url or config.BACKEND_URL).rstrip("/")
        self.api_key = api_key or config.CHAINGUARD_API_KEY
        self.batch_size = batch_size or config.BATCH_SIZE
        self.batch_interval = batch_interval or config.BATCH_INTERVAL_SECONDS
        self.batch: list[dict[str, Any]] = []
        self.last_flush_time = time.time()
        self.is_running = False

    def process_line(self, line: str) -> dict[str, Any] | None:
        """Parse line and append to active batch if valid."""
        event = self.parser.parse_line(line)
        if event:
            self.batch.append(event)
            if len(self.batch) >= self.batch_size:
                self.flush_batch()
        return event

    def flush_batch(self) -> bool:
        """Send pending events in batch to backend with retry backoff."""
        if not self.batch:
            return True

        to_send = list(self.batch)
        self.batch.clear()
        self.last_flush_time = time.time()

        url = f"{self.backend_url}/events/batch"
        headers = {
            "Content-Type": "application/json",
            "X-ChainGuard-Key": self.api_key,
        }
        payload = {"events": to_send}

        success = False
        for attempt in range(config.MAX_RETRIES):
            try:
                with httpx.Client(timeout=5.0) as client:
                    resp = client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        logger.info("Successfully pushed %d events to backend", len(to_send))
                        success = True
                        break
                    logger.warning(
                        "Backend rejected event batch HTTP %d: %s",
                        resp.status_code,
                        resp.text[:200],
                    )
            except (httpx.RequestError, httpx.HTTPStatusError, OSError) as exc:
                logger.warning(
                    "Failed to ship event batch (attempt %d/%d): %s",
                    attempt + 1,
                    config.MAX_RETRIES,
                    exc,
                )

            time.sleep(0.5 * (2**attempt))

        if not success:
            logger.error("Dropping %d events after exhausting retries", len(to_send))

        return success

    def run_once(self) -> None:
        """Periodic tick to flush batch if interval elapsed."""
        if self.batch and (time.time() - self.last_flush_time >= self.batch_interval):
            self.flush_batch()

    def start_tailing(self, stop_after_seconds: float | None = None) -> None:
        """Continuously tail log file, handling log rotation gracefully."""
        self.is_running = True
        start_time = time.time()

        while not os.path.exists(self.log_file_path) and self.is_running:
            logger.info("Waiting for log file to appear at %s...", self.log_file_path)
            time.sleep(1.0)
            if stop_after_seconds and (time.time() - start_time >= stop_after_seconds):
                return

        with open(self.log_file_path, "r", encoding="utf-8", errors="replace") as f:
            # Seek to end on startup
            f.seek(0, os.SEEK_END)
            last_pos = f.tell()

            while self.is_running:
                current_size = os.path.getsize(self.log_file_path)
                if current_size < last_pos:
                    # File was truncated or rotated: rewind to start
                    logger.info("Log file rotation detected (size shrunk). Rewinding.")
                    f.seek(0, os.SEEK_SET)

                line = f.readline()
                if line:
                    self.process_line(line)
                    last_pos = f.tell()
                else:
                    self.run_once()
                    time.sleep(0.2)

                if stop_after_seconds and (time.time() - start_time >= stop_after_seconds):
                    break

        self.flush_batch()
