import scrapy
import datetime
from riskweb.items import ArticleItem
import logging
import time
import re
logger = logging.getLogger(__name__)
class MediaCanberratimesSpider(scrapy.Spider):
    name = 'media_canberratimes'  # name of spider
    allowed_domains = ['canberratimes.com.au']
    start_urls = ['https://www.canberratimes.com.au']

    def parse(self, response, **kwargs): # def parse
        BASEURL = 'https://www.canberratimes.com.au'
        topics = response.xpath('//div[@class="mega-menu__section"]//li//a/@href').extract()
        # request函数的参数表,yield用来遍历网址表或者通过BASEURL解析得到的类似TOPICS的集合
        # dont_fliter 为真:强制下载。为假:多次提交请求之后后面的请求会被过滤
        # callback为函数名，在parse函数里通常为parse_dictionary，一直传递到parse_article
        for topic in topics:
            # 转到话题搜索页面地址：BASEURL + topic
            yield scrapy.Request(BASEURL + topic , self.parse_dictionary,
                                 meta={'topic': topic}, dont_filter=False)


    #parse_dictionary用来迭代页面中文章详情的链接
    #如果能在parse函数内直接迭代文章内容，则省略该函数
    def parse_dictionary(self, response):
        # 不存在下一页的总体格式
        # 基础网址
        BASEURL = 'https://www.canberratimes.com.au'
        #从对应的xpath获取文章详情链接的集合article_urls
        article_urls = response.xpath('//div[@class="story__wof"]//a/@href').extract()
        #迭代链接进行request，此时callback为parse_article
        for article_url in article_urls:
            yield scrapy.Request(BASEURL+article_url, self.parse_article,meta=response.meta,dont_filter=True)

        #当前页面存在下一页时，迭代next_page_url
        #获取当前页面的下一页的nexty_page_url
        next_page_url = response.xpath('//span[@class="pagination__next"]//parent::a/@href').extract_first()
        #存在下一页时，继续发送请求
        if next_page_url is not None:
            yield scrapy.Request(response.url+next_page_url, self.parse_dictionary,meta=response.meta, dont_filter=True)

        #parse_article 进入文章页面获取信息的函数
    def parse_article(self,response):
        #调取参数
        item = ArticleItem()
        #response.xpath获取标题,媒体名，网址，主题
        item['title'] = response.xpath('//header[@class="article__header"]//child::h1//text()').extract_first()
        item['media_name'] = '堪培拉时报'
        item['url'] = response.url
        item['topic'] = response.meta['topic']
        raw_sentences = response.xpath('//div[@class="story"]//p//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).replace(r'\xa0', '')
        item['author'] = response.xpath('// li[ @class ="signature__name"] // h5 // text()').extract_first()
        # 匹配文章的发布时间参照具体格式
        update_time = response.xpath('//time/@datetime').extract_first()
        times = []
        for i in update_time:
            if i is not 'T':
                times.append(i)
            if i == '+':
                del times[18]
                break
        times.insert(10, ' ')
        new_time = ''.join(times)
        print(new_time)
        new_time.strip()
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S",
                                             time.strptime(new_time, "%Y-%m-%d %H:%M:%S"))
        #返回item
        return item
