# shoppinglist.py
# Logic and helper functions for the Shopping List feature

# Add your Shopping List related functions and classes here.


import datetime

def get_week_dates(week_offset=0):
    """
    Returns a list of date objects for the week (Monday to Friday) based on the current week and offset.
    week_offset=0 is current week, -1 is previous, +1 is next, etc.
    """
    today = datetime.date.today()
    # Find the Monday of the current week
    monday = today - datetime.timedelta(days=today.weekday())
    # Apply week offset
    monday = monday + datetime.timedelta(weeks=week_offset)
    return [monday + datetime.timedelta(days=i) for i in range(5)]

def get_week_label(week_dates):
    """Returns a string label for the week, e.g. 'Week of 15/12/25 to 19/12/25'"""
    start = week_dates[0].strftime('%d/%m/%y')
    end = week_dates[-1].strftime('%d/%m/%y')
    return f"Week of {start} to {end}"

def get_dummy_grid(week_dates):
    """Returns a dummy grid for the week: { (period, date): None }"""
    grid = {}
    for period in range(1, 6):
        for date in week_dates:
            grid[(period, date)] = None
    return grid
