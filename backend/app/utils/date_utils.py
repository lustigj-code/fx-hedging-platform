"""
Date utilities for FX hedging calculations.
"""
from datetime import date, datetime, timedelta
from typing import Tuple


def calculate_time_to_maturity(invoice_date: date, payment_date: date) -> float:
    """
    Calculate time to maturity in years.

    Uses actual/365 day count convention (standard for FX options).

    Args:
        invoice_date: Invoice date
        payment_date: Payment date

    Returns:
        Time to maturity in years (e.g., 0.25 for 90 days)
    """
    days_diff = (payment_date - invoice_date).days

    if days_diff < 0:
        raise ValueError("Payment date must be after invoice date")

    return days_diff / 365.0


def calculate_days_to_maturity(invoice_date: date, payment_date: date) -> int:
    """
    Calculate days between invoice and payment.

    Args:
        invoice_date: Invoice date
        payment_date: Payment date

    Returns:
        Number of days
    """
    days_diff = (payment_date - invoice_date).days

    if days_diff < 0:
        raise ValueError("Payment date must be after invoice date")

    return days_diff


def get_trading_days(start_date: date, end_date: date, holidays: list = None) -> int:
    """
    Calculate number of trading days between two dates.

    Excludes weekends and optionally holidays.

    Args:
        start_date: Start date
        end_date: End date
        holidays: List of holiday dates to exclude (optional)

    Returns:
        Number of trading days
    """
    if holidays is None:
        holidays = []

    trading_days = 0
    current_date = start_date

    while current_date <= end_date:
        # Check if weekday (Monday = 0, Sunday = 6)
        if current_date.weekday() < 5:  # Monday-Friday
            # Check if not a holiday
            if current_date not in holidays:
                trading_days += 1

        current_date += timedelta(days=1)

    return trading_days


def annualize_rate(rate: float, days: int, convention: str = "actual/365") -> float:
    """
    Annualize a rate from a shorter period.

    Args:
        rate: Rate for the period (e.g., 0.02 for 2%)
        days: Number of days in the period
        convention: Day count convention ("actual/365" or "actual/360")

    Returns:
        Annualized rate
    """
    if convention == "actual/365":
        return rate * (365 / days)
    elif convention == "actual/360":
        return rate * (360 / days)
    else:
        raise ValueError(f"Unknown convention: {convention}")


def date_range(start_date: date, end_date: date, step_days: int = 1) -> list:
    """
    Generate list of dates between start and end.

    Args:
        start_date: Start date
        end_date: End date
        step_days: Step size in days (default: 1)

    Returns:
        List of dates
    """
    dates = []
    current_date = start_date

    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=step_days)

    return dates


def get_maturity_bucket(days_to_maturity: int) -> str:
    """
    Categorize maturity into standard buckets.

    Common FX option maturities:
    - O/N: Overnight
    - 1W: 1 week
    - 1M: 1 month
    - 3M: 3 months
    - 6M: 6 months
    - 1Y: 1 year

    Args:
        days_to_maturity: Days until maturity

    Returns:
        Maturity bucket label
    """
    if days_to_maturity <= 1:
        return "O/N"
    elif days_to_maturity <= 7:
        return "1W"
    elif days_to_maturity <= 30:
        return "1M"
    elif days_to_maturity <= 90:
        return "3M"
    elif days_to_maturity <= 180:
        return "6M"
    elif days_to_maturity <= 365:
        return "1Y"
    else:
        years = days_to_maturity / 365
        return f"{years:.1f}Y"


def is_business_day(check_date: date, holidays: list = None) -> bool:
    """
    Check if a date is a business day.

    Args:
        check_date: Date to check
        holidays: List of holiday dates (optional)

    Returns:
        True if business day, False otherwise
    """
    if holidays is None:
        holidays = []

    # Check if weekend
    if check_date.weekday() >= 5:  # Saturday or Sunday
        return False

    # Check if holiday
    if check_date in holidays:
        return False

    return True


def next_business_day(from_date: date, holidays: list = None) -> date:
    """
    Get the next business day after the given date.

    Args:
        from_date: Starting date
        holidays: List of holiday dates (optional)

    Returns:
        Next business day
    """
    next_day = from_date + timedelta(days=1)

    while not is_business_day(next_day, holidays):
        next_day += timedelta(days=1)

    return next_day


def previous_business_day(from_date: date, holidays: list = None) -> date:
    """
    Get the previous business day before the given date.

    Args:
        from_date: Starting date
        holidays: List of holiday dates (optional)

    Returns:
        Previous business day
    """
    prev_day = from_date - timedelta(days=1)

    while not is_business_day(prev_day, holidays):
        prev_day -= timedelta(days=1)

    return prev_day
