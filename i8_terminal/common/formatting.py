import re
from datetime import date
from typing import Any, Optional, Union

import arrow
import numpy as np


def make_svg_responsive(svg_str: str) -> str:
    svg_str = re.sub(r'width=".+?"', "", svg_str, 1)
    svg_str = re.sub(r'height=".+?"', "", svg_str, 1)
    svg_str = re.sub(r'style=""', r'style="fill: rgba(0, 0, 0, 0);"', svg_str, 1)  # Make svg transparent

    return svg_str


def format_number(
    m: int,
    unit: Optional[str] = None,
    decimal: int = 2,
    humanize: bool = False,
    colorize: bool = False,
    in_millions: bool = False,
    exportize: Optional[bool] = False,
) -> Optional[Union[str, int]]:
    res: Optional[Union[str, int]] = None
    if m is None or np.isnan(m):
        return "-"

    if exportize:
        return round(m, 2)

    if in_millions and unit in ["usd", "shares"]:
        number = abs(m)
        if number >= 1e6:
            if m < 0:
                res = f"({number // 1e6:,.1f})"
            else:
                res = f"{number // 1e6:,.1f}"

    elif humanize or unit in ["shares", "usdpershare"]:
        number = abs(m)
        if number < 1e3:
            res = f"{m:,.{decimal}f}"
        if number >= 1e3 and number < 1e6:
            res = f"{m / 1e3:,.2f} K"
        if number >= 1e6 and number < 1e9:
            res = f"{m / 1e6:,.2f} M"
        if number >= 1e9 and number < 1e12:
            res = f"{m / 1e9:,.2f} B"
        if number >= 1e12:
            res = f"{m / 1e12:,.2f} T"
    else:
        res = f"{m:,.{decimal}f}"

    if unit == "percentage":
        res = f"{res}%" if m <= 0 else f"+{res}%"

    if unit == "usd":
        res = f"${res}"

    if colorize:
        color = "red" if m <= 0 else "green"
        res = f"[{color}]{res}[/{color}]"

    return res


def format_date(date: date, use_elapsed_format: bool = False, use_precise_format: bool = False) -> Any:
    if use_elapsed_format:
        time_span = arrow.utcnow() - arrow.get(date)
        days = time_span.days
        if days >= 2:
            return arrow.get(date, tzinfo="US/Eastern").strftime("%b %d, %Y %I:%M %p ET")
        hours, remainder = divmod(time_span.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if not use_precise_format:
            if days > 0:
                time = f'{days} day{"s" if days > 1 else ""}'
            elif hours > 0:
                time = f'{hours} hour{"s" if hours > 1 else ""}'
            elif minutes > 0:
                time = f'{minutes} minute{"s" if minutes > 1 else ""}'
            else:
                time = f"{seconds} seconds"

            return f"{time} ago"
        else:
            if days > 0:
                time = f"{days} day, {hours} hour"
            elif hours > 0:
                time = f"{hours} hour, {minutes} minute"
            elif minutes > 0:
                time = f"{minutes} minute, {seconds} second"
            else:
                time = f"{seconds} second"

            return time
    else:
        return arrow.get(date).strftime("%b %d, %Y")


def format_fyq(fyq: str) -> str:
    return f"{fyq[-2:]} {fyq[2:-2]}"


_formatters_map = {
    ("fyq", "console"): lambda x: format_fyq(x),
    ("fyq", "store"): lambda x: format_fyq(x),
    ("number", "console"): lambda x: format_number(x),
    ("number", "store"): lambda x: format_number(x),
    ("price", "console"): lambda x: format_number(x, unit="usd"),
    ("financial", "console"): lambda x: format_number(x, unit="usd", humanize=True),
    ("price", "store"): lambda x: round(x, 2),
    ("number_int", "console"): lambda x: format_number(x, decimal=0),
    ("number_int", "store"): lambda x: int(x),
    ("perc", "console"): lambda x: format_number(x, decimal=2, unit="percentage", colorize=True),
    ("perc", "store"): lambda x: format_number(x, decimal=2),
    ("date", "console"): lambda x: format_date(x),
    ("date", "store"): lambda x: format_date(x),
}


def get_formatter(name: str, target: str) -> Any:
    return _formatters_map[(name, target)]
