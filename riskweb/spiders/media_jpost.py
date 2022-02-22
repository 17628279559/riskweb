"""
耶路撒冷邮报 爬虫
"""

import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaAftenpostenSpider(scrapy.Spider):
    name = 'media_jpost'
    allowed_domains = ['jpost.com']
    #此网站HTML格式非常乱,网页内容少，不需要蹄子，挂蹄子访问不了
    def start_requests(self):
        BASEURL = "https://www.jpost.com"
        start_paths = [
            '/coronavirus/'
            '/breaking-news/',
            '/israel-news/',
            '/israel-elections/',
            '/international/',
            '/middle-east/',
            '/american-politics/',
            '/archaeology/',
            '/opinion/',
            '/aliyah/',
            '/judaism/',
            '/kabbalah/',
            '/health-science/',
            '/diaspora/',
            '/law/',
            '/must/',
            '/premium/'
        ]
        # 发送请求
        for i in range(0, len(start_paths)):
            yield scrapy.Request(BASEURL+start_paths[i], self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):

        #文章详情链接
        #顶部五条
        urls = response.xpath('//div[@class="a-list bottom"]/div[1]/a/@herf').extract()
        urls.extend(response.xpath('//div[@class="a-list bottom"]/div[2]/div/a/@herf').extract())
        #其余新闻
        bottom_article_urls = response.xpath('//div[@class="a-list"]/div/a/@href').extract()

        urls.extend(bottom_article_urls)
        for article_url in urls:
            yield scrapy.Request(article_url, self.parse_article, dont_filter=True)

    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = '|'.join(response.xpath('//div[@class="body-first-part"]/div[1]/h1/text()').extract())
        item['media_name'] = '耶路撒冷邮报'
        item['url'] = response.url
        item['topic'] ="".join(response.xpath('//span[@class="breadcrumbs-list"]/span[2]//text()').extract()).strip()
        author = response.xpath('//div[@class="author"]//span[@class="article-reporter"]//text()').extract()
        if not author:
            author = response.xpath('//div[@class="author mb20"]//span[@class="article-reporter"]//text()').extract()
        #有的多个作者写在多个<a>板块,有的多个作者写在一个<a>板块按'/'分
        for i in range(len(author)):
            if re.search( r'//', author[i]):
                author.extend(author[i].split('/'))
                author.pop(i)

        item['author'] = '|'.join(author).strip()

        publish_date = response.xpath('//div[@class="author"]/div[@class="article-subline-name"]/text()').extract_first()

        # 匹配文章的发布时间
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M", time.strptime(publish_date, "%B %d, %Y %H:%M")) #JULY 11, 2021 10:29
        
        raw_sentences = response.xpath('//div[@class="article-inner-content"]/text()').extract()
        #父级div内含<scrip>，所以没用//text()
        raw_sentences.extend(response.xpath('//div[@class="article-inner-content"]/div/text()').extract())
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip()
        return item
