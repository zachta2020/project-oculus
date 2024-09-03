"""
Info object representing a patreon creator's account
"""
from common.info import Info
from patreon.patreon_common import baseURL

class PatreonInfo(Info):
    def __init__(self):
        super().__init__()

        self.title: str = None
        self.subtitle: str = None
        self.memberCount: int = None
        self.postCount: int = None
        self.income: str = None

        self.postList: list[PatreonPost] = []

    def csv(self) -> str:
        csv: str = ""

        csv += f'Patreon,{self.title},"{self.subtitle}"\n'
        if self.memberCount is not None:
            csv += f"Member Count,{self.memberCount}\n"
        else:
            csv += "Member Count,N/A\n"

        csv += f"Scan Date,{self.get_date()}"

        csv += f"Post Count,{self.postCount}\n"

        if self.income is not None:
            csv += f'Income,"{self.income}"\n'
        else:
            csv += "Income,N/A\n"

        counter = 1
        csv += "Post,Title,Date,Link,Locked\n"
        for post in self.postList:
            csv += f'{counter},{post.csv()}\n'
            counter += 1

        return csv
    
    def __str__(self):
        info = ""

        info += f"Patreon: {self.title}\n{self.subtitle}\n\n"
        if self.memberCount is not None:
            info += f"Member Count: {self.memberCount}\n"
        else:
            info += "Member Count not found"
        info += f"Post Count: {len(self.postList)}/{self.postCount}\n"
        if self.income is not None:
            info += f"Income: {self.income}"
        else:
            info += "Income not found"

        return info

class PatreonPost:
    def __init__(self, title: str = "", date: str = "", link: str = "", locked: bool = False):
        self.title: str = title
        self.date: str = date
        self.link: str = link
        self.locked: bool = locked

    def csv(self) -> str:
        return f'"{self.title}","{self.date}",{baseURL + self.link},{self.locked}'