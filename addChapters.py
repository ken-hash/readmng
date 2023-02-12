import requests

class MangaRequests:
    def __init__(self) -> None:
        self.endpoint = r'http://192.168.50.11/api/MangaChapters/AddChapter'

    def createPayload(self, manga, chapter, path):
        self.payload = {
            "Name": manga,
            "MangaChapter": chapter,
            "Path": path
        }

    def sendRequest(self):
        return requests.post(self.endpoint,json=self.payload)

