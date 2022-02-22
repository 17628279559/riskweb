"""
先锋报 爬虫
"""

import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaAftenpostenSpider(scrapy.Spider):
    name = 'media_lavanguardia'
    allowed_domains = ['lavanguardia.com']
    start_urls = ["https://www.lavanguardia.com"]
    
    def parse(self, response, **kwargs):
        BASEURL = "https://www.lavanguardia.com"
        start_paths = response.xpath('//div[@class="hamburger-menu container"]//li/a/@href').extract()
        # 发送请求
        for start_path in start_paths:
            yield scrapy.Request(start_path, self.parse_dictionary, dont_filter=True)


    def parse_dictionary(self, response):
        BASEURL = 'https://www.lavanguardia.com'
        #文章详情链接
        urls = response.xpath('//article//h2/a/@href').extract()
        for article_url in urls:
            if re.search(r'http',article_url) and not re.search(r'agenda',article_url):
                yield scrapy.Request(article_url, self.parse_article, dont_filter=False)
            elif not re.search(r'agenda',article_url):
                yield scrapy.Request(BASEURL+article_url, self.parse_article, dont_filter=False)

        next_url = response.xpath('//div[@class="pagination"]//li[@class="next"]/a/@href').extract_first()
        if next_url:
            yield scrapy.Request(BASEURL+next_url,self.parse_dictionary,dont_filter=True)

    #scrapy crawl media_lavanguardia
    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = response.xpath('//div[@class="title-container"]/h1/text()').extract_first()
        item['media_name'] = '先锋报'
        item['url'] = response.url

        item['topic'] ="|".join(response.xpath('//div[@class="supra-title-container"]/h2/text()').extract())

        author = response.xpath('//div[@class="author-name"]').xpath('string(.)').extract()
        author = [i.strip() for i in author]
        item['author'] = '|'.join(author)

        publish_date = response.xpath('//div[@class="date-time"]/time/@datetime').extract_first()

        # 匹配文章的发布时间
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date.split('+')[0], "%Y-%m-%dT%H:%M:%S")) #2021-07-15T08:26:10+02:00
        
        raw_sentences = response.xpath('//div[@class="article-modules"]/p | //div[@class="article-modules"]/span/p').xpath('string(.)').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        raw_sentences = [i.strip().replace('\xa0','').replace('\t','').replace('\r','') for i in raw_sentences]
        item['content'] = '\n'.join(raw_sentences).strip()
        return item
