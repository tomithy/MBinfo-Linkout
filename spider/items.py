# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class MCMBItem(Item):
    pageURL = Field()
    csvTitle = Field()
    csvURL = Field()  #may have more than one csv per page.
    key = Field()     #since each page is only crawled one an integer representing the crawl index of page is used as key

