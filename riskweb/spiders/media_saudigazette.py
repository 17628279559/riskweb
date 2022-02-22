import scrapy
import datetime
from riskweb.items import ArticleItem
import logging
import time
import re
topic = ''
logger = logging.getLogger(__name__)

class MediaSaudigazetteSpider(scrapy.Spider):
    name = 'media_saudigazette'  # name of spider
    allowed_domains = ['saudigazette.com.sa']
    numbers = 0

    def start_requests(self):  # def parse
        BASEURL = 'https://saudigazette.com.sa/'
        start_urls = ['https://saudigazette.com.sa/morearticles/World',
                      'https://saudigazette.com.sa/morearticles/Saudi-arabia',
                      'https://saudigazette.com.sa/morearticles/Sports',
                      'https://saudigazette.com.sa/morearticles/Business',
                      'https://saudigazette.com.sa/morearticles/Technology',
                      'https://saudigazette.com.sa/morearticles/Life'
                      ]

        # request函数的参数表,yield用来遍历网址表或者通过BASEURL解析得到的类似TOPICS的集合
        # dont_fliter 为真:强制下载。为假:多次提交请求之后后面的请求会被过滤
        # callback为函数名，在parse函数里通常为parse_dictionary，一直传递到parse_article
        for i in range(0, len(start_urls)):
            yield scrapy.Request(start_urls[i], self.parse_dictionary, dont_filter=True)


    #parse_dictionary用来迭代页面中文章详情的链接
    #如果能在parse函数内直接迭代文章内容，则省略该函数
    def parse_dictionary(self, response):
        print()
        # 不存在下一页的总体格式
        # 基础网址
        BASEURL = 'https://saudigazette.com.sa'
        #从对应的xpath获取文章详情链接的集合article_urls
        article_urls = response.xpath('/html/body/section//a[@class="ratio"]/@href').extract()
        #迭代链接进行request，此时callback为parse_article
        for article_url in article_urls:
            topic = response.xpath('/html/body/section/div//b/text()').extract_first()
            yield scrapy.Request(article_url, self.parse_article,dont_filter=True)

        #当前页面存在下一页时，迭代next_page_url
        #获取当前页面的下一页的nexty_page_url
        next_page_url = response.xpath('/html/body/section//a[@class="nextPage"]/@href').extract_first()
        #存在下一页时，继续发送请求
        if next_page_url is not None:
            yield scrapy.Request(next_page_url, self.parse_dictionary, dont_filter=True)

        #parse_article 进入文章页面获取信息的函数
    def parse_article(self,response):
        #调取参数
        print()
        item = ArticleItem()
        #response.xpath获取标题,媒体名，网址，主题
        item['title'] = response.xpath('//div[@class="title-widget-1"]/h1/text()').extract_first()
        item['media_name'] = '沙特公报'
        item['url'] = response.url
        item['topic'] = "".join(response.url).split("/",-1)[5]
        raw_sentences_1 = response.xpath('//div[@class="article-body articleBody"]//child::p/text()').extract()#存在两种格式的正文
        if(raw_sentences_1):
            raw_sentences_1 = list(filter(lambda sentence: sentence.strip(), raw_sentences_1))
            item['content'] = '\n'.join(raw_sentences_1).strip()
            item['author'] = response.xpath(
                '//div[@class="article-body articleBody"]//child::p/text()').extract_first
        else:
            raw_sentences = response.xpath('//div[@class="article-body articleBody"]//child::span//child::span/text()').extract()
            raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
            item['content'] = '\n'.join(raw_sentences).strip()
        #item['content'] = "".join(response.xpath('//div[@class="article-body articleBody"]//child::span//child::span/text()').extract())
        #匹配文章的发布时间参照具体格式
        #item['num'] = 2
        pubilsh_time =response.xpath('//div[@class="article-publish-time"]/span/text()').extract_first()
        item['publish_date'] = time.strftime("%Y/%m/%d",
                                             time.strptime(pubilsh_time,
                                                           " %B %d, %Y"))
        #返回item
        return item
