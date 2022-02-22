"""
hindustantimes新闻 爬虫
"""
import time
import scrapy
import logging
from riskweb.items import ArticleItem

logger = logging.getLogger(__name__)

class HindustantimesSpider(scrapy.Spider):
    name = 'media_hindustantimes'
    allowed_domains = ['hindustantimes.com']
    def start_requests(self):
        #开始爬取网址
        start_urls = [
            'https://www.hindustantimes.com/latest-news',
            'https://www.hindustantimes.com/mostpopular',
            'https://www.hindustantimes.com/ht-exclusive',
            'https://www.hindustantimes.com/india-news',
            'https://www.hindustantimes.com/cities',
            'https://www.hindustantimes.com/cricket',
            'https://www.hindustantimes.com/entertainment',
            'https://www.hindustantimes.com/editorials'
        ]
        #发送请求
        for i in range(0, len(start_urls)):
            yield scrapy.Request(start_urls[i], self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):
        #基础网址
        BASEURL = "https://www.hindustantimes.com"
        #文章详情链接
        article_urls = response.xpath(
            '/html/body/section[1]/section/section/div/div[1]/h2/a/@href').extract()
        print('number of article:')
        print(len(article_urls))
        for article_url in article_urls:
            article_url = f'{BASEURL}{article_url}'
            yield scrapy.Request(article_url, self.parse_article)

        nextpage_url = response.xpath(
            '/html/body/section[1]/section/section/div/ul/li[7]/a/@href').extract_first()
        if nextpage_url is not None:
            print(nextpage_url)
            yield scrapy.Request(BASEURL+nextpage_url,self.parse_dictionary)

    def parse_article(self, response):
        # 调取参数
        item = ArticleItem()
        # 进入每篇文章获取标题

        item['title'] = response.xpath('//*[@id="dataHolder"]/div[1]/div[1]/h1/text()').extract_first()
        item['media_name'] = 'Hindustatnimes新闻'
        item['url'] = response.url

        item['topic'] = response.xpath('//*[@id="dataHolder"]/div[1]/div[1]/div[1]/a/text()').extract_first()

        item['author'] = response.xpath('//*[@id="dataHolder"]/div[1]/div[1]/div[4]/div[1]/a/text()').extract_first()
        if item['author'] == None:
            item['author'] = response.xpath('//*[@id="dataHolder"]/div[1]/div[1]/div[4]/div//text()').extract_first()

        month_spec = {
            'JAN': '01',
            'FEB': '02',
            'MAR': '03',
            'APR': '04',
            'MAY': '05',
            'JUN': '06',
            'JUL': '07',
            'AUG': '08',
            'SEP': '09',
            'OCT': '10',
            'NOV': '11',
            'DEC': '12'
        }

        unformatted_date = response.xpath('//*[@id="dataHolder"]/div[1]/div[1]/div[4]/div[2]/text()').extract_first()
        # 'UPDATED ON JUL 14, 2021 09:45 AM IST\n'
        unformatted_day = unformatted_date.split()[3].replace(',','')
        unformatted_month = month_spec[unformatted_date.split()[2]]
        unformatted_year = unformatted_date.split()[4]
        unformatted_time = unformatted_date.split()[5]
        unformatted_hour = unformatted_time.split(":")[0]
        if unformatted_date.split()[6] == 'PM':
            unformatted_hour = str(int(unformatted_hour) + 12)
        unformatted_minute = unformatted_time.split(":")[1]
        print(unformatted_day, unformatted_month, unformatted_year, unformatted_time)
        item['publish_date'] = unformatted_year + "/" + unformatted_month + "/" + unformatted_day + " " + unformatted_hour + ":" + unformatted_minute + ":00"


        raw_sentences = response.xpath('//*[@id="dataHolder"]/div[1]/div[2]/div[1]/p//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip()
        return item
