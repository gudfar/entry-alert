"""CoinGecko free-tier API client.

Uses /simple/price to batch-fetch prices for multiple coins in one request.
CoinGecko requires coin IDs (not symbols) — SYMBOL_TO_ID maps the uppercase
symbols used internally to the canonical CoinGecko IDs.
"""

import os
import httpx
from typing import Optional

COINGECKO_BASE = "https://api.coingecko.com/api/v3"

# Maps uppercase coin symbol -> CoinGecko coin ID.
# Extend this dict when adding support for new coins.
SYMBOL_TO_ID: dict[str, str] = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "ADA": "cardano",
    "XRP": "ripple",
    "DOGE": "dogecoin",
    "DOT": "polkadot",
    "AVAX": "avalanche-2",
    "MATIC": "matic-network",
    "LINK": "chainlink",
    "UNI": "uniswap",
    "LTC": "litecoin",
    "ATOM": "cosmos",
    "TRX": "tron",
    "NEAR": "near",
    "APT": "aptos",
    "ARB": "arbitrum",
    "OP": "optimism",
    "SUI": "sui",
}


def _headers() -> dict:
    api_key = os.environ.get("COINGECKO_API_KEY", "").strip()
    if api_key:
        return {"x-cg-pro-api-key": api_key}
    return {}


async def fetch_prices(symbols: list[str]) -> dict[str, Optional[float]]:
    """Batch-fetch USD prices for the given coin symbols.

    Returns a dict {SYMBOL: price_usd} for recognised symbols.
    Unknown symbols (not in SYMBOL_TO_ID) are omitted from the result.

    Raises httpx.HTTPError on network/API failure.
    """
    known = {s: SYMBOL_TO_ID[s] for s in symbols if s in SYMBOL_TO_ID}
    if not known:
        return {}

    ids_param = ",".join(known.values())
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            f"{COINGECKO_BASE}/simple/price",
            params={"ids": ids_param, "vs_currencies": "usd"},
            headers=_headers(),
        )
        response.raise_for_status()
        data: dict = response.json()

    # Invert: id -> symbol, then build {SYMBOL: price}
    id_to_symbol = {v: k for k, v in known.items()}
    result: dict[str, Optional[float]] = {}
    for cg_id, prices in data.items():
        symbol = id_to_symbol.get(cg_id)
        if symbol:
            result[symbol] = prices.get("usd")
    return result
