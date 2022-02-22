"""
20 分钟报 爬虫
"""
import scrapy
from scrapy.http import HtmlResponse
import time
import logging
import json
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)


class MeidaAdnkronosSpider(scrapy.Spider):
    name = 'media_20minutes'
    allowed_domains = ['20minutes.fr']
    start_urls = ['https://www.20minutes.fr/v-ajax/menu-panel']   #新闻分类总菜单 也是异步加载的

    #经过反复测试，发现一级分类的所有新闻并不全面，只包含一部分二级分类的新闻
    #如/sport/下面所有新闻共48条
    #而/sport/basketball/  、  /sport/biathlon/  、  /sport/jo-2020/  等十余个二级分类下面所有新闻加起来有几百条
    #所以决定爬取所有二级分类

    def parse(self, response, **kwargs):

        # 以下三个一级分类无二级分类，单独写出来
        start_urls = [
            'https://www.20minutes.fr/insolite/',
            'https://www.20minutes.fr/diaporama/',
            'https://www.20minutes.fr/voyage/'
            ]

        #重新构造response
        rs =  json.loads(response.text)
        response=HtmlResponse(url=response.url,body=rs,encoding='utf-8')
        start_urls.extend(response.xpath('//ul[@class="menu-list"]/li/a/@href').extract())

        #二级分类共144个，加上3个一级分类，非本域名的网址直接过滤掉，没有新闻的网页在下面也会过滤
        for url in start_urls:
            yield scrapy.Request(url, self.parse_dictionary,dont_filter=True)
            
            
            
    #scrapy crawl media_20minutes
    def parse_dictionary(self, response):
        BASEURL = 'https://www.20minutes.fr'
        #处理一开始就能看到的10条新闻
        if not re.search( r'ajax', response.url):
            article_urls = response.xpath('//article/a/@href').extract()
            for article_url in article_urls:
                yield scrapy.Request(BASEURL + article_url, self.parse_article, dont_filter=False)
            
            nextpage_url = response.xpath('//div[@class="infinite-more"]/@data-href').extract_first()
            if nextpage_url is not None:
                yield scrapy.Request(BASEURL + nextpage_url, self.parse_dictionary,meta={'id':19},dont_filter=True)
        #处理异步加载的网页
        else:
            if not response.xpath('//div[@class="error-page"]'):
                rs = json.loads(response.text)
                article_urls = []
                for i in rs['contents']:
                    html = i['content']
                    x=HtmlResponse(url=response.url,body=html,encoding='utf-8')
                    article_urls.extend(x.xpath('//article/a/@href').extract())
                    
                for article_url in article_urls:
                    yield scrapy.Request(BASEURL + article_url, self.parse_article, dont_filter=False)
                nextpage_url = '/'.join(response.url.split('/')[0:-1]) + '/' + str(response.meta['id'])
                yield scrapy.Request(nextpage_url, self.parse_dictionary,meta={'id':response.meta['id']+10},dont_filter=True)

    def parse_article(self, response):
        # 调取参数
        item = ArticleItem()
        # 进入每篇文章header部分

        item['title'] = response.xpath('//header/h1/text()').extract_first().strip().replace('\xa0','')
        item['media_name'] = '20 分钟报'
        item['url'] = response.url

        topics = response.xpath('//div[contains(@class,"lt-endor-body content")]/ul/li//text()').extract()
        item['topic'] = '|'.join(topics)

        item['author'] = response.xpath('//span[@class="author-name"]/text()').extract_first()

        publish_date = response.xpath('//p[@class="datetime"]//time/@datetime').extract() #2021-08-06T07:05:03+02:00
        #爬取的时间一般有两个，一个发布，一个更新，有的只有一个

        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S",
                                                 time.strptime(publish_date[0].split('+')[0], "%Y-%m-%dT%H:%M:%S"))  #2021-08-06T07:05:03
        raw_sentences=[]
        p = response.xpath('//div[@class="qiota_reserve content"]/p | //div[@class="qiota_reserve content"]/h2')
        if not p:
            p = response.xpath('//div[contains(@class,"lt-endor-body content")]/p')
            
        for i in p:
            data = i.xpath('string(.)').extract()
            if data:
                raw_sentences.append(''.join(data))

        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).replace('\xa0','')

        return item