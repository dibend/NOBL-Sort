#!/usr/bin/env python3
"""
Sort NOBL components by dividend yield using yfinance.

This script:
    1. Uses a hardcoded Python list of NOBL component tickers.
    2. Fetches price and trailing annual dividend data with yfinance.
    3. Calculates dividend yield manually as:

           dividend_yield_percent = dividend_rate / current_price * 100

    4. Sorts components by dividend yield from highest to lowest.
    5. Exports the result to a real CSV file.

Install dependencies:
    pip install yfinance pandas

Run:
    python sort_nobl_by_dividend_yield.py

Output:
    nobl_sorted_by_dividend_yield.csv
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf


OUTPUT_CSV = Path("nobl_sorted_by_dividend_yield.csv")
REQUEST_DELAY_SECONDS = 0.25


NOBL_COMPONENTS: list[str] = [
    "WST",
    "BEN",
    "NUE",
    "ADP",
    "ADM",
    "CL",
    "CAT",
    "ESS",
    "KO",
    "SJM",
    "FRT",
    "GWW",
    "GD",
    "ABBV",
    "EXPD",
    "ES",
    "LIN",
    "XOM",
    "TROW",
    "CHD",
    "JNJ",
    "CVX",
    "KMB",
    "NDSN",
    "SYY",
    "AFL",
    "PG",
    "KVUE",
    "CINF",
    "ED",
    "SWK",
    "HRL",
    "CB",
    "IBM",
    "APD",
    "CTAS",
    "CAH",
    "NEE",
    "PEP",
    "PPG",
    "O",
    "ATO",
    "FDS",
    "FAST",
    "MDT",
    "CLX",
    "DOV",
    "TGT",
    "CHRW",
    "ABT",
    "BDX",
    "EMR",
    "SPGI",
    "ECL",
    "MCD",
    "AMCR",
    "ITW",
    "WMT",
    "SHW",
    "MKC",
    "BF-B",  # Yahoo Finance format for BF/B.
    "ROP",
    "ERIE",
    "AOS",
    "ALB",
    "LOW",
    "GPC",
    "BRO",
    "PNR",
]


@dataclass(frozen=True)
class DividendRecord:
    """Dividend data for one equity."""

    ticker: str
    company_name: str | None
    current_price: float | None
    trailing_annual_dividend_rate: float | None
    dividend_yield_percent: float | None
    source_note: str


def safe_float(value: Any) -> float | None:
    """
    Convert a value to float when possible.

    Args:
        value: Value returned by yfinance.

    Returns:
        Float value, or None when conversion fails.
    """

    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_current_price(info: dict[str, Any], ticker_object: yf.Ticker) -> float | None:
    """
    Get the best available current price.

    Args:
        info: yfinance info dictionary.
        ticker_object: yfinance Ticker object.

    Returns:
        Current price, or None when unavailable.
    """

    price = safe_float(
        info.get("currentPrice")
        or info.get("regularMarketPrice")
        or info.get("previousClose")
    )

    if price is not None:
        return price

    try:
        fast_info_price = ticker_object.fast_info.get("last_price")
        return safe_float(fast_info_price)
    except Exception:
        return None


def get_trailing_annual_dividend_rate(info: dict[str, Any]) -> float | None:
    """
    Get the trailing annual dividend rate.

    Args:
        info: yfinance info dictionary.

    Returns:
        Annual dividend per share, or None when unavailable.
    """

    return safe_float(
        info.get("trailingAnnualDividendRate")
        or info.get("dividendRate")
    )


def calculate_dividend_yield_percent(
    dividend_rate: float | None,
    current_price: float | None,
) -> float | None:
    """
    Calculate dividend yield as a percentage.

    Args:
        dividend_rate: Annual dividend per share.
        current_price: Current share price.

    Returns:
        Dividend yield percentage, or None when inputs are unavailable.
    """

    if dividend_rate is None or current_price is None:
        return None

    if current_price <= 0:
        return None

    return (dividend_rate / current_price) * 100


def fetch_dividend_record(ticker: str) -> DividendRecord:
    """
    Fetch and calculate dividend data for one ticker.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        DividendRecord with calculated dividend yield.
    """

    ticker_object = yf.Ticker(ticker)
    info = ticker_object.info

    company_name = info.get("longName") or info.get("shortName")
    current_price = get_current_price(info, ticker_object)
    dividend_rate = get_trailing_annual_dividend_rate(info)

    dividend_yield_percent = calculate_dividend_yield_percent(
        dividend_rate=dividend_rate,
        current_price=current_price,
    )

    return DividendRecord(
        ticker=ticker,
        company_name=str(company_name) if company_name else None,
        current_price=current_price,
        trailing_annual_dividend_rate=dividend_rate,
        dividend_yield_percent=dividend_yield_percent,
        source_note="calculated as trailing annual dividend rate / current price",
    )


def build_dividend_dataframe(tickers: list[str]) -> pd.DataFrame:
    """
    Build a DataFrame sorted by dividend yield.

    Args:
        tickers: List of ticker symbols.

    Returns:
        Sorted pandas DataFrame.
    """

    records: list[DividendRecord] = []

    for index, ticker in enumerate(tickers, start=1):
        print(f"[{index:02d}/{len(tickers)}] Fetching {ticker}")

        try:
            record = fetch_dividend_record(ticker)
        except Exception as error:
            record = DividendRecord(
                ticker=ticker,
                company_name=None,
                current_price=None,
                trailing_annual_dividend_rate=None,
                dividend_yield_percent=None,
                source_note=f"error: {error}",
            )

        records.append(record)
        time.sleep(REQUEST_DELAY_SECONDS)

    dataframe = pd.DataFrame(
        {
            "Ticker": record.ticker,
            "Company Name": record.company_name,
            "Current Price": record.current_price,
            "Trailing Annual Dividend Rate": record.trailing_annual_dividend_rate,
            "Dividend Yield %": record.dividend_yield_percent,
            "Source Note": record.source_note,
        }
        for record in records
    )

    dataframe = dataframe.sort_values(
        by="Dividend Yield %",
        ascending=False,
        na_position="last",
    ).reset_index(drop=True)

    dataframe["Current Price"] = dataframe["Current Price"].round(2)
    dataframe["Trailing Annual Dividend Rate"] = dataframe[
        "Trailing Annual Dividend Rate"
    ].round(4)
    dataframe["Dividend Yield %"] = dataframe["Dividend Yield %"].round(2)

    return dataframe


def main() -> None:
    """Run the NOBL dividend-yield sorting workflow."""

    sorted_dataframe = build_dividend_dataframe(NOBL_COMPONENTS)

    sorted_dataframe.to_csv(OUTPUT_CSV, index=False)

    print()
    print(sorted_dataframe.to_string(index=False))
    print()
    print(f"Saved CSV file: {OUTPUT_CSV.resolve()}")


if __name__ == "__main__":
    main()
