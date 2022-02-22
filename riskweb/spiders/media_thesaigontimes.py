"""
西贡时报 爬虫
"""

import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaAftenpostenSpider(scrapy.Spider):
    name = 'media_thesaigontimes'
    allowed_domains = ['thesaigontimes.vn']

    def start_requests(self):
        BASEURL = "https://www.thesaigontimes.vn"
        start_paths = [
            '/tieudiem/'
            '/taichinh/',
            '/kinhdoanh/',
            '/khoinghiep/',
            '/thegioi/',
            '/vanhoaxahoi/' 
            #视频板块未爬取
        ]
        # 发送请求
        for start_path in start_paths:
            yield scrapy.Request(BASEURL+start_path, self.parse_dictionary, dont_filter=False)

    def parse_dictionary(self, response):
        BASEURL = "https://www.thesaigontimes.vn"
        #文章详情链接
        urls = response.xpath('//div[@class="ARTICLE"]/a[@class="ArticleTitle"]/@href').extract()

        for article_url in urls:
            yield scrapy.Request(BASEURL+article_url, self.parse_article, dont_filter=False)

        next_page_path = response.xpath('//a[@id="ctl00_cphContent_hlN"]/@href').extract_first()
        # 增加参数中的start值
        if next_page_path is not None:
            yield scrapy.Request(BASEURL+next_page_path, self.parse_dictionary, dont_filter=False)

        #scrapy crawl media_thesaigontimes
    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = ''.join(response.xpath('//span[@id = "ctl00_cphContent_lblTitleHtml"]//text()').extract()).strip()
        item['media_name'] = '西贡时报'
        item['url'] = response.url
        item['topic'] ="".join(response.xpath('//a[@class="ArticleHeader"]//text()').extract()).strip()
        item['author'] = ''.join(response.xpath('//span[@class="ReferenceSourceTG"]//text()').extract()).strip()
        publish_date = ''.join(response.xpath('//span[@class="Date"]//text()').extract()).strip()
        publish_date = publish_date[re.search(r',',publish_date).end():].strip()
        # 匹配文章的发布时间  Thứ Tư,  21/7/2021, 08:00 
        #21/7/2021, 08:00
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M", time.strptime(publish_date, "%d/%m/%Y, %H:%M")) #JULY 11, 2021 10:29

        raw_sentences = response.xpath('//span[@id="ctl00_cphContent_lblContentHtml"]/p/text()').extract()

        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip()
        return item
