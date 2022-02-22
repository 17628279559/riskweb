"""
每日观察报 爬虫
"""
import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem

logger = logging.getLogger(__name__)

class MediaMonitorSpider(scrapy.Spider):
    name = 'media_monitor'
    allowed_domains = ['monitor.co.ug']
    start_urls = ['https://www.monitor.co.ug/']
    BASEURL = "https://www.monitor.co.ug"
    def parse(self, response):
        # 各内容板块链接
        section_paths = response.xpath('//nav[contains(@class,"footer-section")]/a/@href').extract()
        for section_path in section_paths:
            yield scrapy.Request(self.BASEURL+section_path, self.parse_dictionary)

    def parse_dictionary(self, response):
        # 文章详情链接
        # 左侧文章
        story_teaser_paths = response.xpath(
            '//div[@class="five-eight column"]/div[contains(@class,"story-teaser")]/*[name(.)!="figure"]/a/@href') \
            .extract()
        # 右侧文章
        sidebar_item_paths = response.xpath('//li[contains(@class,"story-teaser")]/a[2]/@href').extract()
        sidebar_item_paths.append(response.xpath('//div[@class="gallery"]/a/@href').extract_first())
        article_paths = story_teaser_paths + sidebar_item_paths

        logger.debug(article_paths)
        logger.debug(self.BASEURL)
        for article_path in article_paths:
            yield scrapy.Request(self.BASEURL+article_path, self.parse_article)

    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = response.xpath('//header/h2/text()').extract_first()
        item['media_name'] = '每日观察报'
        item['url'] = response.url
        item['topic'] = '/'.join(response.xpath('//ol[contains(@class,"breadcrumb")]/li//text()').extract())
        item['author'] = response.xpath('//section[@class="author noprint"]/strong/text()').extract_first().replace('By ','')

        publish_date = response.xpath('//header/h6/text()').extract_first()
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date, "%A %B %d %Y")) #Sunday November 01 2020

        raw_sentences = response.xpath('//section[@class="body-copy"]/p//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).replace(r'\xa0', '')

        return item
