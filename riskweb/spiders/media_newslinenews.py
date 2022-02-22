'''
乌克兰新闻资讯
'''
import scrapy
import time
from riskweb.items import ArticleItem

BASE_URL = 'https://www.ukrinform.ua'
class MediaNewslinenewsSpider(scrapy.Spider):
    name = 'media_newslinenews'
    allowed_domains = ['ukrinform.ua']
    
    def start_requests(self):
        start_urls = [
        'https://www.ukrinform.ua/rubric-ato/block-lastnews?page=1',
        'https://www.ukrinform.ua/rubric-polytics/block-lastnews?page=1',
        'https://www.ukrinform.ua/rubric-economy/block-lastnews?page=1',
        'https://www.ukrinform.ua/rubric-world/block-lastnews?page=1',
        'https://www.ukrinform.ua/rubric-society/block-lastnews?page=1',
        'https://www.ukrinform.ua/rubric-regions/block-lastnews?page=1',
        'https://www.ukrinform.ua/rubric-kyiv/block-lastnews?page=1',
        'https://www.ukrinform.ua/rubric-crimea/block-lastnews?page=1',
        'https://www.ukrinform.ua/rubric-sports/block-lastnews?page=1',
        'https://www.ukrinform.ua/rubric-diaspora/block-lastnews?page=1',
        'https://www.ukrinform.ua/rubric-technology/block-lastnews?page=1',
        'https://www.ukrinform.ua/rubric-yakisne-zhyttia/block-lastnews?page=1',
    ]
        for i in range(0,len(start_urls)):
            yield scrapy.Request(start_urls[i],self.parse_dictionary)
    
    def parse_dictionary(self,response):
        global BASE_URL
        article_urls = response.xpath('//article/figure/a/@href').extract()
        for article_url in article_urls:
            yield scrapy.Request(BASE_URL+article_url,self.parse_details)

        next_url = response.xpath('//a[@rel="next"]/@href').extract_first()
        if next_url:
            yield scrapy.Request(next_url,self.parse_details)


    def parse_details(self,response):
        item = ArticleItem()

        item['title'] = response.xpath('//h1[@class="newsTitle"]/text()').extract_first()
        item['media_name'] = '乌克兰新闻资讯'
        item['author'] = '本网站暂未列出'
        item['url'] = response.url
        topic = response.xpath('//a[@class="tag"]/text()').extract()
        item['topic'] = ','.join(topic)
        newsheading = response.xpath('//div[@class="newsText"]/div/text()').extract_first()
        content = response.xpath('//div[@class="newsText"]//div//text()').extract()
        content = '\n'.join(content).replace('\n', '').replace('\r', '').replace('\t', '')
        item['content'] = content
        publish_date = response.xpath('//time/text()').extract_first()
        # '06.07.2021 13:22'
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date, "%d.%m.%Y %H:%M"))

        return item
