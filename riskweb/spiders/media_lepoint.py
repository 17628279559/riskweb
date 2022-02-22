"""
观点 爬虫
"""

import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaAftenpostenSpider(scrapy.Spider):
    name = 'media_lepoint'
    allowed_domains = ['lepoint.fr']
    start_urls = ["https://www.lepoint.fr"]

    def parse(self, response, **kwargs): # 从主页找到所有的话题路径
        # 基础网址
        BASEURL = "https://www.lepoint.fr"
        topic_paths = response.xpath('//*[@id="scrollable-left-menu"]/li[position()>18]/a/@href').extract()
        topic_paths.remove('/montres/')
        for topic_path in topic_paths:
            yield scrapy.Request(BASEURL + topic_path, self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):
        BASEURL = "https://www.lepoint.fr"
        #文章详情链接  
        urls = response.xpath('//article[contains(@class,"art-full")]/a/@href').extract()
        urls.extend(response.xpath('//article[contains(@class,"mbm art-small")]//figure/a/@href').extract())

        for article_url in urls:
            yield scrapy.Request(BASEURL+article_url, self.parse_article, dont_filter=False)

        next_page_node = response.xpath('//nav[@class="list-view"]/ol/li[last()]')
        #如果存在下一页标志，则含有 i子节点，最后一页则没有下一页标志
        if next_page_node.xpath('.//i'):
            next_page_path = next_page_node.xpath('./a/@href').extract_first()
            yield scrapy.Request(BASEURL+next_page_path, self.parse_dictionary, dont_filter=False)

        #scrapy crawl media_lepoint
    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = response.xpath('//article/header/h1/text()').extract_first().strip().replace('\xa0','')
        item['media_name'] = '观点'
        item['url'] = response.url

        item['topic'] ="|".join(response.xpath('//div[@class="Keywords"]//li//text()').extract()).strip()
        item['author'] = ''.join(response.xpath('//*[@class="SigatureAuthorNames"]//text()').extract()).replace("Par",'').strip()
        publish_date = response.xpath('//time[@class = "DateTime"]/@datetime').extract_first().strip()

        #2015-02-15T09:14
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M", time.strptime(publish_date, "%Y-%m-%dT%H:%M")) #2015-02-15T09:14

        raw_sentences = []
        p = response.xpath('//div[contains(@class , "ArticleBody")]/p | //div[contains(@class , "ArticleBody")]/h3')
        for i in p:
                raw_sentences.append(i.xpath('string(.)').extract_first().strip())

        if response.xpath('//article//aside[@class="Paywall"]'):
            raw_sentences.append("此新闻为付费新闻，只能爬取上述一部分")

        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip().replace('\xa0','')
        return item
