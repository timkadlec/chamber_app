# filters.py

from datetime import datetime

def format_date(date):
    """Format date as DD. MM. YYYY"""
    if date:
        return date.strftime("%d. %m. %Y")
    return ''
