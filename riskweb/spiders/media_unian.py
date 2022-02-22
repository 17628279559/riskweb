import scrapy
from scrapy import Request
import json
import logging
import time
from scrapy.selector import Selector
import requests
from scrapy.http import HtmlResponse
import time
from selenium import webdriver
from riskweb.items import ArticleItem


logger = logging.getLogger(__name__)

class MediaUnianSpider(scrapy.Spider):
    name = 'media_unian'
    allowed_domains = ['unian.net']
    
    def __init__(self):
        super(MediaUnianSpider,self).__init__(name='media_unian')
        # 在scrapy中创建driver对象，尽可能少的创建该对象。
        # 1. 在初始化方法中创建driver对象；
        # 2. 在open_spider中创建deriver对象；
        # 3. 不要将driver对象的创建放在process_request()；
        option=webdriver.ChromeOptions()
        option.headless=True
        self.driver = webdriver.Chrome(options=option)

    def start_requests(self):
        urls = ['https://covid.unian.net/',
                'https://www.unian.net/politics/',
                'https://www.unian.net/economics/',
                'https://www.unian.net/war/',
                'https://www.unian.net/ecology/',
                'https://www.unian.net/insurance/',
                'https://www.unian.net/kyiv/',
                'https://www.unian.net/lvov/',
                'https://www.unian.net/dnepropetrovsk/',
                'https://www.unian.net/kharkiv/',
                'https://www.unian.net/odessa/',
                'https://www.unian.net/society/',
                'https://www.unian.net/world/',
                'https://www.unian.net/science/',
                'https://www.unian.net/incidents/',
                'https://health.unian.net/',
                'https://www.unian.net/curiosities/']
        
        for url in urls:
            for i in range(1,4):#控制分页 
                yield Request(url = url+'?page='+str(i),callback = self.parse_mod)
            
    def parse_mod(self,response):
        urls = response.xpath('//div[@class="list-thumbs__info"]//h3/a/@href').extract()
        yield{
                'items':urls
        }
        for url in urls:
            headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            resp = requests.get(url,headers = headers)
            temp = HtmlResponse(url=url, encoding='utf8', body=resp.text)
    
            date = temp.xpath('//div[@class="article__info-item time "]/text()').extract()[0].strip().split()
            date = '20'+date[1][-2:]+'/'+ date[1][-5:-3] + '/'+ date[1][-8:-6]+' '+date[0][:-1]+':00'
            title = temp.xpath('//h1[1]/text()').extract()[0]
            raw_sentences = temp.xpath('//div[@class="article-text  "]//p/text()').extract()
            editor = temp.xpath('//a[@class="article__author-name"]/text()').extract()[0]
            tags = temp.xpath('//div[@class="article__tags "][1]//text()').extract()
            raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
            item = ArticleItem()
            item['content'] = '\n'.join(raw_sentences).strip()
            item['media_name'] = '乌克兰独立新闻社'
            item['url'] = temp.url
            item['author'] = editor
            item['publish_date'] = date
            item['title'] = title
            item['topic'] = tags
            yield item
                
                