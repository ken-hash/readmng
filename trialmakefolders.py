import os
def checkdirectory(title,chapter):
    path = "manga/"+ title +"/"+chapter
    return(os.path.isdir(path))

def createdirectory(title,chapter):
    path = "manga/" + title +"/"+chapter
    os.makedirs(path)
    return True


print(checkdirectory('solo leveling 3','292'))
#createdirectory('one punch man','1')