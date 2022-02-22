"""
西班牙国家电视台 爬虫
"""

import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaAftenpostenSpider(scrapy.Spider):
    name = 'media_rtve'
    allowed_domains = ['rtve.es']
    start_urls = ["https://www.rtve.es/temas/"]
    
    def parse(self, response, **kwargs):
        BASEURL = "http://www.rtve.es"
        start_paths = response.xpath('//div[@class="wrapper bodier"]//aside//ul/li/a/@href').extract()
        # 发送请求
        for start_path in start_paths:
            yield scrapy.Request(BASEURL+start_path, self.parse_dictionary, dont_filter=True)


    def parse_dictionary(self, response):
        BASEURL = 'http://www.rtve.es'
        #文章详情链接
        urls = response.xpath('//article//h2/a/@href').extract()
        for article_url in urls:
            yield scrapy.Request(article_url, self.parse_article, dont_filter=False)

        next_url = response.xpath('//ul[@class="paginaBox"]/li/span[@class="ico arrow next_"]/a/@href').extract_first()
        if next_url:
            yield scrapy.Request(BASEURL+next_url,self.parse_dictionary,dont_filter=True)

    #scrapy crawl media_rtve
    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = response.xpath('//h1[@id="h1_maincontent"]/span/text() | //span[@class="maintitle"]/text()').extract_first()
        item['media_name'] = '西班牙国家电视台'
        item['url'] = response.url

        item['topic'] ="|".join(response.xpath('//div[@class="wrapper shortBox"]//li/a/text()').extract())

        author = response.xpath('//span[@class="name"]').xpath('string(.)').extract()
        author = [i.strip() for i in author]
        item['author'] = '|'.join(author)
        raw_sentences = []
        publish_date = response.xpath('//*[@class="pubBox"]/time/@datetime').extract_first()
        if publish_date:
            item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date.split('+')[0], "%Y-%m-%dT%H:%M:%S")) #2021-02-23T17:24:00+01:00
        elif response.xpath('//div[@id="tVP"]'):
            raw_sentences.append("这条新闻是个视频")
            item['publish_date'] = ''
        else:
            publish_date = ' '.join(response.xpath('//div[@class="content"]//span[@class="duration"]/text() | //div[@class="content"]//span[@class="datemi"]/text()').extract())
            if publish_date:
                item['publish_date'] = time.strftime("%Y/%m/%d %H:%M", time.strptime(publish_date, "%d.%m.%Y %H:%M")) #23.07.2021 02:43
        
        if not raw_sentences:
            raw_sentences = response.xpath('//div[@class="artBody"]/* | //div[@class="mainDescription"]/*').xpath('string(.)').extract()
            raw_sentences = [i.strip().replace('\xa0','').replace('\t','').replace('\r','').replace('\n','') for i in raw_sentences]
            raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip()
        return item
