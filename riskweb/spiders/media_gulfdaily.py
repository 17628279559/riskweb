'''
海湾日报 爬虫
已完成
'''
import scrapy
from riskweb.items import ArticleItem
import json
import logging
import time
import re
logger = logging.getLogger(__name__)

class MediaGulfdailySpider(scrapy.Spider):
    name = 'media_gulfdaily'
    allowed_domains = ['gdnonline.com']
    start_urls = ['http://gdnonline.com/index.html']

    def parse(self,response):
        base_url = 'https://www.gdnonline.com'
        # 无下拉框
        main_menu = response.xpath('//ul[@id="menu-main-menu"]/li/a/@href').extract()
        # 有下拉框
        sub_menu = response.xpath('//ul[@class="sub-menu"]/li/a/@href').extract()

        urls = main_menu + sub_menu
        for url in urls:
            yield scrapy.Request(base_url+url,self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self,response):
        base_url = 'https://www.gdnonline.com' 
        articles = response.xpath('//article/div[@class="penci_post_thumb"]/a/@href').extract()
        home_articles = response.xpath('//a[contains(@href,/Details/)]').extract()
        if articles:
            # 普通界面（文章列表）
            for article in articles:
                yield scrapy.Request(base_url+article,self.parse_article, dont_filter=True)
        elif home_articles:
            # 主页文章        
            for article in home_articles:
                yield scrapy.Request(base_url+article,self.parse_article, dont_filter=True)
        else:
            return self

    def parse_article(self,response):
        # 获取参数
        item = ArticleItem()
        # 进入文章页面匹配相关参数
        item['title'] = response.xpath('//h1[@class="entry-title penci-entry-title penci-title-"]/text()').extract_first()
        item['media_name'] = '海湾日报'
        item['url'] = response.url
        item['topic'] = response.xpath('//div[@class="penci-entry-categories"]//a[@rel="category tag"]/text()').extract()
        item['author'] = ' '.join(response.xpath('//span[@class="author vcard"]/a/text()').extract()).replace('By ','')

        publish_date = response.xpath('//header[contains(@class,"entry-header")]//time/@datetime').extract_first()
        # 2017-12-05T03:29:21+00:00
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S",time.strptime(publish_date, "%Y-%m-%dT%H:%M:%S+00:00"))
        
        subscribe = response.xpath('//img[@alt="Subscribe"]')
        if subscribe:
            # 需要订阅
            subscribe_content=response.xpath('//div[@class="penci-entry-content entry-content"]/text()').extract_first().strip()
            item['content'] = '此篇文章需要付费\n'+subscribe_content
        else:
            # 无需订阅
            raw_sentences = response.xpath('//div[@class="penci-entry-content entry-content"]/p/text()').extract()
            raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
            item['content'] = '\n'.join(raw_sentences).strip()
        return item
        