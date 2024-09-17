"""
Info objects representing a YouTube channel and its videos/shorts/livestreams
"""

from common.info import Info

class YouTubeChannelInfo(Info):
    """Models information about a YouTube channel"""
    def __init__(self):
        super().__init__()

        self.title: str = None
        self.about: str = None
        self.subCount: int = None
        self.vidCount: int = None
        self.viewCount: int = None
        self.joinDate: str = None
        self.socmedLinks: list[tuple[str, str]] = []
        self.videos: list[youtubeVideoInfo] = []
        self.premieringVideos: list[youtubeCurrentInfo] = []
        self.scheduledVideos: list[youtubeScheduledInfo] = []
        self.shorts: list[youtubeVideoInfo] = []
        self.livestreamVODs: list[youtubeVideoInfo] = []
        self.currentLivestreams: list[youtubeCurrentInfo] = []
        self.scheduledLivestreams: list[youtubeScheduledInfo] = []

    def csv(self) -> str:
        csv_string = f"YouTube Channel,{self.title}\n"
        sanitizedAbout = self.about.replace('\"', '\"\"')
        csv_string += f"About,\"{sanitizedAbout}\"\n"
        csv_string += f"Scan Date, {self.get_date()}\n"
        csv_string += f"Subscribers,\"{self.subCount}\"\n"
        csv_string += f"Total Videos,\"{self.vidCount}\"\n"
        csv_string += f"Videos,\"{len(self.videos)}\"\n"
        csv_string += f"Shorts,\"{len(self.shorts)}\"\n"
        csv_string += f"Livestreams,\"{len(self.livestreamVODs) + len(self.currentLivestreams) + len(self.scheduledLivestreams)}\"\n"
        csv_string += f"Views,\"{self.viewCount}\"\n"
        csv_string += f"Join Date,\"{self.joinDate}\"\n"

        if len(self.socmedLinks) > 0:
            csv_string += "External,Website,Link\n"
            for link in self.socmedLinks:
                csv_string += f",{link[0]},{link[1]}\n"
        else:
            csv_string += "No External Links Detected\n"

        if len(self.scheduledVideos) > 0:
            csv_string += "SCHEDULED VIDEOS\n"
            csv_string += "Video,Title,Date,Waiting,Likes,URL\n"
            counter = 1
            for vid in self.scheduledVideos:
                sanitizedTitle = vid.title.replace('\"', '\"\"')
                csv_string += f"{counter},\"{sanitizedTitle}\",\"{vid.date}\",\"{vid.waiting}\",\"{vid.likes}\",{vid.URL}\n"
                counter += 1

        if len(self.premieringVideos) > 0:
            csv_string += "PREMIERING VIDEOS\n"
            csv_string += "Video,Title,Date,Waiting,Likes,URL\n"
            counter = 1
            for vid in self.premieringVideos:
                sanitizedTitle = vid.title.replace('\"', '\"\"')
                csv_string += f"{counter},\"{sanitizedTitle}\",\"{vid.date}\",\"{vid.currentViewers}\",\"{vid.likes}\",{vid.URL}\n"
                counter += 1

        if len(self.videos) > 0:
            csv_string += "VIDEOS\n"
            csv_string += "Video,Title,Date,Views,Likes,URL\n"
            counter = 1
            for vid in self.videos:
                sanitizedTitle = vid.title.replace('\"', '\"\"')
                csv_string += f"{counter},\"{sanitizedTitle}\",\"{vid.date}\",\"{vid.views}\",\"{vid.likes}\",{vid.URL}\n"
                counter += 1

        if len(self.shorts) > 0:
            csv_string += "SHORTS\n"
            csv_string += "Short,Title,Date,Views,Likes,URL\n"
            counter = 1
            for vid in self.shorts:
                sanitizedTitle = vid.title.replace('\"', '\"\"')
                csv_string += f"{counter},\"{sanitizedTitle}\",\"{vid.date}\",\"{vid.views}\",\"{vid.likes}\",{vid.URL}\n"
                counter += 1

        if len(self.scheduledLivestreams) > 0:
            csv_string += "SCHEDULED LIVESTREAMS\n"
            csv_string += "Stream,Title,Date,Waiting,Likes,URL\n"
            counter = 1
            for vid in self.scheduledLivestreams:
                sanitizedTitle = vid.title.replace('\"', '\"\"')
                csv_string += f"{counter},\"{sanitizedTitle}\",\"{vid.date}\",\"{vid.waiting}\",\"{vid.likes}\",{vid.URL}\n"
                counter += 1

        if len(self.currentLivestreams) > 0:
            csv_string += "CURRENT LIVESTREAMS\n"
            csv_string += "Stream,Title,Date,Current Viewers,Likes,URL\n"
            counter = 1
            for vid in self.currentLivestreams:
                sanitizedTitle = vid.title.replace('\"', '\"\"')
                csv_string += f"{counter},\"{sanitizedTitle}\",\"{vid.date}\",\"{vid.currentViewers}\",\"{vid.likes}\",{vid.URL}\n"
                counter += 1

        if len(self.livestreamVODs) > 0:
            csv_string += "LIVESTREAM VODS\n"
            csv_string += "Stream,Title,Date,Views,Likes,URL\n"
            counter = 1
            for vid in self.livestreamVODs:
                sanitizedTitle = vid.title.replace('\"', '\"\"')
                csv_string += f"{counter},\"{sanitizedTitle}\",\"{vid.date}\",\"{vid.views}\",\"{vid.likes}\",{vid.URL}\n"
                counter += 1

        return csv_string
    
    def __str__(self):
        info = ""

        info += f"Channel Title: {self.title}\n"
        info += f"About: {self.about}\n\n"
        info += f"Subscribers: {self.subCount}\n"
        totalVidsFound = len(self.videos) + len(self.premieringVideos) + len(self.scheduledVideos) + len(self.shorts) + len(self.livestreamVODs) + len(self.currentLivestreams) + len(self.scheduledLivestreams)
        info += f"Videos: {totalVidsFound}/{self.vidCount}\n"
        info += f"Views: {self.viewCount}\n"
        info += f"Join Date: {self.joinDate}\n\n"

        if len(self.socmedLinks) > 0:
            info += "Other Links:"
            for link in self.socmedLinks:
                info += f" {link[0]} - {link[1]}\n"
        else:
            info += "No External Links Detected.\n"

        return info

#Video Schema
class commonVideoInfo:
    def __init__(self, title=None, date=None, likes=None, URL=None):
        self.title = title
        self.date = date
        self.likes = likes
        self.URL = URL

class youtubeVideoInfo(commonVideoInfo):
    """Models information for a Normal Video, a Short, or a Livestream VOD"""
    def __init__(self, title=None, date=None, views=None, likes=None, commentCount=None, URL=None):
        super().__init__(title, date, likes, URL)
        self.views = views
        self.commentCount = commentCount

class youtubeCurrentInfo(commonVideoInfo):
    """Models a stream in progress or a premiering video at the time of scanning"""
    def __init__(self, title=None, date=None, currentViewers=None, likes=None, URL=None):
        super().__init__(title, date, likes, URL)
        self.currentViewers = currentViewers

class youtubeScheduledInfo(commonVideoInfo):
    """Models a stream or video pre-planned at the time of scanning"""
    def __init__(self, title=None, date=None, waiting=None, likes=None, URL=None):
        super().__init__(title, date, likes, URL)
        self.waiting = waiting