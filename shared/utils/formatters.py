"""
Formatting Utilities Module

This module provides data formatting utilities for the MathVerse
platform, including date/time formatting, number formatting, and
display formatting.
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from decimal import Decimal


def format_duration(
    seconds: int,
    format_type: str = "short"
) -> str:
    """
    Format a duration in seconds to a human-readable string.
    
    Args:
        seconds: Duration in seconds
        format_type: Format type ("short", "long", "verbose")
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        if format_type == "verbose":
            return f"{seconds} second{'s' if seconds != 1 else ''}"
        return f"{seconds}s"
    
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    
    if minutes < 60:
        if format_type == "verbose":
            s = "" if minutes == 1 else "s"
            return f"{minute}{s} {remaining_seconds} second{'s' if remaining_seconds != 1 else ''}"
        return f"{minutes}m {remaining_seconds}s"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if format_type == "verbose":
        h = "" if hours == 1 else "s"
        m = "" if remaining_minutes == 1 else "s"
        s = "" if remaining_seconds == 1 else "s"
        return f"{hours} hour{h}, {remaining_minutes} minute{m}, {remaining_seconds} second{s}"
    
    return f"{hours}h {remaining_minutes}m"


def format_duration_hours(minutes: int) -> str:
    """
    Format duration in minutes to hours and minutes.
    
    Args:
        minutes: Duration in minutes
        
    Returns:
        Formatted string (e.g., "2h 30m")
    """
    hours = minutes // 60
    mins = minutes % 60
    
    if hours == 0:
        return f"{mins}m"
    elif mins == 0:
        return f"{hours}h"
    else:
        return f"{hours}h {mins}m"


def format_number(
    number: Union[int, float, Decimal],
    decimal_places: int = 2,
    use_thousands_separator: bool = True
) -> str:
    """
    Format a number with proper thousands separators and decimals.
    
    Args:
        number: Number to format
        decimal_places: Number of decimal places
        use_thousands_separator: Whether to use commas
        
    Returns:
        Formatted number string
    """
    if isinstance(number, float):
        formatted = f"{number:,.{decimal_places}f}"
    elif isinstance(number, Decimal):
        formatted = f"{float(number):,.{decimal_places}f}"
    else:
        formatted = f"{number:,}"
        
        if decimal_places > 0:
            formatted += "." + "0" * decimal_places
    
    return formatted


def format_percentage(
    value: float,
    decimal_places: int = 1,
    include_symbol: bool = True
) -> str:
    """
    Format a value as a percentage.
    
    Args:
        value: Value to format (0-1 range)
        decimal_places: Number of decimal places
        include_symbol: Whether to include % symbol
        
    Returns:
        Formatted percentage string
    """
    percentage = value * 100
    
    if include_symbol:
        return f"{percentage:.{decimal_places}f}%"
    return f"{percentage:.{decimal_places}f}"


def format_date(
    date: Union[datetime, str],
    format_str: str = "medium"
) -> str:
    """
    Format a date for display.
    
    Args:
        date: Date to format or ISO date string
        format_str: Format preset ("short", "medium", "long", "full")
        
    Returns:
        Formatted date string
    """
    if isinstance(date, str):
        date = datetime.fromisoformat(date.replace("Z", "+00:00"))
    
    format_map = {
        "short": "%m/%d/%y",
        "medium": "%b %d, %Y",
        "long": "%B %d, %Y",
        "full": "%A, %B %d, %Y"
    }
    
    fmt = format_map.get(format_str, format_str)
    return date.strftime(fmt)


def format_datetime(
    date: Union[datetime, str],
    format_str: str = "medium"
) -> str:
    """
    Format a datetime for display.
    
    Args:
        date: Datetime to format or ISO string
        format_str: Format preset ("short", "medium", "long")
        
    Returns:
        Formatted datetime string
    """
    if isinstance(date, str):
        date = datetime.fromisoformat(date.replace("Z", "+00:00"))
    
    format_map = {
        "short": "%m/%d/%y %H:%M",
        "medium": "%b %d, %Y %I:%M %p",
        "long": "%B %d, %Y at %I:%M %p"
    }
    
    fmt = format_map.get(format_str, format_str)
    return date.strftime(fmt)


