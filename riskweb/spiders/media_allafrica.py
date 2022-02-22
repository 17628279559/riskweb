import scrapy
import datetime
from riskweb.items import ArticleItem
import logging
import time
import re
logger = logging.getLogger(__name__)
topic = ''
topics = ['coronavius',
          'agriculuture',
          'governance',
          'africa',
          'centralafrica',
          'eastafrica',
          'northafrica',
          'southernafrica',
          'westafrica']
class MediaAllafricaSpider(scrapy.Spider):
    name = 'media_allafrica'  # name of spider
    allowed_domains = ['allafrica.com']
    count = 0
    def start_requests(self):  # def parse
        start_urls = ['https://allafrica.com/coronavirus/?page=1',
                      'https://allafrica.com/agriculture/?page=1',
                      'https://allafrica.com/governance/?page=1',
                      'https://allafrica.com/africa/?page=1',
                      'https://allafrica.com/centralafrica/?page=1',
                      'https://allafrica.com/eastafrica/?page=1',
                      'https://allafrica.com/northafrica/?page=1',
                      'https://allafrica.com/southernafrica/?page=1',
                      'https://allafrica.com/westafrica/?page=1'
                      ]
        # request函数的参数表,yield用来遍历网址表或者通过BASEURL解析得到的类似TOPICS的集合
        # dont_fliter 为真:强制下载。为假:多次提交请求之后后面的请求会被过滤
        # callback为函数名，在parse函数里通常为parse_dictionary，一直传递到parse_article
        for i in range(0,len(start_urls)):
            yield scrapy.Request(start_urls[i],self.parse_dictionary,dont_filter = False, meta={'topic': start_urls[i]})



    #parse_dictionary用来迭代页面中文章详情的链接
    #如果能在parse函数内直接迭代文章内容，则省略该函数
    def parse_dictionary(self, response):
        # 不存在下一页的总体格式
        # 基础网址
        BASEURL = "https://allafrica.com"
        #从对应的xpath获取文章详情链接的集合article_urls
        article_urls = response.xpath('//ul[@class="stories"]/li/a/@href').extract()
        #迭代链接进行request，此时callback为parse_article
        for article_url in article_urls:

            yield scrapy.Request('https://allafrica.com'+article_url, self.parse_article,dont_filter=False,meta=response.meta)

        #当前页面存在下一页时，迭代next_page_url
        #获取当前页面的下一页的nexty_page_url
        next_page_url = response.xpath('//li[@class="next"]/a/@href').extract_first()

        #存在下一页时，继续发送请求
        if next_page_url is not None:
            yield scrapy.Request('https://allafrica.com'+next_page_url, self.parse_dictionary, dont_filter=False,meta=response.meta)

        #parse_article 进入文章页面获取信息的函数
    def parse_article(self,response):
        #调取参数
        item = ArticleItem()
        #response.xpath获取标题,媒体名，网址，主题


        item['title'] = response.xpath('//h2[@class="headline"]/text()').extract_first()
        item['media_name'] = '泛非通讯社'
        item['url'] = response.url
        item['topic'] = response.meta['topic']
        item['author'] = response.xpath('//cite/text()').extract_first()
        raw_sentences = response.xpath('//div[@class="story-body"]//p//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).replace(r'\xa0', '')
        #update_time = response.xpath('//div[@class="publication-date"]/text()')
        #publish_date_pattern= re.compile(r'')
        #匹配文章的发布时间参照具体格式
        update_time = response.xpath('//div[@class="publication-date"]/text()').extract_first()
        item['publish_date'] = time.strftime("%Y/%m/%d",
                                             time.strptime(update_time,
                                                           "%d %B %Y"))
        #返回item
        return item
