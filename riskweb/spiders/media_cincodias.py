"""
五天报 爬虫
"""

import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaAftenpostenSpider(scrapy.Spider):
    name = 'media_cincodias'
    allowed_domains = ['cincodias.elpais.com']
    start_urls = ["https://cincodias.elpais.com"]
    
    def parse(self, response, **kwargs):
        BASEURL = "https://cincodias.elpais.com"
        start_paths = response.xpath('//div[@class="menu-col"]//li[not(@class)]/a/@href').extract()[0:69]
        # 发送请求
        for start_path in start_paths:
            if re.search(r'//',start_path):
                yield scrapy.Request('https:'+start_path, self.parse_dictionary, dont_filter=True)
            elif re.search(r'http',start_path):
                yield scrapy.Request(start_path, self.parse_dictionary, dont_filter=True)
            else:
                yield scrapy.Request(BASEURL+start_path, self.parse_dictionary, dont_filter=True)


    def parse_dictionary(self, response):
        BASEURL = 'https://cincodias.elpais.com'
        #文章详情链接
        urls = response.xpath('//div[@class="articulo__interior"]//h2/a/@href').extract()
        for article_url in urls:
            yield scrapy.Request(BASEURL+article_url, self.parse_article, dont_filter=False)

        next_url = response.xpath('//li[@class="paginacion-siguiente activo"]/a/@href').extract_first()
        if next_url:
            yield scrapy.Request(next_url,self.parse_dictionary,dont_filter=True)

    #scrapy crawl media_cincodias
    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = '|'.join(response.xpath('//div[@class="articulo-titulares"]/h1/text()').extract())
        item['media_name'] = '五天报'
        item['url'] = response.url

        item['topic'] ="|".join(response.xpath('//li[@itemprop="keywords"]/a/text()').extract())

        author = response.xpath('//*[@class="articulo-localizacion"]/text()').extract()
        author = [i.strip() for i in author]
        item['author'] = '|'.join(author)

        publish_date = response.xpath('//div[@class="articulo-datos"]/time/@datetime').extract_first()

        # 匹配文章的发布时间
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date.split('+')[0], "%Y-%m-%dT%H:%M:%S")) #2021-08-19T08:48:46+02:00
        
        raw_sentences = response.xpath('//div[@class="articulo-cuerpo"]/p').xpath('string(.)').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        raw_sentences = [i.strip() for i in raw_sentences]
        item['content'] = '\n'.join(raw_sentences).strip()
        return item
