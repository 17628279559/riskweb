import scrapy
import datetime
from riskweb.items import ArticleItem
import logging
import time
import re
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains  # 引入 ActionChains 类


logger = logging.getLogger(__name__)
class MediaSbsSpider(scrapy.Spider):
    name = 'media_sbs'  # name of spider
    allowed_domains = ['sbs.com.au']



    def start_requests(self):  # def parse
        BASEURL = 'https://sbs.com.au'

        topic_paths = [
            'https://www.sbs.com.au/news/latest',
            'https://www.sbs.com.au/news/topic/australia',
            'https://www.sbs.com.au/news/topic/world',
            'https://www.sbs.com.au/news/topic/coronavirus',
            'https://www.sbs.com.au/news/topic/politics',
            'https://www.sbs.com.au/news/topic/immigration',
            'https://www.sbs.com.au/news/topic/indigenous',
            'https://www.sbs.com.au/news/topic/identity',
            'https://www.sbs.com.au/news/topic/environment',
            'https://theworldgame.sbs.com.au/latest'
        ]
        # request函数的参数表,yield用来遍历网址表或者通过BASEURL解析得到的类似TOPICS的集合
        # dont_fliter 为真:强制下载。为假:多次提交请求之后后面的请求会被过滤
        # callback为函数名，在parse函数里通常为parse_dictionary，一直传递到parse_article
        for topic_path in topic_paths:
            yield scrapy.Request( topic_path, self.parse_dictionary, meta={
                'topicPath': topic_path
            }, dont_filter=False)


    #parse_dictionary用来迭代页面中文章详情的链接
    #如果能在parse函数内直接迭代文章内容，则省略该函数
    def parse_dictionary(self, response):
        BASEURL = 'https://www.sbs.com.au'
        # 从对应的xpath获取文章详情链接的集合article_urls
        article_urls = response.xpath('//div[@class="preview__content"]//a/@href').extract()
        # 迭代链接进行request，此时callback为parse_article
        for article_url in article_urls:
            yield scrapy.Request(BASEURL+article_url, self.parse_article, meta=response.meta, dont_filter=True)

        # 当前页面存在下一页时，迭代next_page_url
        # 获取当前页面的下一页的nexty_page_url
        next_page_url = response.xpath('//a[@class="page-next"]/@href').extract_first()
        # 存在下一页时，继续发送请求
        if next_page_url is not None:
            yield scrapy.Request(response.url + next_page_url, self.parse_dictionary, meta=response.meta,
                                 dont_filter=True)

    #parse_article 进入文章页面获取信息的函数
    def parse_article(self,response):
        #调取参数
        item = ArticleItem()
        #response.xpath获取标题,媒体名，网址，主题
        item['title'] = response.xpath('//div[@class="text-headline"]/h1//text()').extract_first()
        item['media_name'] = '澳大利亚特别节目电视台新闻'
        item['url'] = response.url
        item['topic'] = response.meta['topicPath']
        raw_sentences = response.xpath('//div[@class="text-body"]//p//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).replace(r'\xa0', '')
        item['author'] = response.xpath('//div[@class="meta__item article__meta-author article__meta-author--block"]//span//text()').extract_first()
        # 匹配文章的发布时间参照具体格式
        #匹配文章的发布时间参照具体格式
        update_time = response.xpath('//time/@datetime').extract_first()
        times = []
        for i in update_time:
            if i is not 'T':
                times.append(i)
            if i == '+':
                del times[18]
                break
        times.insert(10,' ')
        new_time=''.join(times)
        print(new_time)
        new_time.strip()
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S",
                                             time.strptime(new_time,"%Y-%m-%d %H:%M:%S"))
        #返回item
        return item
