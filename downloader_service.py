import downloadimg
import sqlsql
import time

print(f'Download Service Started')
sql = sqlsql.MySQLClass()
downloader = downloadimg.Downloader(sql)
while True:
    #grabs the oldest 10 chapters to download from the queue
    queue = sql.getDownloadQueue()
    if queue is not None and len(queue) > 0:
        #todo retry function instead of clearing queues
        sql.deleteDownloadQueue(queue)
        queueObj = sql.deserialize_sql_dict(queue)
        downloader.downloadLinks(queueObj)
    else:
        #if queue is empty then rest 30s
        time.sleep(30)
