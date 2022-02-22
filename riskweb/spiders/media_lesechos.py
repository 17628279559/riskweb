"""
回声报 爬虫
"""

import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaAftenpostenSpider(scrapy.Spider):
    name = 'media_lesechos'
    allowed_domains = ['lesechos.fr']
    
    def start_requests(self):
        BASEURL = "https://www.lesechos.fr"
        start_paths = [
            '/idees-debats',
            '/economie-france',
            '/elections',
            '/industrie-services',
            '/finance-marches',
            '/bourse',
            '/monde',
            '/tech-medias',
            '/start-up',
            '/politique-societe',
            '/pme-regions',
            '/patrimoine',
            '/weekend'
        ]
        # 发送请求
        for start_path in start_paths:
            yield scrapy.Request(BASEURL+start_path, self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):
        BASEURL = "https://www.lesechos.fr"
        #文章详情链接
        article_urls = response.xpath('//div[@class="jdkqq3-0 iNjvMT"]/article/div/a/@href').extract()
        for article_url in article_urls:
            yield scrapy.Request(BASEURL+article_url, self.parse_article, dont_filter=False)

        next_url = response.xpath('//ul[@class="sc-14kwckt-17 cxo6d5-5 drzpau"]/li[last()]/a/@href').extract_first()
        if next_url:
            yield scrapy.Request(BASEURL+next_url,self.parse_dictionary,dont_filter=True)

        #scrapy crawl media_lesechos
    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = '|'.join(response.xpath('//header/h1/text()').extract()).replace('\xa0','')
        item['media_name'] = '回声报'
        item['url'] = response.url

        item['topic'] =response.xpath('//ul[contains(@class,"sc-14kwckt-17 tez3o0-1")]/li[2]/a/text()').extract_first().strip()
        
        author = response.xpath('//div[contains(@class,"sc-78pc27-0")]/a').xpath('string(.)').extract()
        item['author'] = '|'.join(author).strip()

        # 匹配文章的发布时间
        publish_date = response.xpath('//div[contains(@class,"sc-AxjAm sc-1i0ieo8-1")]/span/text()').extract_first()
        #Publié le 6 août 2021 à 8:07
        #将法语月份替换
        month = ['janv.','févr.','mars','avr.','mai','juin',
                 'juil.','août','sept.','oct.','nov.','déc.']
        for i in range(12):
            publish_date = publish_date.replace(month[i],str(i+1))


        #Publié le 6 8 2021 à 8:07
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M", time.strptime(publish_date, "Publié le %d %m %Y à %H:%M")) #Publié le 6 8 2021 à 8:07
        
        raw_sentences = response.xpath('//div[contains(@class,"sc-1r87fjh-0")]/p | //div[contains(@class,"sc-1r87fjh-0")]/h3').xpath('string(.)').extract()
        if response.xpath('//div[contains(@class,"pgxf3b-2")]'):
            raw_sentences.append("此篇新闻需要付费订阅,只能爬取上述一部分")

        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip().replace('\xa0','')
        return item
