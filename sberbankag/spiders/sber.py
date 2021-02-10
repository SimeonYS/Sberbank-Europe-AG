import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from ..items import SberbankagItem
import re

pattern = r'(\r)?(\n)?(\t)?(\xa0)?'

class SberSpider(scrapy.Spider):
    name = 'sber'

    start_urls = ['https://www.sberbank.at/press-releases/']

    def parse(self, response):
        links = response.xpath('//div[@class="view-content"]//h2/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//div[@class="item-list"]//a[@title="Go to next page"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)
    def parse_article(self, response):
        item = ItemLoader(SberbankagItem())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@class="panel-pane pane-node-title"]/h1/text()').get()
        date = response.xpath('//div[@class="article-date"]/text()').get()
        content = ''.join(response.xpath('//div[@property="content:encoded"]//text()').getall())
        content = re.sub(pattern, "", content)


        item.add_value('date', date)
        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()