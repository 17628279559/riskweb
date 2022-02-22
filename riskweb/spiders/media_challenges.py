"""
挑战杂志 爬虫
"""

import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaAftenpostenSpider(scrapy.Spider):
    name = 'media_challenges'
    allowed_domains = ['challenges.fr']
    
    def start_requests(self):
        BASEURL = "https://www.challenges.fr"
        start_paths = [
            '/entreprise/',
            '/economie/',
            '/politique/',
            '/monde/',
            '/media/',
            '/high-tech/',
            '/automobile/',
            '/emploi/',
            '/patrimoine/',
            '/luxe/',
            '/femmes/'
        ]
        # 发送请求
        for start_path in start_paths:
            yield scrapy.Request(BASEURL+start_path, self.parse_dictionary,meta = {'path':start_path,'page':3}, dont_filter=True)

    def parse_dictionary(self, response):
        BASEURL = "https://www.challenges.fr"
        #文章详情链接
        article_urls = response.xpath('//div[@class="txt"]/a/@href | //div[@class="overlay-hover"]/a[1]/@href | //div[@class="content-main"]//ul[@class="list-img list-img-sqr"]/li/a/@href | //div[@class="item"]/a/@href').extract()
        if article_urls:
            for article_url in article_urls:
                yield scrapy.Request(article_url, self.parse_article, dont_filter=False)
            next_url = BASEURL + response.meta['path'] + 'page-' + str(response.meta['page'])
            yield scrapy.Request(next_url,self.parse_dictionary,meta = {'path':response.meta['path'],'page':response.meta['page']+1},dont_filter=True)

        #scrapy crawl media_challenges
    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = response.xpath('//div[@class="article-start"]/h1/text()').extract_first().replace('\xa0','')
        item['media_name'] = '挑战杂志'
        item['url'] = response.url

        item['topic'] ='|'.join(response.xpath('//*[@class="article-tags"]/a/text()').extract())
        
        author = response.xpath('//*[@class="signature"]/text()').extract()
        if author:
            item['author'] = '|'.join(author).strip()

        # 匹配文章的发布时间
        publish_date = response.xpath('//*[contains(@class,"article-infos")]/a/text()').extract_first()
        #08.07.2021 à 09h00
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M", time.strptime(publish_date, "%d.%m.%Y à %Hh%M")) #08.07.2021 à 09h00
        
        raw_sentences = response.xpath('//div[@class=" corps"]/div/p | //div[@class=" corps"]/div/h2').xpath('string(.)').extract()

        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip().replace('\xa0','')
        return item
