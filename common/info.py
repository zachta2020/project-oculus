"""
Common interface for Info objects that Scanners create and fill
"""
from datetime import datetime

class Info:
    def __init__(self):
        self.date: datetime = datetime.today()

    def csv(self) -> str:
        return ""