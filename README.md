Simple scrapping scripts

Copy of my personal manga scraper used to download manga into local computer

downloader_service.py to be used as service
 --- checks downloadqueues and download 10 oldest manga chapter queues into computer

checkhome.py 
 --- can be used as a service
   --- periodically check if theres a newly added manga in the db then sync off missing chapters 
        into local computer
   --- if there is no newly added manga then check readmng site for newly updated manga
        then syncs off missing chapters

sqlsqlsqlsql.py
 --- script to manually check all/individual manga and sync up missing chapters

redownloader.py
 --- script to manually check manga folder of corrupted/empty downloaded images and attempts to redownload.

sort.py
 --- script to sort mangachapters in db

mmsort.py
 --- script to manually sort all/individual manga chapters in webserver db