from common.info import Info

class TwitchInfo(Info):
    def __init__(self):
        super().__init__()

        #home page
        self.title: str = None
        self.followerCount: str = None
        self.currentStream: TwitchStream = None

        #about page
        self.description: str = None
        self.team: str = None
        self.externalLinks: list[tuple[str, str]] = []

    def get_linksString(self) -> str:
        linkStrings = [f"{link[0]} - {link[1]}" for link in self.externalLinks]
        return "\n".join(linkStrings)

    def csv(self) -> str:
        csv: str = ""

        csv += f"Scan Date,{self.get_date()}\n"
        csv += f"Twitch Channel,{self.title}\n"
        sanitizedDescription = self.description.replace("\"", "\"\"")
        csv += f"Description,\"{sanitizedDescription}\"\n"
        csv += f"Team,{self.team}\n"
        csv += f"Followers,{self.followerCount}\n"

        if len(self.externalLinks) > 0:
            csv += "External,Website,Link\n"
            for link in self.externalLinks:
                csv += f",{link[0]},{link[1]}\n"

        if self.currentStream is not None:
            csv += self.currentStream.csv()

        return csv
    
    def __str__(self) -> str:
        info: str = ""

        info += f"Channel Title: {self.title}\n"
        info += f"Description: {self.description}\n"
        info += f"Team: {self.team}\n"
        info += f"Followers: {self.followerCount}"

        if len(self.externalLinks) > 0:
            info += "\n\n"
            info += "External Links:\n"
            info += self.get_linksString()
        
        if self.currentStream is not None:
            info += "\n\n"
            info += f"{self.currentStream}"

        return info

class TwitchStream:
    def __init__(self, title:str = None, game:str = None, tags:list[str] = None, viewerCount:int = None, currentRuntime:str = None):
        self.title: str = title
        self.game: str = game
        self.tags: list[str] = tags
        self.viewerCount: int = viewerCount
        self.currentRuntime: str = currentRuntime

    def get_tagstring(self) -> str:
        return ", ".join(self.tags)

    def csv(self) -> str:
        csv: str = ""

        csv += "CURRENT LIVESTREAM\n"
        sanitizedTitle = self.title.replace("\"", "\"\"")
        csv += f"Title,\"{sanitizedTitle}\"\n"
        csv += f"Game,{self.game}\n"
        csv += f"Tags,\"{self.get_tagstring()}\"\n"
        csv += f"Viewer Count,{self.viewerCount}\n"
        csv += f"Runtime,{self.currentRuntime}\n"

        return csv

    def __str__(self) -> str:
        info: str = ""

        info += f"Current Stream: {self.title}\n"
        info += f"Game: {self.game}\n"
        info += f"Tags: {self.get_tagstring()}\n"
        info += f"Current Viewers: {self.viewerCount}\n"
        info += f"Runtime: {self.currentRuntime}"

        return info