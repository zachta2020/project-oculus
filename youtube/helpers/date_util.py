from datetime import date, timedelta

months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec"
    ]

def write_date(date: date):
    return f"{months[date.month-1]} {date.day}, {date.year}"

def relative_to_absolute(vidDate):
    hours = 0
    minutes = 0
    seconds = 0
    if "hour" in vidDate or "h" in vidDate:
        hours = int(
            vidDate
                .replace(" hours ago", "")
                .replace(" hour ago", "")
                .replace("h", "")
        )
    if "minute" in vidDate or "m" in vidDate:
        minutes = int(
            vidDate
                .replace(" minutes ago", "")
                .replace(" minute ago", "")
                .replace("m", "")
        )
    if "second" in vidDate or "s" in vidDate:
        seconds = int(
            vidDate
                .replace(" seconds ago", "")
                .replace(" second ago", "")
                .replace("s", "")
        )
    return write_date(date.today() - timedelta(hours=hours, minutes=minutes, seconds=seconds))