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

class MediaCanberratimesSpider(scrapy.Spider):
    name = 'media_afr'  # name of spider
    allowed_domains = ['afr.com']


    def parse(self, response, **kwargs): # def parse
        start_urls = ['https://www.afr.com']
        BASEURL = 'https://www.afr.com'
        topics = response.xpath('//li[@class="_22VNd"]//a/@href').extract()
        # request函数的参数表,yield用来遍历网址表或者通过BASEURL解析得到的类似TOPICS的集合
        # dont_fliter 为真:强制下载。为假:多次提交请求之后后面的请求会被过滤
        # callback为函数名，在parse函数里通常为parse_dictionary，一直传递到parse_article
        for topic in topics:
            # 转到话题搜索页面地址：BASEURL + topic
            yield scrapy.Request(BASEURL + topic , self.parse_dictionary,
                                 meta={'topic': topic}, dont_filter=False)


    #parse_dictionary用来迭代页面中文章详情的链接
    #如果能在parse函数内直接迭代文章内容，则省略该函数
    def parse_dictionary(self, response):
        # 不存在下一页的总体格式
        # 基础网址
        browser = webdriver.Chrome()
        browser.get(response.url)
        BASEURL = 'https://www.afr.com'
        #从对应的xpath获取文章详情链接的集合article_urls
        while ():
            right_click = browser.find_element_by_xpath(
                '//button[@class="_3zImT"]')
            try:
                ActionChains(browser).context_click(right_click).perform()
            except Exception as e:
                break
        article_urls = response.xpath('//div[@data-testid="StoryTileBase"]//a/@href').extract()
        #迭代链接进行request，此时callback为parse_article
        for article_url in article_urls:
            yield scrapy.Request(BASEURL+article_url, self.parse_article,meta=response.meta,dont_filter=True)



        #parse_article 进入文章页面获取信息的函数
    def parse_article(self,response):
        #调取参数
        item = ArticleItem()
        #response.xpath获取标题,媒体名，网址，主题
        item['title'] = response.xpath('//header//child::h1//text()').extract_first()
        item['media_name'] = '澳大利亚金融评论报'
        item['url'] = response.url
        item['topic'] = response.meta['topic']
        raw_sentences = response.xpath('//div//child::p//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).replace(r'\xa0', '')
        item['author'] =response.xpath('//span[@data-testid="AuthorNames"]//a//text()').extract_first()
        #匹配文章的发布时间参照具体格式

        #返回item
        return item