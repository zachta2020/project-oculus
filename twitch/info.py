from common.info import Info

class TwitchInfo(Info):
    def __init__(self):
        super().__init__()

        self.title: str = None
        self.followerCount: str = None

        self.currentStream: TwitchStream = None

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
        
        if self.currentStream is not None:
            info += "\n"
            info += f"{self.currentStream}\n"

        return info

class TwitchStream:
    def __init__(self, title:str = None, game:str = None, tags:list[str] = None, viewerCount:int = None, currentRuntime:str = None):
        self.title: str = title
        self.game: str = game
        self.tags: list[str] = tags
        self.viewerCount: int = viewerCount
        self.currentRuntime: str = currentRuntime

    def __str__(self) -> str:
        info: str = ""

        info += f"Current Stream: {self.title}\n"
        info += f"Game: {self.game}\n"

        tagstring = ", ".join(self.tags)
        info += f"Tags: {tagstring}\n"

        info += f"Current Viewers: {self.viewerCount}\n"
        info += f"Runtime: {self.currentRuntime}"

        return info