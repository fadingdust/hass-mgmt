"""Check implementations for uptime_checker — no Home Assistant imports."""
from __future__ import annotations

import asyncio
import socket
import time
from typing import NamedTuple

import aiohttp
from icmplib import async_ping

DEFAULT_TIMEOUT = 5.0


class CheckResult(NamedTuple):
    is_up: bool
    rtt_ms: float | None


async def check_ping(address: str, timeout: float = DEFAULT_TIMEOUT) -> CheckResult:
    try:
        host = await async_ping(address, count=1, timeout=timeout, privileged=False)
        if host.is_alive:
            return CheckResult(True, host.avg_rtt)
        return CheckResult(False, None)
    except Exception:
        return CheckResult(False, None)


async def check_dns(address: str, timeout: float = DEFAULT_TIMEOUT) -> CheckResult:
    start = time.monotonic()
    try:
        await asyncio.wait_for(
            asyncio.to_thread(socket.getaddrinfo, address, None), timeout=timeout
        )
        return CheckResult(True, (time.monotonic() - start) * 1000)
    except Exception:
        return CheckResult(False, None)


async def check_http(address: str, timeout: float = DEFAULT_TIMEOUT) -> CheckResult:
    start = time.monotonic()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                address, timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                elapsed_ms = (time.monotonic() - start) * 1000
                is_up = response.status < 500
                return CheckResult(is_up, elapsed_ms if is_up else None)
    except Exception:
        return CheckResult(False, None)


CHECK_FUNCS = {
    "ping": check_ping,
    "dns": check_dns,
    "http": check_http,
}
