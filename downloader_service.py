import downloadimg
import sqlsql
import time

print(f'Download Service Started')
sql = sqlsql.MySQLClass()
downloader = downloadimg.Downloader(sql)
while True:
    queue = sql.getDownloadQueue()
    if queue is not None and len(queue) > 0:
        #todo retry function instead of clearing queues
        sql.deleteDownloadQueue(queue)
        queueObj = sql.deserialize_sql_dict(queue)
        downloader.downloadLinks(queueObj)
    else:
        time.sleep(30)
