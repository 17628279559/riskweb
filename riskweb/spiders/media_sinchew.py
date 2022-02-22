import scrapy
import datetime
from riskweb.items import ArticleItem
import logging
import time
import re
logger = logging.getLogger(__name__)
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains  # 引入 ActionChains 类

class MediaSinchewSpider(scrapy.Spider):
    name = 'media_sinchew'  # name of spider
    allowed_domains = ['sinchew.com.my']
    start_urls = ['https://www.sinchew.com.my/']

    def parse(self, response, **kwargs): # def parse

        BASEURL = 'https://www.sinchew.com.my/'
        topics = response.xpath('//div[@class="dropdownlistbylist"]//a/@href').extract()
        # topics = ['https://www.sinchew.com.my/column/node_65_2.html']
        # request函数的参数表,yield用来遍历网址表或者通过BASEURL解析得到的类似TOPICS的集合
        # dont_fliter 为真:强制下载。为假:多次提交请求之后后面的请求会被过滤
        # callback为函数名，在parse函数里通常为parse_dictionary，一直传递到parse_article
        for topic in topics:
            # 转到话题搜索页面地址：BASEURL + topic
            yield scrapy.Request(topic, self.parse_dictionary,
                                 meta={'topic': topic}, dont_filter=False)


    #parse_dictionary用来迭代页面中文章详情的链接
    #如果能在parse函数内直接迭代文章内容，则省略该函数
    def parse_dictionary(self, response):
        # 不存在下一页的总体格式
        # 基础网址
        BASEURL = 'https://www.sinchew.com.my/'
        #从对应的xpath获取文章详情链接的集合article_urls
        article_urls = response.xpath('//li[@class="listing"]/child::div/child::a/child::img/parent::a/@href').extract()
        print(article_urls)
        # 迭代链接进行request，此时callback为parse_article
        for article_url in article_urls:
            article_url=article_url.lstrip()
            yield scrapy.Request(article_url, self.parse_article, meta=response.meta, dont_filter=True)

        # 当前页面存在下一页时，迭代next_page_url
        # 获取当前页面的下一页的nexty_page_url
        next_page_url = response.xpath('//li[@class="page-next"]/a/@href').extract_first()
        # 存在下一页时，继续发送请求
        if next_page_url is not None:
            yield scrapy.Request(next_page_url, self.parse_dictionary, meta=response.meta,
                                 dont_filter=True)

        #parse_article 进入文章页面获取信息的函数
    def parse_article(self,response):
        #调取参数
        item = ArticleItem()
        #response.xpath获取标题,媒体名，网址，主题
        item['title'] = response.xpath('//div[@id="articlenum"]/h1//text()').extract_first()
        item['media_name'] = '星州日报'
        item['url'] = response.url
        item['topic'] = response.meta['topic']
        raw_sentences = response.xpath('//div[@id="dirnum"]//p//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).replace(r'\xa0', '')
        camefrom=response.xpath('//div[@class="wycamefrom"]//text()').extract()

        #匹配文章的发布时间参照具体格式
        item['author'] = camefrom[0].strip()
        times=camefrom[1].strip().split()
    
        time_1=times[3]
        #返回item
        item['publish_date'] = time.strftime("%Y/%m/%d",
                                             time.strptime(time_1,
                                                           "%Y-%m-%d"))
        return item