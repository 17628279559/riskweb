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


class MediaUkrinformSpider(scrapy.Spider):
    name = 'media_ukrinform'
    allowed_domains = ['ukrinform.net']
    
    def __init__(self):
        super(MediaUkrinformSpider,self).__init__(name='media_ukrinform')
        # 在scrapy中创建driver对象，尽可能少的创建该对象。
        # 1. 在初始化方法中创建driver对象；
        # 2. 在open_spider中创建deriver对象；
        # 3. 不要将driver对象的创建放在process_request()；
        option=webdriver.ChromeOptions()
        option.headless=True
        self.driver = webdriver.Chrome(options=option)
    
    def start_requests(self):
        urls = ['https://www.ukrinform.net/rubric-polytics',
                'https://www.ukrinform.net/rubric-economy',
                'https://www.ukrinform.net/rubric-defense',
                'https://www.ukrinform.net/rubric-society',
                'https://www.ukrinform.net/rubric-sports']
        
        for url in urls:
            yield Request(url = url,callback = self.parse_article)
            
    def parse_article(self,response):
        base_url = 'https://www.ukrinform.net'
        urls = response.xpath('//h2/a/@href').extract()
        yield{
            'items':urls
        }
        for url in urls:
            headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            resp = requests.get(base_url+url,headers = headers)
            temp = HtmlResponse(url=base_url+url, encoding='utf8', body=resp.text)
            date = temp.xpath('//time/text()').extract()[0].strip().split()
            date = date[0][-4:]+'/' + date[0][-7:-5] +'/'+date[0][:2]+' ' + date[1]+':00'
            title = temp.xpath('//h1[1]/text()').extract()[0]
            raw_sentences = temp.xpath('//div[@class="newsText"][1]//text()').extract()
            raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
            item = ArticleItem()
            item['content'] = '\n'.join(raw_sentences).strip()
            item['media_name'] = '乌克兰独立新闻社'
            item['url'] = temp.url
            item['author'] = ' '
            item['publish_date'] = date
            item['title'] = title
            item['topic'] = ' '
            yield item
    
        
    