def format_relative_time(date: Union[datetime, str]) -> str:
    """
    Format a date as relative time (e.g., "2 hours ago").
    
    Args:
        date: Date to format or ISO string
        
    Returns:
        Relative time string
    """
    if isinstance(date, str):
        date = datetime.fromisoformat(date.replace("Z", "+00:00"))
    
    now = datetime.now()
    diff = now - date
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    
    minutes = seconds / 60
    if minutes < 60:
        mins = int(minutes)
        return f"{mins} minute{'s' if mins != 1 else ''} ago"
    
    hours = minutes / 60
    if hours < 24:
        hrs = int(hours)
        return f"{hrs} hour{'s' if hrs != 1 else ''} ago"
    
    days = hours / 24
    if days < 7:
        d = int(days)
        return f"{d} day{'s' if d != 1 else ''} ago"
    
    weeks = days / 7
    if weeks < 4:
        w = int(weeks)
        return f"{w} week{'s' if w != 1 else ''} ago"
    
    months = days / 30
    if months < 12:
        m = int(months)
        return f"{m} month{'s' if m != 1 else ''} ago"
    
    years = days / 365
    y = int(years)
    return f"{y} year{'s' if y != 1 else ''} ago"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "2.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    
    size_kb = size_bytes / 1024
    if size_kb < 1024:
        return f"{size_kb:.1f} KB"
    
    size_mb = size_kb / 1024
    if size_mb < 1024:
        return f"{size_mb:.1f} MB"
    
    size_gb = size_mb / 1024
    return f"{size_gb:.1f} GB"


def format_count(
    count: int,
    singular: str,
    plural: str
) -> str:
    """
    Format a count with proper singular/plural form.
    
    Args:
        count: Count value
        singular: Singular form
        plural: Plural form
        
    Returns:
        Formatted count string
    """
    return f"{count} {singular if count == 1 else plural}"


def format_progress(
    current: int,
    total: int,
    decimals: int = 1
) -> str:
    """
    Format progress as a percentage.
    
    Args:
        current: Current value
        total: Total value
        decimals: Decimal places
        
    Returns:
        Formatted progress string
    """
    if total == 0:
        return "0%"
    
    percentage = (current / total) * 100
    return f"{percentage:.{decimals}f}%"


def truncate_text(
    text: str,
    max_length: int,
    suffix: str = "..."
) -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix for truncated text
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_phone_number(phone: str) -> str:
    """
    Format a phone number for display.
    
    Args:
        phone: Phone number string
        
    Returns:
        Formatted phone number
    """
    digits = re.sub(r"\D", "", phone)
    
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits.startswith("1"):
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    
    return phone


def format_grade_level(level: int) -> str:
    """
    Format a grade level for display.
    
    Args:
        level: Grade level (1-12)
        
    Returns:
        Formatted grade string
    """
    suffixes = {1: "st", 2: "nd", 3: "rd"}
    suffix = suffixes.get(level % 10, "th") if level not in (11, 12, 13) else "th"
    
    return f"{level}{suffix} grade"


def format_currency(
    amount: float,
    currency: str = "USD",
    locale: str = "en_US"
) -> str:
    """
    Format a currency amount.
    
    Args:
        amount: Amount to format
        currency: Currency code
        locale: Locale for formatting
        
    Returns:
        Formatted currency string
    """
    import locale as locale_module
    
    try:
        locale_module.setlocale(locale_module.LC_ALL, locale)
    except locale_module.Error:
        locale = "en_US.UTF-8"
    
    try:
        return locale_module.currency(amount, currency, symbol=True, grouping=True)
    except Exception:
        return f"{currency} {amount:,.2f}"
