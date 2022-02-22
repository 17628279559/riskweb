"""
刚果金期刊 爬虫
"""

import scrapy
import logging
import time
from riskweb.items import ArticleItem
import re
logger = logging.getLogger(__name__)


class MediaJournaldekinshasaSpider(scrapy.Spider):
    name = 'media_journaldekinshasa'
    allowed_domains = ['journaldekinshasa.com']

    def start_requests(self):
        # 开始爬取网址
        start_urls = [
            'https://www.journaldekinshasa.com/category/politique/',
            'https://www.journaldekinshasa.com/category/eco-et-business/',
            'https://www.journaldekinshasa.com/category/societe/',
            'https://www.journaldekinshasa.com/category/sport/',
            'https://www.journaldekinshasa.com/category/culture/',
            'https://www.journaldekinshasa.com/category/sante/',
            'https://www.journaldekinshasa.com/category/opinions/',
            'https://www.journaldekinshasa.com/category/personnalites/',
            'https://www.journaldekinshasa.com/category/dossiers/',
            'https://www.journaldekinshasa.com/category/international/',
        ]
        # 发送请求
        for i in range(0, len(start_urls)):
            yield scrapy.Request(start_urls[i], self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):
        # 文章详情链接
        article_urls = response.xpath('//article[contains(@class,"small-post")]/a/@href').extract()

        for article_url in article_urls:
            yield scrapy.Request(article_url, self.parse_article)

        # 分页链接
        next_page_url = response.xpath('//a[@class="page larger"]/@href').extract_first()
        # 如果存在下一页，继续请求
        if next_page_url is not None:
            yield scrapy.Request(next_page_url, self.parse_dictionary, dont_filter=True)

    def parse_article(self, response):
        # 调取参数
        item = ArticleItem()
        # 进入每篇文章获取标题
        item['title'] = response.xpath('//h1[@class="title"]/text()').extract_first().replace(r'\xa0', '')
        item['media_name'] = '刚果金期刊'
        item['url'] = response.url
        topics = response.xpath('//p[@class="page-title-category"]//text()').extract()
        item['topic'] = ''.join(topics).replace('\t', '').replace('\n', '').strip()

        # 获取每篇文章的发布信息
        post_infos = response.xpath('//div[contains(@class,"post-infos")][1]/p/text()').extract_first() \
            .replace('\t', '').replace('\n', '').strip()  # Publié le 04.01.2021 à 17h20 par Khady Baldé
        # 正则匹配文章的发布作者
        author_pattern = re.compile(r'par (.*)')
        item['author'] = re.findall(author_pattern, post_infos)[0]
        # 正则匹配文章的发布时间
        publish_date_pattern = re.compile(r'\d{2}.\d{2}.\d{4} à \d{2}h\d{2}')
        publish_date = re.findall(publish_date_pattern, post_infos)[0]
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S",
                                             time.strptime(publish_date, "%d.%m.%Y à %Hh%M"))  # 27.01.2021 à 13h09

        raw_sentences = response.xpath('//div[@class="post-content"]/p//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).replace(r'\xa0', '')

        return item
