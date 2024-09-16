"""
Common interface for Info objects that Scanners create and fill
"""
from datetime import datetime

class Info:
    def __init__(self):
        self.date: datetime = datetime.today()

    def get_date(self):
        return f"{self.date.year}-{self.date.month}-{self.date.day}_{self.date.hour}:{str(self.date.minute).zfill(2)}"

    def csv(self) -> str:
        return ""