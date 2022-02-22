"""
孟加拉国国家通讯社 爬虫
"""

import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaAftenpostenSpider(scrapy.Spider):
    name = 'media_bssnews'
    allowed_domains = ['bssnews.net']
    def start_requests(self):
        BASEURL = "https://www.bssnews.net/all-news"

        yield scrapy.Request(BASEURL, self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):

        urls = response.xpath('//div[@class="col-lg-6 col-sm-6"]/div/a/@href').extract()

        for article_url in urls:
            yield scrapy.Request(article_url, self.parse_article, dont_filter=True)

        next_page_url = response.xpath('//li[@class="next-btn "]/a/@href').extract_first()
        # 如果存在下一页，继续请求
        if next_page_url is not None:
            yield scrapy.Request(next_page_url, self.parse_dictionary, meta= response.meta, dont_filter=False)
            
            
        #scrapy crawl media_bssnews
    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = response.xpath('//div[@class="headline_section mb-2"]/h4/text()').extract_first().replace("\xa0",'')
        item['media_name'] = '孟加拉国国家通讯社'
        item['url'] = response.url

        item['topic'] ="|".join(response.xpath('//ol[@class="breadcrumb"]/li/a/text()').extract()).strip().replace("\xa0",'')
        author = response.xpath('//div[@class="rpt_name"]/text()').extract()
        item['author'] = '|'.join(author).strip()

        publish_date = response.xpath('//div[@class="entry_update mt-1 pt-1"]/text()').extract_first().strip().replace("\xa0",'')

        # 匹配文章的发布时间
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M", time.strptime(publish_date, "%d %b %Y, %H:%M")) #30 Jul 2021, 12:43
        
        raw_sentences = response.xpath('//div[@class="dtl_section"]/p/text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        for i in range(len(raw_sentences)):
            raw_sentences[i] = raw_sentences[i].replace("\xa0",'')
        item['content'] = '\n'.join(raw_sentences).strip()
        return item

