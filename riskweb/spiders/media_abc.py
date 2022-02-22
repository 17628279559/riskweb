"""
阿贝赛报 爬虫
"""

import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaAftenpostenSpider(scrapy.Spider):
    name = 'media_abc'
    allowed_domains = ['abc.es']
    
    def start_requests(self):
        BASEURL = "https://www.abc.es"
        start_paths = [
            '/espana/',
            '/economia/',
            '/internacional/',
            '/sociedad/',
            '/cultura/',
            '/historia/',
            '/ciencia/',
            '/gente/',
            '/play/'
        ]
        # 发送请求
        for start_path in start_paths:
            yield scrapy.Request(BASEURL+start_path, self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):
        BASEURL = "https://www.abc.es"
        #文章详情链接
        article_urls = response.xpath('//article/a/@href').extract()
        for i in article_urls:
            if re.search(r'http',i) and re.search(r'html',i):
                yield scrapy.Request(i, self.parse_article, dont_filter=False)
            elif re.search(r'html',i):
                yield scrapy.Request(BASEURL+i, self.parse_article, dont_filter=False)
            else:
                pass
        next_url = response.xpath('//ul[@class="paginacion-portada"]//a[@title="Siguiente"]/@href').extract_first()
        if next_url:
            yield scrapy.Request(BASEURL+next_url, self.parse_dictionary, dont_filter=True)

        #scrapy crawl media_abc
    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = '|'.join(response.xpath('//*[@class="main"]//h1//text()').extract()).replace('\xa0','')
        item['media_name'] = '阿贝赛报'
        item['url'] = response.url

        item['topic'] ='|'.join(response.xpath('//*[@class="modulo temas"]/ul/li//text()').extract())
        
        author = response.xpath('//*[@class="autor"]/a[@class="nombre"]/text()').extract()
        if author:
            item['author'] = '|'.join(author).strip()
        else:
           item['author'] =''

        # 匹配文章的发布时间
        publish_date = response.xpath('//time[@class="actualizado"]/@datetime').extract_first()
        #2021-08-12T17:55:20Z
        if publish_date:
            item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date[0:-1], "%Y-%m-%dT%H:%M:%S")) #2021-08-12T17:55:20
        else:
            item['publish_date'] = ""
        raw_sentences = response.xpath('//*[contains(@class,"cuerpo-texto")]/p | //*[contains(@class,"cuerpo-texto")]/h3 | //div[contains(@class,"entrada-directo")]').xpath('string(.)').extract()
        if response.xpath('//*[contains(@class,"cuerpo")]/aside[@class="cierre-suscripcion "]'):
            raw_sentences.append("此篇新闻需要付费订阅,只能爬取上述一部分")
        if response.xpath('//*[@class="detalle-video "]'):
            raw_sentences.append("此篇新闻是个视频")
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip().replace('\xa0','')
        return item



