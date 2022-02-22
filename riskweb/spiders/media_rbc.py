"""
RBC新闻 爬虫
"""
import scrapy
import json
from riskweb.items import ArticleItem
import logging
import time
logger = logging.getLogger(__name__)
from scrapy.selector import Selector
import re
import datetime

from selenium import webdriver


class RBCSpider(scrapy.Spider):
    name = 'media_rbc'
    allowed_domains = ['rbc.ru']
    def __init__(self):
        super(RBCSpider,self).__init__(name='media_rbc')
        # 在scrapy中创建driver对象，尽可能少的创建该对象。
        # 1. 在初始化方法中创建driver对象；
        # 2. 在open_spider中创建deriver对象；
        # 3. 不要将driver对象的创建放在process_request()；
        option=webdriver.ChromeOptions()
        option.headless=True
        self.driver = webdriver.Chrome(options=option)
    def start_requests(self):
        #开始爬取网址
        start_urls = [
            'https://www.rbc.ru/']
        #发送请求
        yield scrapy.Request(start_urls[0], self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):
        #基础网址
        print("this is response.url")
        print(response.url)
        BASEURL = "https://www.rbc.ru"
        #文章详情链接
        article_urls = response.xpath(
            '/html/body/div[6]/div[1]/div[2]/div[1]/div[2]/div/div[1]/div[2]/div[3]/div/div/a/@href').extract()[0:2]
        print('number of article:')
        print(len(article_urls))
        for article_url in article_urls:
            print(article_url)
            yield scrapy.Request(article_url, self.parse_article)

        other_article_urls = response.xpath(
            '/html/body/div[6]/div[1]/div[2]/div[1]/div[2]/div/div[1]/div[4]/div[1]/div/div/div/a/@href').extract()[0:2]
        print('number of other article:')
        print(len(other_article_urls))
        for other_article_url in other_article_urls:
            print(other_article_url)
            yield scrapy.Request(other_article_url, self.parse_article)

    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题


        item['title'] = response.xpath(
            '/html/body/div[7]/div[1]/div[2]/div[1]/div[2]/div/div[4]/div/div[1]/div[1]/div[1]/div[2]/h1/text()').extract_first()
        item['media_name'] = 'rbc新闻'
        item['url'] = response.url
        item['topic'] = ''

        item['author'] = ''

        month_spec = {
            'Январь': '01',
            'Февраль': '02',
            'Март': '03',
            'Апрель': '04',
            'май': '05',
            'июня': '06',
            'июля': '07',
            'Август': '08',
            'Сентябрь': '09',
            'Октябрь': '10',
            'Ноябрь': '11',
            'декабрь': '12'
        }

        unformatted_date = response.xpath(
            '/html/body/div[7]/div[1]/div[2]/div[1]/div[2]/div/div[4]/div/div[1]/div[1]/div[1]/div[1]/span[2]/text()').extract_first().replace('\n','')

        unformatted_day = unformatted_date.split()[0]  # 01
        unformatted_month = month_spec[unformatted_date.split()[1].replace(",",'')]  # июля
        unformatted_year = 2021  # 2021
        unformatted_time = unformatted_date.split()[2]  # 14:43
        unformatted_hour = unformatted_time.split(":")[0]
        unformatted_minute = unformatted_time.split(":")[1]
        item['publish_date'] = unformatted_year + "/" + unformatted_month + "/" + unformatted_day + " " + unformatted_hour + ":" + unformatted_minute + ":00"

        raw_sentences = response.xpath(
            '/html/body/div[7]/div[1]/div[2]/div[1]/div[2]/div/div[4]/div/div[1]/div//p//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip()
        return item
