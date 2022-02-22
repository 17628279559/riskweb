'''
基督教日报
部分文章的作者和文章内容展现方式不同，并且一些文章需要付费才能查看
'''
import scrapy
import time
import re
from riskweb.items import ArticleItem

BASE_URL = 'https://www.kristeligt-dagblad.dk'
class MediaKristeligtSpider(scrapy.Spider):
    name = 'media_kristeligt'
    allowed_domains = ['www.kristeligt-dagblad.dk']
    start_urls = ['https://www.kristeligt-dagblad.dk/']

    def parse(self, response):
        global BASE_URL
        categories = response.xpath('//ul[@class="site-navigation__section site-navigation__section--subsub"]//a/@href').extract()
        for category in categories:
            yield scrapy.Request(BASE_URL+category,self.parse_dictionary)

        
    def parse_dictionary(self,response):
        global BASE_URL
        article_urls = response.xpath('//a[@class="simple-teaser__cover-link"]/@href').extract()
        month = response.xpath('//div[starts-with(@class,"simple-teaser__meta")]/span[1]/text()').extract()
        for index,article_url in enumerate(article_urls):
            yield scrapy.Request(BASE_URL+article_url,self.parse_details,meta={'time':month[index]})

        next_url = response.xpath('//a[@class="pagination__link pagination__link--step"]/@href').extract_first()
        if next_url:
            yield scrapy.Request(response.url+next_url,self.parse_dictionary)
    
    
    def parse_details(self,response):
        item = ArticleItem()

        item['title'] = response.xpath('//h1[@class="article__title"]//text()').extract_first()
        item['media_name'] = '基督教日报 Kristeligt Dagblad'
        # author有不同类别
        author = response.xpath('//a[@class="byline__link"]//text()').extract_first() 
        politic_author = response.xpath('//div[@class="byline"]//font/text()').extract_first()
        travel_author = response.xpath('//div[@class="byline__heading"]/text()').extract_first()
        if author:
            item['author'] = author
        elif politic_author:
            item['author'] = politic_author
        elif travel_author:
            item['author'] = travel_author
        else:
            item['author'] = '未给出'
        item['url'] = response.url
        item['topic'] = response.xpath('//span[@class="article__meta-item"][1]/text()').extract_first()
        # 部分文章需要付费
        lead_para = response.xpath('//p[@class="article__lead-para"]/text()').extract()
        content = response.xpath('//div[@class="article__content article__content--drop-cap rich-text"]/p/text()').extract()
        passage = lead_para+content
        other = response.xpath('//p/em/text()').extract_first()
        if passage:
            item['content'] = '\n'.join(passage).replace('\n','').strip()
        elif other:
            item['content'] = '此篇文章需要付费，下面是开头：'+ other
        else:
            item['content'] = '此篇文章需要付费'
        
        
        month = response.meta['time'] 
        hour = response.xpath('//span[@class="article__meta-item"][2]/text()').extract_first()
        pattern = re.compile(r'\d{2}:\d{2}')
        hour = re.findall(pattern, hour)[0]
        publish_date = month+' '+hour 
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S",time.strptime(publish_date,'%d.%m.%Y %H:%M'))

        return item
