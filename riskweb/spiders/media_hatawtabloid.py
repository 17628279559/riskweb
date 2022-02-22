"""
hatawtabloid 爬虫
"""

import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem
import cfscrape
from parsel import Selector
import requests
logger = logging.getLogger(__name__)

class MediaAftenpostenSpider(scrapy.Spider):
    name = 'media_hatawtabloid'
    allowed_domains = ['hatawtabloid.com']

    def start_requests(self):
        urls="https://www.hatawtabloid.com/"


        ssss = cfscrape.create_scraper(delay=10)
        cookies,user_agent= ssss.get_cookie_string(urls)
        headers = {'cookies': cookies,'user_agent':user_agent}
        print(ssss.get(urls,headers=headers).text)

        #scrapy crawl media_hatawtabloid
        








