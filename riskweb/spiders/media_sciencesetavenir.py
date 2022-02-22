"""
科学与未来 爬虫
"""

import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaAftenpostenSpider(scrapy.Spider):
    name = 'media_sciencesetavenir'
    allowed_domains = ['sciencesetavenir.fr']
    
    def start_requests(self):
        BASEURL = "https://www.sciencesetavenir.fr"
        start_paths = [
            '/espace/',
            '/sante/',
            '/nutrition/',
            '/nature-environnement/',
            '/animaux/',
            '/high-tech/',
            '/archeo-paleo/'
        ]
        # 发送请求
        for start_path in start_paths:
            yield scrapy.Request(BASEURL+start_path, self.parse_dictionary,meta={'url':start_path}, dont_filter=True)

    def parse_dictionary(self, response):
        BASEURL = "https://www.sciencesetavenir.fr"
        #文章详情链接
        if not re.search( r'page', response.url):
            article_urls = response.xpath('//div[@class="alaune"]/div[@class="txt"]/a/@href | //div[@class="overlay-hover"]/a[1]/@href').extract()
            article_urls.extend(response.xpath('//div[@class="content-main"]//ul[@class="list-img list-img-sqr"]/li/a/@href').extract())
            for article_url in article_urls:
                yield scrapy.Request(article_url, self.parse_article,meta={'topic':response.meta['url'][1:-1]}, dont_filter=False)
            next_url = BASEURL + response.meta['url'] + 'page-' + '2'
            yield scrapy.Request(next_url,self.parse_dictionary,meta={'url':response.meta['url'],'page':3},dont_filter=True)
        else: 
            if response.xpath('//div[@class="content-main"]//div[@class="item"]'):
                article_urls = response.xpath('//div[@class="item"]/a/@href').extract()
                for article_url in article_urls:
                    yield scrapy.Request(article_url, self.parse_article,meta={'topic':response.meta['url'][1:-1]}, dont_filter=False)
                next_url = BASEURL + response.meta['url'] + 'page-' + str(response.meta['page'])
                yield scrapy.Request(next_url,self.parse_dictionary,meta={'url':response.meta['url'],'page':response.meta['page']+1},dont_filter=True)

            
        #scrapy crawl media_sciencesetavenir
    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = response.xpath('//div[@class="article-start"]/h1/text()').extract_first().replace('\xa0','')
        item['media_name'] = '科学与未来'
        item['url'] = response.url
        item['topic'] ='|'.join(response.xpath('//p[contains(@class,"article-tags")]/a/text()').extract()).strip()
        item['author'] = '|'.join(response.xpath('//*[@class="signature"]/text()').extract()).strip()

        # 匹配文章的发布时间
        publish_date = response.xpath('//*[contains(@class,"article-infos")]//a/text()').extract()[-1]
        #10.08.2021 à 11h25

        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M", time.strptime(publish_date, "%d.%m.%Y à %Hh%M")) #08.08.2021 à 16h00
        
        raw_sentences = response.xpath('//div[contains(@class,"corps")]//p | //div[contains(@class,"corps")]//h2').xpath('string(.)').extract()

        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip().replace('\xa0','')
        return item
