"""
西班牙广播公司电台 爬虫
"""

import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaAftenpostenSpider(scrapy.Spider):
    name = 'media_cadenaser'
    allowed_domains = ['cadenaser.com']
    
    def start_requests(self):
        BASEURL = "https://cadenaser.com/tag/listado/"
        start_paths = ['9','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        # 发送请求
        for start_path in start_paths:
            yield scrapy.Request(BASEURL+start_path+'.html', self.parse_catalogue, dont_filter=True)

        #话题非常多，有几万个
    def parse_catalogue(self, response):
        BASEURL = "https://cadenaser.com"
        #文章详情链接
        catalogue_urls = response.xpath('//ul[@id="listado"]/li/a/@href').extract()
        for catalogue_url in catalogue_urls:
            yield scrapy.Request(BASEURL+catalogue_url, self.parse_dictionary,meta={'url':BASEURL+catalogue_url,'next':-1}, dont_filter=True)

    def parse_dictionary(self, response):
        BASEURL = "https://cadenaser.com"
        #文章详情链接
        urls = response.xpath('//article//h2/a/@href').extract()
        for article_url in urls:
            yield scrapy.Request(article_url, self.parse_article, dont_filter=False)
        if response.xpath('//li/a[@title="Cargar más"]'):
            next = response.meta['next']
            if next == -1:
                next = int(response.xpath('//li/a[@title="Cargar más"]/@data-next').extract_first())
            elif next>0:
                next_url = response.meta['url']+str(next)
                if next_url:
                    yield scrapy.Request(next_url,self.parse_dictionary,meta={'url':response.meta['url'],'next':next-1},dont_filter=True)

    #scrapy crawl media_cadenaser
    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = '|'.join(response.xpath('//header/h1/text()').extract()).replace('\xa0','')
        item['media_name'] = '西班牙广播公司电台'
        item['url'] = response.url

        item['topic'] ='|'.join(response.xpath('//section[@class="cnt-modulo lst-keywords"]/ul/li/a/text()').extract())
        
        author = response.xpath('//div[@class="autor"]/a').xpath('string(.)').extract()
        item['author'] = '|'.join(author).strip()

        # 匹配文章的发布时间
        publish_date = response.xpath('//div[@class="cnt-metas"]/time').xpath('string(.)').extract_first().strip().replace('\xa0','').replace(' ','')
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M", time.strptime(publish_date.split('.')[0], "%d/%m/%Y-%H:%Mh")) #24/06/2021-14:44h. 
        
        raw_sentences = response.xpath('//div[@class="cnt-body"]//p').xpath('string(.)').extract()
        raw_sentences = [i.strip().replace('\xa0','').replace('\t','').replace('\r','') for i in raw_sentences]
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip().replace('\xa0','')
        return item
