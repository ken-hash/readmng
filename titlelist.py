import os
#to be run once generates manga titles to be used incase mapping doesnt work
#reads links from listmanga into generate what manga title would be suitable to be used

path = os.path.realpath(r'readmng\listmanga.txt')
file = open(path,'r', encoding='utf-8')
data = file.read().split('\n')
file.close()

myManga = {
    'realtitle' : [],
    'title' : []
}

for lines in data:
    if len(lines) < 2:
            myManga['realtitle'].append('\n'+lines.upper())
            myManga['title'].append('Titles to use'+'\n')
    else:
        myManga['realtitle'].append(lines.split(' - ')[0])
        temptitles = lines.split(' - ')[-1].split('/')[-1]
        newtitles = temptitles.replace('-',' ')
        myManga['title'].append(newtitles)

write = 'Manga Title - Titles to use'
for x in range(len(myManga['realtitle'])):
    write+='{:<50} - {:>6s}'.format(myManga['realtitle'][x],myManga['title'][x])+'\n'
    
path = os.path.realpath(r'readmng\listTitles.txt')
file = open(path,'w',encoding='utf-8')
file.write(write)
file.close()