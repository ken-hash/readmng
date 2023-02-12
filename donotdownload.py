import io
import os
import json

class donotdownload():
    def __init__(self):
        self.exclusionDict = {}
        if os.path.exists('donotdownload.json'):
            self.exclusionDict = self.loadFromFile()
        else:
            self.saveToFile()

    def addToList(self,manga,chapter):
        if manga in self.exclusionDict:
            if chapter in self.exclusionDict[manga]:
                return False
            else:
                self.exclusionDict[manga].append(chapter)
        else:
            self.exclusionDict[manga] = [chapter]
        self.saveToFile()

    def getList(self,manga):
        if manga in self.exclusionDict:
            return self.exclusionDict[manga]
        else:
            return []

    def saveToFile(self):
        writeJson = json.dumps(self.exclusionDict, indent=4)
        with open('donotdownload.json','w') as f:
            f.write(writeJson)

    def loadFromFile(self):
        with open('donotdownload.json','r') as f:
            readJson = f.read()
        return json.loads(readJson)

    