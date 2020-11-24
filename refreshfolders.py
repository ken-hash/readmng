import os
'''
Refreshing date modified by opening all folders in downloads 
'''
class RefreshIt:
    def refresh(self):
        path = os.path.realpath('downloads')
        listfolders = os.listdir(path)
        for folder in listfolders:
            newpath = path + '\\' + folder
            pass