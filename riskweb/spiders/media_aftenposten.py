"""
挪威晚邮报 爬虫
"""
import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaAftenpostenSpider(scrapy.Spider):
    name = 'media_aftenposten'
    allowed_domains = ['aftenposten.no']

    def start_requests(self):
        BASEURL = "https://www.aftenposten.no"
        start_paths = [
            '/nyheter',
            '/oslo',
            '/sport',
            '/meninger',
            '/kultur',
            '/historie',
            '/norge/politikk',
            '/norge',
            '/verden',
            '/okonomi',
            '/amagasinet',
            '/podkast',
            '/karriere',
            '/oslo/sulten',
            '/sport/fotball',
            '/sport/langrenn',
            '/sport/sprek',
            '/sport/meninger',
            '/meninger/leder',
            '/meninger/debatt',
            '/meninger/kommentar',
            '/meninger/kronikk',
            '/meninger/sid',
            '/viten',
            '/tag/film',
            '/tag/tv-serier-2',
            '/tag/musikk',
            '/tag/litteratur',
        ]
        # 发送请求
        for i in range(0, len(start_paths)):
            yield scrapy.Request(BASEURL+start_paths[i], self.parse_dictionary, dont_filter=False)

    def parse_dictionary(self, response):
        BASEURL = "https://www.aftenposten.no"
        #文章详情链接
        article_urls = response.xpath(
            '//article/a/@href').extract()

        for article_url in article_urls:
            yield scrapy.Request(article_url, self.parse_article, dont_filter=False)

        # 下一页地址
        next_page_path = response.xpath(
            '//a[@class="link__nextPage"]/@href').extract_first()

        # 增加参数中的start值
        if next_page_path is not None:
            yield scrapy.Request(BASEURL+next_page_path, self.parse_dictionary, dont_filter=False)

    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = response.xpath('//h1[contains(@class,"extendedContent")]/text()').extract_first()
        item['media_name'] = '挪威晚邮报'
        item['url'] = response.url
        item['topic'] = '|'.join(response.xpath('//div[@data-test-tag="running-head"]/div/a//text()').extract())

        author = response.xpath('//div[@data-test-tag="byline"]//span/a/text()').extract()
        if author is None:
            author = response.xpath('//div[@data-test-tag="byline"]//span/text()').extract()

        item['author'] = '|'.join(author)


        publish_date = response.xpath('//div[@data-test-tag="timestamp"]/div/time/@datetime').extract_first()

        # 匹配文章的发布时间
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date, "%Y-%m-%dT%H:%M:%SZ")) #2021-05-29T18:00:00Z

        raw_sentences = response.xpath('//div[@id="main"]//p[@class]//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip()
        return item
