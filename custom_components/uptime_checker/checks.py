"""Check implementations for uptime_checker — no Home Assistant imports."""
from __future__ import annotations

import asyncio
import socket

import aiohttp
from icmplib import async_ping

DEFAULT_TIMEOUT = 5.0


async def check_ping(address: str, timeout: float = DEFAULT_TIMEOUT) -> bool:
    try:
        host = await async_ping(address, count=1, timeout=timeout, privileged=False)
        return bool(host.is_alive)
    except Exception:
        return False


async def check_dns(address: str, timeout: float = DEFAULT_TIMEOUT) -> bool:
    try:
        await asyncio.wait_for(
            asyncio.to_thread(socket.getaddrinfo, address, None), timeout=timeout
        )
        return True
    except Exception:
        return False


async def check_http(address: str, timeout: float = DEFAULT_TIMEOUT) -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                address, timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                return response.status < 500
    except Exception:
        return False


CHECK_FUNCS = {
    "ping": check_ping,
    "dns": check_dns,
    "http": check_http,
}
