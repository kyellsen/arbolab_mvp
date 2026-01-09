"""Pytest fixtures for frontend browser tests."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Generator

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def _get_free_port() -> int:
    """Return an available local port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_for_server(
    base_url: str,
    process: subprocess.Popen[str],
    timeout: float = 30.0,
) -> None:
    """Wait for the server to respond to health checks.

    Args:
        base_url: Base URL for the server.
        process: Running server process.
        timeout: Maximum wait time in seconds.
    """
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=1)
            raise RuntimeError(
                "Server exited early.\n"
                f"stdout:\n{stdout}\n"
                f"stderr:\n{stderr}"
            )
        try:
            with urllib.request.urlopen(f"{base_url}/health", timeout=1) as response:
                if response.status == 200:
                    return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(0.2)
    raise RuntimeError(f"Server did not become ready: {last_error}")


@pytest.fixture(scope="session")
def server_url(tmp_path_factory: pytest.TempPathFactory) -> Generator[str, None, None]:
    """Start the web server for browser-based tests.

    Args:
        tmp_path_factory: Factory for temporary directories.

    Yields:
        Base URL for the running server.
    """
    data_root = tmp_path_factory.mktemp("arbolab-data")
    db_path = data_root / "saas.db"

    env = os.environ.copy()
    env["ARBO_DATA_ROOT"] = str(data_root)
    env["ARBO_DATABASE_URL"] = f"sqlite:///{db_path}"
    env["ARBO_RUN_SEED"] = "1"

    port = _get_free_port()
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "apps.web.main:app", "--port", str(port)],
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    base_url = f"http://127.0.0.1:{port}"
    _wait_for_server(base_url, process)

    try:
        yield base_url
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
