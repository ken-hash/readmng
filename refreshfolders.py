import os
'''
Refreshing date modified by opening all folders in downloads 
'''
class RefreshIt:
    def refresh(self):
        path = os.path.realpath('downloads')

        if not os.path.isdir(path):
            try:
                listfolders = os.listdir(path)
                os.makedirs(path)
                for folder in listfolders:
                    print(f'Refreshing folders of {folder}')
            except:
                return


RefreshIt().refresh()