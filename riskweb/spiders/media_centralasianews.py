'''
中亚新闻社 爬虫
已完成（需要改进，将俄文的月份写一个字典）
'''
import scrapy
import logging
import time
from riskweb.items import ArticleItem
import re
from translate import Translator
logger = logging.getLogger(__name__)

class MediaCentralasianewsSpider(scrapy.Spider):
    name = 'media_centralasianews'
    allowed_domains = ['centralasia.media']

    def start_requests(self):
        country_count = 7
        category_count = [1,2,3,4,6,8]
        start_url = [
            'https://centralasia.media/country:',
            'https://centralasia.media/category:',
            'https://centralasia.media/report:1:1',# 图像新闻，无法获取内容，需要订阅，只有标题
            'https://centralasia.media/report:2:1',# 视频新闻，无法获取内容，需要订阅，只有标题        
        ]
        country_urls = [ start_url[0] + str(x) for x in range(1,country_count+1) ]
        category_urls = [ start_url[1] + str(x) for x in category_count ]
        start_url = country_urls + category_urls 
        # 发送请求
        for i in range(0, len(start_url)):
            yield scrapy.Request(start_url[i], self.parse_dictionary, dont_filter=True)

        
    def parse_dictionary(self, response):
        base_url = 'https://centralasia.media'

        special_news_title = response.xpath('//div[@class="titles"]/text()')   
        # 如果出现特殊标题，说明是那两个特殊的网页（只能看文章标题的）
        if special_news_title:
            special_article_urls = response.xpath('//div[@id="maincontent"]//tr//td/a/@href').extract()
            for article_url in special_article_urls:
                yield scrapy.Request(base_url+article_url, self.parse_special_article)
            # 分页链接
            next_page_url = response.xpath('//a[@class="pageLink"]/@href').extract_first()[0]
            # 如果存在下一页，继续请求
            if next_page_url:
                yield scrapy.Request(base_url + next_page_url, self.parse_dictionary, dont_filter=True)
        else:
            # 普通文章详情链接
            article_urls = response.xpath('//div[@class="newslist"]//a/@href').extract()
            for article_url in article_urls:
                yield scrapy.Request(base_url+article_url, self.parse_article)
        
    def parse_special_article(self, response):
        # 调取参数
        item = RiskwebItem()
        # 进入每篇文章获取相关信息
        item['title'] = response.xpath('//div[@id="maincontent"]//div[@style="font-size: 20px;margin:10px 0 15px 0;"]/text()').extract()[-1].strip()
        item['media_name'] = '中亚新闻社'
        item['url'] = response.url
        item['author'] = ''
        # 清洗标签内容
        topics = response.xpath('//ul[@class="newsToolbar"]/li/a/text()').extract()
        item['topic'] = ','.join(topics).strip()
        # 清洗文章内容
        raw_sentences = response.xpath('//div[@class="newstext"]//p/text()').extract()
        item['content'] = ''.join(raw_sentences).replace('\xa0', ' ').strip()
        # 转换时间格式
        publish_date = response.xpath('//ul[@class="newsToolbar"]/li/text()').extract()[1].replace('\xa0','')
        translator = Translator(from_lang="russian",to_lang="english")
        publish_date = translator.translate(publish_date)
        # '16: 47.07 July 2021'
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date, "%H: %M.%d %B %Y"))
        
        return item

    def parse_article(self, response):
        # 调取参数
        item = ArticleItem()
        # 进入每篇文章获取相关信息
        item['title'] = response.xpath('//div[@id="maincontent"]//div[@style="font-size: 20px;margin:10px 0 15px 0;"]/text()').extract()[-1].strip()
        item['media_name'] = '中亚新闻社'
        item['url'] = response.url
        item['author'] = ''
        # 清洗标签内容
        topics = response.xpath('//ul[@class="newsToolbar"]/li/a/text()').extract()
        item['topic'] = ','.join(topics).strip()
        # 清洗文章内容
        front_sentence = response.xpath('//div[@class="newstext"]/p/b/b/text()').extract()[0]
        raw_sentences = response.xpath('//div[@class="newstext"]/p/text()').extract()
        item['content'] = front_sentence + ''.join(raw_sentences).replace('\xa0', ' ').strip()
        # 转换时间格式
        publish_date = response.xpath('//ul[@class="newsToolbar"]/li/text()').extract()[1].replace('\xa0','')
        translator = Translator(from_lang="russian",to_lang="english")
        publish_date = translator.translate(publish_date)
        # '6:11,12 июля 2021'
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date, "%H:%M,%d %B %Y"))
        
        return item