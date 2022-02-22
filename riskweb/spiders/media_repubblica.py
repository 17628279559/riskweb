"""
共和国报 爬虫
"""

import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaAftenpostenSpider(scrapy.Spider):
    name = 'media_repubblica'
    allowed_domains = ['repubblica.it']
    start_urls = ["https://www.repubblica.it"]
    
    def parse(self, response, **kwargs):
        start_paths = response.xpath('//li[@class="rep-left-nav__list__item"]/ul/li/a/@href').extract()
        # 发送请求
        start_paths.remove('https://www.repubblica.it/podcast/')
        for start_path in start_paths:
            if re.search(r'www',start_path):
                yield scrapy.Request(start_path, self.parse_dictionary, dont_filter=True)


    def parse_dictionary(self, response):
        BASEURL = 'https://www.repubblica.it'
        #文章详情链接
        urls = response.xpath('//article//h2/a/@href').extract()
        for article_url in urls:
            yield scrapy.Request(article_url, self.parse_article, dont_filter=False)

        next_url = response.xpath('//nav[@class="pagination"]//li/a[text()="Avanti"]/@href').extract_first()
        if next_url:
            yield scrapy.Request(next_url,self.parse_dictionary,dont_filter=True)

    #scrapy crawl media_repubblica
    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = response.xpath('//h1[@class="story__title"]/text()').extract_first()
        item['media_name'] = '共和国报'
        item['url'] = response.url

        item['topic'] ="|".join(response.xpath('//ul[@class="story__tags__list"]/li/a/text()').extract())

        author = response.xpath('//div[@class="story__header__content"]/em/text()').extract()
        if author:
            author = [i.strip().replace('\xa0','').replace('\t','').replace('\r','').replace('\n','') for i in author]
            item['author'] = '|'.join(author)
        else:
            item['author'] = ''

        publish_date = response.xpath('//div[@class="story__toolbar"]/time/@datetime').extract_first()
        if publish_date:
            item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date.split('+')[0], "%Y-%m-%dT%H:%M:%SZ")) #2021-08-21T22:01:00Z
        else:
            item['publish_date'] = ''

        raw_sentences = response.xpath('//div[@class="story__text"] | //*[@id="article-body"]').xpath('string(.)').extract()
        raw_sentences = [i.strip().replace('\xa0','').replace('\t','').replace('\r','').replace('\n','') for i in raw_sentences]
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        if response.xpath('//*[@id="paywall"]'):
            raw_sentences.append("此篇新闻需要付费订阅,只能爬取上述一部分")
        item['content'] = '\n'.join(raw_sentences).strip()
        return item




