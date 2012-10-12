# Scrapy settings for tutorial project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/intro/tutorial.html
#

BOT_NAME = 'tutorial'
BOT_VERSION = '1.0'

CLOSESPIDER_PAGECOUNT = 0       # closes the spider when page count is reach. Since spider is async,
                                # the running count will be more

SPIDER_MODULES = ['tutorial.spiders']
NEWSPIDER_MODULE = 'tutorial.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

ITEM_PIPELINES = [
    'tutorial.pipelines.MCMBPipeline',
    ]

