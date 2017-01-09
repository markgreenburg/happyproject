"""
Spider class module for finding Ra Sushi's happy hour times by day of week.
"""
# to run via Bash: scrapy crawl happy -o happy.json. Make sure to install
# scrapy first. saves output as json but make sure to delete old json file
# first.

# framework for scraping
import scrapy

# create a new scraper as subclass of the scrapy scraper superclass
class HappySpider(scrapy.Spider):
    """
    Spider subclass. Crawls through pages looking for strings containing day of
    week
    """
    # each scraper must have unique name
    name = "happy"
    # here's the list of URLS that are going to get scraped
    start_urls = [
        'http://rasushi.com/menu/happy-hour/'
    ]

    # parse the results of the HappySpider object instance
    def parse(self, response):
        # yield gives us a generator instead of a saved list. It's kind of like
        # a 'return' but doesn't remember the whole list.
        yield {
            # scrapy can use CSS or xpath selectors, but xpath is more flexible
            # so we're going to use those. extract_first() simply extracts the
            # first instance, extract() would give all instances that are found
            # on the page.
            'monday': response.xpath("//*[starts-with(., 'MONDAY')]")\
            .extract_first(),
            'tuesday': response.xpath("//*[starts-with(., 'TUESDAY')]")\
            .extract_first(),
            'wednesday': response.xpath("//*[starts-with(., 'WEDNESDAY')]")\
            .extract_first(),
            'thursday': response.xpath("//*[starts-with(., 'THURSDAY')]")\
            .extract_first(),
            'friday': response.xpath("//*[starts-with(., 'FRIDAY')]")\
            .extract_first(),
            'saturday': response.xpath("//*[starts-with(., 'SATURDAY')]")\
            .extract_first(),
            'sunday': response.xpath("//*[starts-with(., 'SUNDAY')]")\
            .extract_first()
        }

    #####
    # Sample code for following links and scraping them as well
    #####
    # next_page = response.css('li.next a::attr(href)').extract_first()
    #     if next_page is not None:
    #         next_page = response.urljoin(next_page)
    #         yield scrapy.Request(next_page, callback=self.parse)
