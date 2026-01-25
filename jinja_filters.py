from datetime import datetime

def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    """Format a datetime object for Jinja2 templates."""
    if not value:
        return ''
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except Exception:
            return value
    return value.strftime(format)

def format_nz_week(date):
    """Format NZ week label from yyyy-mm-dd to dd-mm-yyyy."""
    if not date:
        return ''
    if isinstance(date, str):
        try:
            date = datetime.strptime(date, '%Y-%m-%d')
        except Exception:
            return date
    return date.strftime('%d-%m-%Y')
