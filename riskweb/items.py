# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

#定义数据爬取字段
class ArticleItem(scrapy.Item):
    title = scrapy.Field()
    topic = scrapy.Field()
    publish_date = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    media_name = scrapy.Field()
    author = scrapy.Field()
