"""
Utility functions for formatting values.
"""

import locale

def format_currency(value: float) -> str:
    """Format a number as currency."""
    try:
        return locale.currency(value, grouping=True)
    except:
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_percentage(value: float) -> str:
    """Format a number as percentage."""
    return f"{value:.2f}%" 