# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

#import tutorial.spiders.database.databaseProcesses as db

class MCMBPipeline(object):

    spiderItemStore = []
    _downloadFileFlag = True
    _numFilesDownloaded = 0
#    _rawSpiderDB = None
#

    def process_item(self, item, spider):

        if self._downloadFileFlag:

            print "Pipeline: Downloading CSV:", item['csvTitle'], " from ", item['csvURL']
            self.spiderItemStore.append( [item['key'], item['csvTitle'], item['csvURL']] )
            self.downloadFile(item["csvURL"], item['csvTitle'])
            self._numFilesDownloaded +=1

        return item

    def open_spider(self, spider):

        # These cleans up the downloadedFiles folder of any csv file.
        # Necessary due to the async/random crawl nature of spider, which makes file naming random
        import os
        from glob import glob
        for f in glob ('downloadedFiles/*.csv'):
            os.unlink (f)


    def close_spider(self, spider):

        print "Session Ended | Total files downloaded: ", self._numFilesDownloaded, "| Total pages crawled: ", spider.pagesCrawledCount
        self.writeSessionFile()

#        print  "MCMB spider is closing! Downloading all files now!"
#        url = "https://sites.google.com/a/mechanobio.info/mbinfo/Home/glossary-of-terms/mechano-glossary--a/mechano-glossary-adherens-junction/adherensjunction_proteins.csv?attredirects=0&d=1"
#        fileName = "adherensjunction_proteins.csv"
#        self.downloadFile(url, fileName)

        #run tests for spider
        from tests.spiderTests import spider_tests

#        spider_tests(spider)



    def downloadFile(self, url, fileName):
        import urllib2

        downloadFile = urllib2.urlopen(url)
        output = open('downloadedFiles/' + fileName, 'wb')
        output.write(downloadFile.read())
        output.close()
        pass

    def writeSessionFile(self):
        out_file = open("downloadedFiles/listOfCsv.txt", "wt")
        for item in self.spiderItemStore:
            item[0] = str(item[0])
            out_file.write(",".join(item) + "\n" )
        out_file.close()
