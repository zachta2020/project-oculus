from common.info import Info

class TwitchInfo(Info):
    def __init__(self):
        super().__init__()

        self.title: str = None
        self.followerCount: str = None

    def csv(self) -> str:
        csv: str = ""

        csv += f"Scan Date,{self.get_date()}\n"
        csv += f"Twitch Channel,{self.title}\n"
        csv += f"Followers,{self.followerCount}\n"

        return csv
    
    def __str__(self) -> str:
        info: str = ""

        info += f"Channel Title: {self.title}\n"
        info += f"Followers: {self.followerCount}\n"

        return info