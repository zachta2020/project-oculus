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
    if vidDate.find("hour") != -1:
        hours = int(
            vidDate
                .replace(" hours ago", "")
                .replace(" hour ago", "")
        )
    if vidDate.find("minute") != -1:
        minutes = int(
            vidDate
                .replace(" minutes ago", "")
                .replace(" minute ago", "")
        )
    if vidDate.find("second") != -1:
        seconds = int(
            vidDate
                .replace(" seconds ago", "")
                .replace(" second ago", "")
        )
    return write_date(date.today() - timedelta(hours=hours, minutes=minutes, seconds=seconds))