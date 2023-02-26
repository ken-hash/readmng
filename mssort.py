from mssql import MSSQLClass
import datetime
import re
import copy
import sys
import random

class Sort:
    def __init__(self, title):
        self.sql = MSSQLClass()
        self.sql.connect()
        self.title = title
        self.mssql = []
        self.retries = 0
        self.lastChap = None

    def atof(self,text):
        try:
            retval = float(text)
        except ValueError:
            retval = 0
        return retval

    #sort by number in string atof to put all string as first entry
    def natural_keys(self, text):
        return [ self.atof(c) for c in re.split(r'[+-]?([0-9]+(?:[.][0-9]*)?|[.][0-9]+)', text) ]

    def main_sort(self):
        self.mssql = self.sql.getAllMangaLogs(self.title)
        if self.mssql is None or len(self.mssql)==0:
            raise Exception(f'{self.title} not recognised')
        self.unsorted = [row['MangaChapter'] for row in self.mssql]
        self.sorted = copy.deepcopy(self.unsorted)
        self.sorted.sort(key = self.natural_keys)
        dateTime = None
        id = None
        for elem in range(len(self.sorted)):
            #if sorted elem doesnt match unsorted elem then
            if self.sorted[elem]!=self.unsorted[elem]:
                #if retry count goes more than 3 then force next elem in db to change datetime
                if self.lastChap == self.sorted[elem]:
                    self.retries += 1
                else:
                    self.lastChap = self.sorted[elem]
                    self.retries = 0
                if self.retries >=3:
                    for chap in self.mssql:
                        if chap['MangaChapter'] == self.unsorted[elem+1]:
                            unsortedNext = chap
                    dateTime = unsortedNext['DateTime'] - datetime.timedelta(milliseconds=random.randint(1,20))
                    id = unsortedNext['MangaLogId']
                    self.sql.UpdateMangaLogDateTime(id,dateTime)
                    self.main_sort()
                #if sorted elem is inserted then change datetime to previous db elem + 1 microsecond
                if elem != 0:
                    previousSortedChapter = self.unsorted[elem-1]
                    for chap in self.mssql:
                        if chap['MangaChapter'] == previousSortedChapter:
                            dateTime = chap['DateTime'] + datetime.timedelta(microseconds=1)
                        if chap['MangaChapter'] == self.sorted[elem]:
                            id = chap['MangaLogId']
                        if dateTime is not None and id is not None:
                            self.sql.UpdateMangaLogDateTime(id,dateTime)
                            self.main_sort()
                #if sorted elem is the first elem then change its datetime to 1 millisecond earler than db first elem value
                else:
                    unsortedFirst = self.mssql[0] 
                    for chap in self.mssql:
                        if chap['MangaChapter'] == self.sorted[elem]:
                            sortedFirst = chap
                    dateTime = unsortedFirst['DateTime'] - datetime.timedelta(milliseconds=1)
                    id = sortedFirst['MangaLogId']
                    self.sql.UpdateMangaLogDateTime(id,dateTime)
                    self.main_sort()

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 0:
        for arg in args:
            Sort(arg).main_sort()
    else:
        allManga = MSSQLClass().getAllMangas()
        for manga in allManga:
            Sort(manga['Name']).main_sort()
