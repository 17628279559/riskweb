'''
乌克兰新闻 
俄语

'''
BASE_URL = 'https://ukranews.com'
import scrapy
import time
from riskweb.items import ArticleItem

class MediaUkrainiannewsSpider(scrapy.Spider):
    name = 'media_ukrainiannews'
    # allowed_domains = ['https://ukranews.com/']
    # start_urls = ['https://ukranews.com/']

    def start_requests(self):
        start_urls = [
            'https://ukranews.com/news/politics',
            'https://ukranews.com/news/economy',
            'https://ukranews.com/news/world',
            'https://ukranews.com/news/china',
            'https://ukranews.com/news/events',
            'https://ukranews.com/news/ukraine',
            'https://ukranews.com/news/press_centre',
            'https://ukranews.com/news',
            'https://ukranews.com/lifestyle'
        ]
        for i in range(0,len(start_urls)):
            yield scrapy.Request(start_urls[i], self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self,response):
        global BASE_URL
        article_urls = response.xpath('//div[@class="news__content"]/div/a/@href').extract()
        lifestyle_urls = response.xpath('//div[@id="w0"]/a/@href').extract()
        if article_urls:
            for article_url in article_urls:
                yield scrapy.Request(BASE_URL+article_url,self.parse_details)
        elif lifestyle_urls:
            for article_url in lifestyle_urls:
                yield scrapy.Request(BASE_URL+article_url,self.parse_details)
        
        next_page = response.xpath('//li[@class="arrow"]/a/@href').extract_first()
        if next_page:
            yield scrapy.Request(BASE_URL+next_page,self.parse_dictionary)

    def parse_details(self,response):
        item = ArticleItem()
        # 俄语月份字典
        month_spec = {
            'января': 'January',
            'Февраля': 'February',
            'март': 'March',
            'апреля': 'April',
            'май': 'May',
            'июня': 'June',
            'июля': 'July',
            'август': 'August',
            'сентября': 'September',
            'октябя': 'October',
            'ноября': 'November',
            'декабря': 'December'
        }
        item['title'] = response.xpath('//h1[@class="article_title"]//text()').extract_first()
        item['media_name'] = '乌克兰新闻'
        item['author'] = response.xpath('//div[@class="name"]/a//text()').extract_first() 
        item['url'] = response.url
        topic = response.xpath('//span[@itemprop="itemListElement"]//text()').extract()
        item['topic'] = ','.join(topic)
        content = response.xpath('//div[@class="article_content"]/h2/text()').extract()
        content += response.xpath('//div[@class="article_content"]/p/text()').extract() 
        item['content'] = '\n'.join(content).replace('\n', '').replace('\xa0','')
        publish_date = response.xpath('//div[@class="article_date"]/a/text()').extract_first().strip().split(',')
        # '26 июля 2021, понедельник, 19:59'
        # 星期不需要，将其舍弃
        publish_month = publish_date[0].strip().split(' ')[1]
        formatted_month = month_spec[publish_month]
        formatted_month = publish_date[0].replace(publish_month,formatted_month)
        publish_date = formatted_month+publish_date[2]
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date, "%d %B %Y %H:%M"))

        return item

        