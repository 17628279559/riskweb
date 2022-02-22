'''
白俄罗斯国家新闻社 爬虫
已完成（需要改进，将俄文的月份写一个字典）
'''
import scrapy
import logging
import time
from riskweb.items import ArticleItem
import re
from translate import Translator
logger = logging.getLogger(__name__)

class MediaBeltaSpider(scrapy.Spider):
    name = 'media_belta'
    allowed_domains = ['www.belta.by']

    def start_requests(self):
        start_urls = [
            'https://www.belta.by/president/',
            'https://www.belta.by/politics/',
            'https://www.belta.by/economics/',
            'https://www.belta.by/society/',
            'https://www.belta.by/regions/',
            'https://www.belta.by/incident/',
            'https://www.belta.by/tech/',
            'https://www.belta.by/world/',
            'https://www.belta.by/culture/',
            'https://www.belta.by/events/',
            'https://www.belta.by/kaleidoscope/',
        ]
        special_urls = [
            'https://www.belta.by/opinions/',
            'https://www.belta.by/comments/',
            'https://www.belta.by/interview/',
            'https://www.belta.by/columnists/',
            'https://www.belta.by/photonews/',
            'https://www.belta.by/search/findTags/1193/',
            'https://www.belta.by/video/',
            'https://www.belta.by/infographica/',
        ]
        # 发送请求
        for i in range(0, len(start_urls)):
            yield scrapy.Request(start_urls[i], self.parse_dictionary, dont_filter=True)
        for j in range(0, len(special_urls)):
            yield scrapy.Request(special_urls[j], self.parse_dictionary, dont_filter=True)
        
    def parse_dictionary(self, response):
        base_url = 'https://www.belta.by'
        news_urls = response.xpath('//div[@class="news_item"]//a/@href').extract()       
        special_urls = response.xpath('//div[@class="center_col"]/div/a/@href').extract()
        if news_urls:
            for article_url in news_urls:
                yield scrapy.Request(base_url+article_url, self.parse_article)
        else:
            for article_url in special_urls:
                yield scrapy.Request(article_url, self.parse_article)
        # 分页链接
        next_page_url = response.xpath('//a[@class="p_next"]/@href').extract_first()
        # 如果存在下一页，继续请求
        if next_page_url:
            yield scrapy.Request(base_url + next_page_url, self.parse_dictionary, dont_filter=True)

    def parse_article(self, response):
        # 调取参数
        item = ArticleItem()
        # 进入每篇文章获取相关信息
        item['media_name'] = '白俄罗斯国家新闻社'
        # 清洗文章内容
        raw_sentences = response.xpath('//div[@class="text"]//p/text()').extract()
        item['content'] = ''.join(raw_sentences).replace('\xa0', ' ').strip()
        item['url'] = response.url
        # 转换时间格式
        publish_date = response.xpath('//div[@class="date_full"]/text()').extract_first().replace('\xa0','')
        translator = Translator(from_lang="russian",to_lang="english")
        publish_date = translator.translate(publish_date)
        # '11 July 2021, 09:03'
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date, "%d %B %Y, %H:%M"))
        
        # 文章标题
        title = response.xpath('//div[@class="content_margin"]//h1/text()').extract_first().replace('\xa0','').strip()
        if title:
            item['title'] = title
        else:
            item['title'] = response.xpath('//div[@class="main"]//h1/text()').extract_first().replace('\xa0','').strip()
        # 白俄罗斯国家新闻社普通文章的作者都是БЕЛТА,特殊文章不是
        author = response.xpath('//div[@class="person_fio"]/@title').extract_first()
        if author:
            item['author'] = author
        else:
            item['author'] = 'БЕЛТА'       
        # 清洗标签内容
        topics = response.xpath('//div[@class="news_tags_block"]//a/@title').extract()
        if topics:
            #普通文章的情况
            if len(topics)!=1:
                item['topic'] = ','.join(topics).strip()
            else:
                item['topic'] = ''.join(topics).strip()
        else:
            #特殊文章的情况
            topics = response.xpath('//div[@class="news_tags_block"]//a/text()').extract_first()
            if len(topics)!=1:
                item['topic'] = ','.join(topics).strip()
            else:
                item['topic'] = ''.join(topics).strip()
        
        return item

        translate_data = {

        }