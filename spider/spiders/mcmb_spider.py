__author__ = 'Tomithy'

from scrapy.contrib.spiders import SitemapSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector



from tutorial.items import MCMBItem
from tutorial.pipelines import MCMBPipeline
from scrapy.conf import settings
import re


class MCMBSpider(SitemapSpider):
    name = "mcmb"
    allowed_domains = ["sites.google.com"]
    sitemap_urls = ['https://sites.google.com/a/mechanobio.info/mbinfo/system/feeds/sitemap']


    #DEBUG: Tracking crawling progress
    pagesCrawled = []
    pagesCrawledCount = 0
    filesNotPrinted = []

    def parse(self, response):

        # For tracking progress
        self.pagesCrawledCount += 1
        print "\n\n", str(self.pagesCrawledCount), "Now Crawling: ", str(response.url)
        self.pagesCrawled.append(str(response.url))


        # Uses Xpath selector to obtain the span node which contains the title. It selects by finding all <ul>
        # with id="JOT..." and all its child <li> that has class="sites..." and subsequently its child which are <span>
        hxs = HtmlXPathSelector(response)



        # Simple extract all the <a> tags from the page and check if they either have Download for their text() or has
        # a .csv extension, if they do we will store them in the MCMB item
        csvLinks2 = hxs.select("//a")

        for csvLink2 in csvLinks2:
            downloadChecker = csvLink2.select('text()').extract()
            filename = csvLink2.select('@href').extract()
            indexOfCsv = str(filename).find(".csv")
            if str(downloadChecker).count("DownLoad") or indexOfCsv > 0:

                fileURL = "https://sites.google.com" + str(filename)[3:-2]

                filename = str(filename).split("/")
                subString = filename[-1]            #filename is the last item in the list
                indexOfCsvInSubString = str(subString).find(".csv")
#                csvFilename = subString[:indexOfCsvInSubString+4] + "_" + str(self.pagesCrawledCount)
                csvFilename = subString[:indexOfCsvInSubString] + "_" + str(self.pagesCrawledCount) + ".csv"



                if csvFilename.find("_proteins") > 0:
                    #! Storing item in MCMB item
                    item = MCMBItem()
                    item['csvTitle'] = csvFilename
                    item['csvURL'] = fileURL
                    item['pageURL'] = str(response.url)
                    item['key'] = self.pagesCrawledCount
                    MCMBPipeline.process_item(MCMBPipeline(), item, self)
                else:
                    self.filesNotPrinted.append(csvFilename)



                print item


        items = [] #empty list to store items

        return items



    #For Debug Purposes
    newSession = True   #used to issue new .dat file for every session
    linkCounter = 1     #used to count the number of links extracted

    def print_to_file(self):
        import os.path
        import datetime

        printURLList = False


        if not os.path.exists("MCMBSpiderCrawlLog.txt") or self.newSession:
            printLog = open('urlLog.txt', 'w')
        else:
            printLog = open('urlLog.txt', 'a')

        printLog.write("CrawlSession @" + str(datetime.datetime) + " :\n")

        printString = "Total Pages Crawled: " + str(self.pagesCrawledCount)
        printLog.write("Total Pages Crawled: " + str(self.pagesCrawledCount))

#        roundCounter = 1
#        printString = "Pages Crawled: " + str(self.pagesCrawledCount) + "\n "
#        if not os.path.exists("urlLog.txt") or self.newSession:
#            printLog = open('urlLog.txt', 'w')
#            self.newSession = False
#        else:
#            printLog = open('urlLog.txt', 'a')
#        for urlStrings in urlList:
#            url = str(urlStrings.url)
#            printString += ' '.join((str(self.linkCounter), ",", str(roundCounter), ":", url, "\n"))
#            self.linkCounter += 1 ; roundCounter += 1
#        printString += "\n\n"
#        printLog.write(printString)
        printLog.close()



#if __name__ == '__main__':
#
##    spider = DmozSpider()
##    spider.parse()
#    pass