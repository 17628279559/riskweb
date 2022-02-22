import scrapy
from scrapy import Request
import json
import logging
import time
from scrapy.selector import Selector
import re
import datetime
import time
from selenium import webdriver
from riskweb.items import ArticleItem


logger = logging.getLogger(__name__)

#该网站为点击更新动态网页如果要更改点击请求的次数（xhr请求个数），需要在middlewares中的SeleniumTaobaoDownloaderMiddleware
#进行修改 ，而且该网站存在加载速度慢的情况 ，有时会存在请求失效的情况
class AeSpider(scrapy.Spider):
    name = "media_ae"
    allowed_domains = ['wam.ae']
    start_urls = ['http://wam.ae/ar']
    def start_requests(self):
        #列出各个板块的网页链接
        urls = [ 'http://wam.ae/ar/news_bulletin',
                 'http://wam.ae/ar/category/emirates',
                 'http://wam.ae/ar/category/decrees',
                 'http://wam.ae/ar/category/international-relations',
                 'http://wam.ae/ar/category/events',
                 'http://wam.ae/ar/category/women-empowerment',
                 'http://wam.ae/ar/category/infrastructure, transport',
                 'http://wam.ae/ar/category/environment_sustainability',
                 'http://wam.ae/ar/category/culture, heritage, tourism, ',
                 'http://wam.ae/ar/category/humanitarian-aid',
                 'http://wam.ae/ar/category/expo-2020-dubai',
                 'http://wam.ae/ar/category/Kids_Bulletin',
                 'http://wam.ae/ar/category/local_news',
                 'http://wam.ae/ar/occasion/world_government_summit',
                 'http://wam.ae/ar/occasion/coronavirus_updates',
                 'http://wam.ae/ar/category/2020_towards_the_next_50',
                 'http://wam.ae/ar/category/world',
                 'http://wam.ae/ar/category/gcc',
                 'http://wam.ae/ar/category/international',
                 'http://wam.ae/ar/category/business', 
                 'http://wam.ae/ar/category/reports',
                 'http://wam.ae/ar/category/expo-2020-dubai']
       
        
        #time.sleep(1)
        for url in urls:
            yield Request(url = url,callback = self.parse_mod)#在middlewares中新增了类，因此不用担心爬取过程
            #如果要定义xhr请求的个数需要到middlwares中的class SeleniumTaobaoDownloaderMiddleware 中定义，默认请求数为3
            #time.sleep(3)
    def __init__(self):
        super(AeSpider,self).__init__(name='media_ae')
        # 在scrapy中创建driver对象，尽可能少的创建该对象。
        # 1. 在初始化方法中创建driver对象；
        # 2. 在open_spider中创建deriver对象；
        # 3. 不要将driver对象的创建放在process_request()；
        option=webdriver.ChromeOptions()
        option.headless=True
        self.driver = webdriver.Chrome(options=option)
    
    def parse_mod(self,response):
        print("Successful")
        items = response.xpath("//h3[@class='title']//a/@href").extract()#获取新闻链接
        yield{
                'items':items
                }
        for item in items:
            yield Request(url = item,callback = self.parse_article,meta = response.meta,dont_filter=True)
    
    def parse_article(self,response):
        date = response.xpath('//p[@class]/text()').extract()[0]
        title = response.xpath('//h1/span/text()').extract()[0]
        raw_sentences = response.xpath('//div[@data-rvfs="4"]//p/text()').extract()
        editor = response.xpath("//div[@class='post-editor']/text()").extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item = ArticleItem()
        item['content'] = '\n'.join(raw_sentences).strip()
        item['media_name'] = '阿联酋新闻社'
        item['url'] = response.url
        item['author'] = editor
        item['publish_date'] = date
        item['title'] = title
        item['topic'] = ''
        return item
        
        