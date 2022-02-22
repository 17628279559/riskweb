"""
斯洛伐克通讯社 爬虫
"""

import scrapy
import time
import datetime
import logging
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaAftenpostenSpider(scrapy.Spider):
    name = 'media_tasr'
    allowed_domains = ['newsnow.tasr.sk','obce.tasr.sk']
    def start_requests(self):
        BASEURL = [ "https://newsnow.tasr.sk/","https://obce.tasr.sk/"
                   
                   ]
        for url in BASEURL:
            yield scrapy.Request(url, self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):
        if re.search( r'obce', response.url):
            BASE = 'https://obce.tasr.sk'
            urls = response.xpath('//header[@class="main-header"]/div[@class="container"]//a/@href').extract()
            urls.extend(response.xpath('//div[@class="main-wrap"]/div[@class="full-frame"]/a/@href').extract())
            urls.extend(response.xpath('//div[@class="half-frame-wrap"]//a/@href').extract())
            for article_url in urls:
                yield scrapy.Request(BASE+article_url, self.parse_article, dont_filter=True)

            next_url = response.xpath('//ul[@class="pagination"]/li[last()]/a/@href').extract_first()
            # 如果存在下一页，继续请求
            if next_url is not None:
                yield scrapy.Request(next_url, self.parse_dictionary,  dont_filter=False)
        elif re.search( r'newsnow', response.url):
            urls = response.xpath('//div[@class="td_module_10 td_module_wrap td-animation-stack"]/div/a/@href').extract()
          
            for article_url in urls:
                yield scrapy.Request(article_url, self.parse_article, dont_filter=True)

            next_page_url = response.xpath('//div[@class="page-nav td-pb-padding-side"]/a[last()]/@href').extract_first()
            # 如果存在下一页，继续请求
            if next_page_url is not None:
                yield scrapy.Request(next_page_url, self.parse_dictionary, dont_filter=False)
        else:
            pass
            
            
        #scrapy crawl media_tasr
    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        if re.search( r'obce', response.url):
            item['title'] = response.xpath('//div[@class="articleTitle"]/text()').extract_first()
            item['media_name'] = '斯洛伐克通讯社'
            item['url'] = response.url

            time_and_topic_and_author = response.xpath('//article/text()').extract()
            time_and_topic_and_author = list(filter(lambda x: x.strip(), time_and_topic_and_author))
            time_and_topic = time_and_topic_and_author[0].strip().split('|')
            item['topic'] = time_and_topic[1].strip()

            item['author'] = time_and_topic_and_author[1].strip()

            publish_date = time_and_topic[0].strip()
            if re.search( r'pred', publish_date):
                nowtime = datetime.datetime.now()
                d = int(publish_date.split()[1].strip())
                day = datetime.timedelta(days=d)
                item['publish_date'] = (nowtime - day).strftime('%Y/%m/%d')
            # 匹配文章的发布时间
            else: 
                item['publish_date'] = time.strftime("%Y/%m/%d", time.strptime(publish_date, "%d.%m.%Y")) #20.07.2021
        
            raw_sentences = response.xpath('//div[@class="articleText"]/p')

            content = []
            for i in raw_sentences:
                content.append(i.xpath('string(.)').extract_first())
            content = list(filter(lambda sentence: sentence.strip(), content))

            item['content'] = '\n'.join(content).strip()
        elif re.search( r'newsnow', response.url):
            item['title'] = response.xpath('//div[@class="entry-crumbs"]/span[last()]/text()').extract_first()
            item['media_name'] = '斯洛伐克通讯社'
            item['url'] = response.url

            item['topic'] = response.xpath('//div[@class="entry-crumbs"]/span//text()').extract()[1]

            item['author'] = ' '

            publish_date = response.xpath('//span[@class="td-post-date"]/time/text()').extract_first().strip()

            # 匹配文章的发布时间
            item['publish_date'] = time.strftime("%Y/%m/%d", time.strptime(publish_date, "%B %d, %Y")) #July 29, 2021
        
            raw_sentences = response.xpath('//div[@class="td-post-content"]/p/text()').extract()
            raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
            item['content'] = '\n'.join(raw_sentences).strip()
        return item

