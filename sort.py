from sqlsql import MySQLClass
from mysql.connector import pooling
import re

class Sort:
    def __init__(self):
        self.sql = MySQLClass()
        self.sql.connect()

    def atof(self,text):
        try:
            retval = float(text)
        except ValueError:
            retval = text
        return retval

    def natural_keys(self, text):
        '''
        alist.sort(key=natural_keys) sorts in human order
        http://nedbatchelder.com/blog/200712/human_sorting.html
        (See Toothy's implementation in the comments)
        float regex comes from https://stackoverflow.com/a/12643073/190597
        '''
        return [ self.atof(c) for c in re.split(r'[+-]?([0-9]+(?:[.][0-9]*)?|[.][0-9]+)', text) ]

    def main_sort(self, options='True'):
        sqlquery = f"SELECT MangaTitle FROM mangaDatabase WHERE {options}"
        mycursor = self.sql.mycursor
        mycursor.execute(sqlquery,)
        extraInfo = mycursor.fetchall()
        for x in extraInfo:
            sortedString = ''
            unsort = self.sql.getExtraInformation(x["MangaTitle"])
            if unsort is None:
                continue
            trysorted = unsort.split(',')[:-1]
            trysorted = list(dict.fromkeys(trysorted))
            trysorted.sort(key = self.natural_keys)
            for y in trysorted:
                sortedString += f'{y},'
            self.sql.updateExtraInformation(x['MangaTitle'], sortedString,'off')

if __name__ == "__main__":
    sort = Sort()
    sort.main_sort()