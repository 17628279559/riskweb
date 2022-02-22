#_*_ encoding:utf-8 _*_
"""
菲律宾星报 爬虫
"""
import scrapy
import json
from riskweb.items import ArticleItem
import logging
import time
from selenium import webdriver
import re
import random

logger = logging.getLogger(__name__)


class MediaMarketwatchSpider(scrapy.Spider):
    name = 'media_philstar'
    allowed_domains = ['philstar.com']

    def start_requests(self):
        # 基础网址
        BASEURL = 'https://www.philstar.com'
        #起始爬取网址
        topic_paths = [
            '/headlines',
            '/opinion',
            '/nation',
            '/world',
            '/business',
            '/sports',
            '/entertainment',
            '/lifestyle',
            '/campus',
            '/movies',
            '/music'
        ]
        # 发送请求
        for topic_path in topic_paths:
            option = webdriver.ChromeOptions()
            # 防止打印一些无用的日志
            option.add_experimental_option("excludeSwitches", ['enable-automation'])
            option.add_experimental_option('excludeSwitches', ['enable-logging'])
            option.add_argument('--incognito')#无痕隐身模式
            option.add_argument("disable-cache")#禁用缓存
            option.add_argument('disable-infobars')
            option.add_argument('--disable-gpu')
            option.add_argument('log-level=3') 
            driver = webdriver.Chrome(chrome_options=option)
            driver.get(BASEURL+topic_path)
            x = True
            num =0
            while x:
                num = len(driver.find_elements_by_xpath('//div[contains(@class,"news_title") or contains(@class,"titleForFeature") or contains(@class,"microsite_article_title")]'))
                for r in range(10):
                    t = random.uniform(0.1, 0.3)
                    time.sleep(t)
                    driver.execute_script("window.scrollBy(0,1000)")
                if len(driver.find_elements_by_xpath('//div[contains(@class,"news_title") or contains(@class,"titleForFeature") or contains(@class,"microsite_article_title")]')) == num:
                    x = False
            u = []
            for i in driver.find_elements_by_xpath('//div[contains(@class,"news_title") or contains(@class,"titleForFeature") or contains(@class,"microsite_article_title")]/a'):
                u.append(i.get_attribute('href'))
            driver.close()
            for i in u:
                yield scrapy.Request(i, self.parse_article,meta={'topic': topic_path[1:]}, dont_filter=False)



    #scrapy crawl media_philstar
    def parse_article(self, response):
        # 调取参数
        item = ArticleItem()
        item['media_name'] = '菲律宾星报'
        item['url'] = response.url

        title = response.xpath('//div[@id="sports_title"]/h1/text()').extract_first()



        item['topic'] =response.meta['topic']

        item['author'] = '|'.join(response.xpath('//div[@id="sports_article_credits"]/a//text()').extract()).strip()

        publish_date = ''.join(response.xpath('//div[@id="sports_article_credits"]//text()').extract()).replace('\xa0','').replace(' ','').replace('\n','').replace('\t','')
        # (Philstar.com) - July 20, 2021 - 10:36am 
        p_date = publish_date[re.search(r'\)-',publish_date).end():re.search(r'(am|pm)',publish_date).end()]
        while p_date == "":
            p_date = publish_date[re.search(r'(am|pm)',p_date).end():]
            p_date = p_date[re.search(r'\)-',p_date).end():re.search(r'(am|pm)',p_date).end()]



        # July21,2021-12:00am
        # 匹配文章的发布时间
        item['publish_date'] =time.strftime("%Y/%m/%d %H:%M", time.strptime(p_date, "%B%d,%Y-%I:%M%p")) #July21,2021-12:00am
        
        raw_sentences = response.xpath('//div[@id="sports_article_writeup"]/p//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))

        item['content'] = '\n'.join(raw_sentences).strip()
        return item








