"""
indianexpress新闻 爬虫
"""
import time
import scrapy
import logging
from riskweb.items import ArticleItem

logger = logging.getLogger(__name__)

class IndianexpressSpider(scrapy.Spider):
    name = 'media_indianexpress'
    allowed_domains = ['indianexpress.com']

    def start_requests(self):
        city_url = 'https://indianexpress.com/section/cities/'
        yield scrapy.Request(city_url, self.parse_normal, dont_filter=True)

        opinion_url='https://indianexpress.com/section/opinion/'
        yield scrapy.Request(opinion_url, self.parse_opinion, dont_filter=True)

        sports_url='https://indianexpress.com/section/sports/'
        yield scrapy.Request(sports_url, self.parse_normal, dont_filter=True)

        entertainment_url='https://indianexpress.com/section/entertainment/'
        yield scrapy.Request(entertainment_url, self.parse_entertainment, dont_filter=True)

        lifestyle_url='https://indianexpress.com/section/lifestyle/'
        yield scrapy.Request(lifestyle_url, self.parse_normal, dont_filter=True)

        technology_url='https://indianexpress.com/section/technology/'
        yield scrapy.Request(technology_url, self.parse_technology, dont_filter=True)

        world_url='https://indianexpress.com/section/world/'
        yield scrapy.Request(world_url, self.parse_world, dont_filter=True)

        india_url='https://indianexpress.com/section/india/'
        yield scrapy.Request(india_url, self.parse_normal, dont_filter=True)

    def parse_normal(self, response):
        #基础网址
        #文章详情链接
        article_urls = response.xpath(
            '//*[@id="section"]/div/div[2]/div[1]/div/div/h2/a/@href').extract()
        print('number of article:')
        print(len(article_urls))
        for article_url in article_urls:
            yield scrapy.Request(article_url, self.parse_article)

        nextpage_url = response.xpath(
            '//*[@id="section"]/div/div[2]/div[1]/div/div/ul/li/a/@href').extract()[-1]
        if nextpage_url is not None:
            print(nextpage_url)
            yield scrapy.Request(nextpage_url, self.parse_normal)

    def parse_opinion(self, response):
        #基础网址
        #文章详情链接
        article_urls = response.xpath(
            '//*[@id="section"]/div/div[2]/div[1]/div[3]/div[3]/div/h2/a/@href').extract()
        print('number of article:')
        print(len(article_urls))
        for article_url in article_urls:
            yield scrapy.Request(article_url, self.parse_article)

        nextpage_url = response.xpath(
            '//*[@id="section"]/div/div[2]/div[1]/div[3]/div[3]/div[34]/ul/li/a/@href').extract()[-1]
        if nextpage_url is not None:
            print(nextpage_url)
            yield scrapy.Request(nextpage_url, self.parse_opinion)

    def parse_entertainment(self, response):
        #基础网址
        #文章详情链接
        article_urls = response.xpath(
            '//*[@id="section"]/div/div[2]/div[1]/div/div/div[2]/a/@href').extract()
        print('number of article:')
        print(len(article_urls))
        for article_url in article_urls:
            yield scrapy.Request(article_url, self.parse_article)

        nextpage_url = response.xpath(
            '//*[@id="section"]/div/div[2]/div[1]/div/div[27]/ul/li/a/@href').extract()[-1]
        if nextpage_url is not None:
            print(nextpage_url)
            yield scrapy.Request(nextpage_url, self.parse_entertainment)

    def parse_technology(self, response):
        #基础网址
        #文章详情链接
        article_urls = response.xpath(
            '//*[@id="wrapper"]/div[3]/div[4]/div[2]/ul[1]/li/h3/a/@href').extract()
        print('number of article:')
        print(len(article_urls))
        for article_url in article_urls:
            yield scrapy.Request(article_url, self.parse_article)

        nextpage_url = response.xpath(
            '//*[@id="wrapper"]/div[3]/div[4]/div[2]/ul[2]/ul/li/a/@href').extract()[-1]
        if nextpage_url is not None:
            print(nextpage_url)
            yield scrapy.Request(nextpage_url, self.parse_technology)

    def parse_world(self, response):
        #基础网址
        #文章详情链接
        article_urls = response.xpath(
            '//*[@id="north-east-data"]/ul/li/h3/a/@href').extract()
        print('number of article:')
        print(len(article_urls))
        for article_url in article_urls:
            yield scrapy.Request(article_url, self.parse_article)

        nextpage_url = response.xpath(
            '//*[@id="wrapper"]/div[7]/div/ul/li/a/@href').extract()[-1]
        if nextpage_url is not None:
            print(nextpage_url)
            yield scrapy.Request(nextpage_url, self.parse_world)

    def parse_article(self, response):
        # 调取参数
        item = ArticleItem()
        # 进入每篇文章获取标题

        item['title'] = response.xpath('//*[@id="section"]/div/div[2]/div/h1/text()').extract_first()
        item['media_name'] = 'Indianexpress新闻'
        item['url'] = response.url
        item['topic'] = response.xpath('//*[@id="section"]/div/div[2]/div/nav/ol/li/a/text()').extract()[-1]

        item['author'] = response.xpath('//*[@id="storycenterbyline"]/a/text()').extract_first()

        month_spec = {
            'January': '01',
            'February': '02',
            'March': '03',
            'April': '04',
            'May': '05',
            'June': '06',
            'July': '07',
            'August': '08',
            'September': '09',
            'October': '10',
            'November': '11',
            'December': '12'
        }
        unformatted_date = response.xpath('//*[@id="storycenterbyline"]/span/text()').extract_first()
        unformatted_date=unformatted_date.replace("Updated:",'')
        print(unformatted_date)
        # 'July 14, 2021 7:55:34 am'
        unformatted_day = unformatted_date.split()[1].replace(',', '')
        unformatted_month = unformatted_date.split()[0]
        unformatted_month = month_spec[unformatted_month]
        unformatted_year = unformatted_date.split()[2]
        unformatted_time = unformatted_date.split()[3]
        unformatted_hour = unformatted_time.split(":")[0]
        if unformatted_date.split()[4] == 'pm':
            unformatted_hour = str(int(unformatted_hour) + 12)
        unformatted_minute = unformatted_time.split(":")[1]
        unformatted_second = unformatted_time.split(":")[2]
        print(unformatted_day, unformatted_month, unformatted_year, unformatted_time)

        # fomattted_month = month_spec[unformatted_month]
        # unformatted_date = unformatted_date.replace(unformatted_month, fomattted_month)

        # publish_date_year = response.xpath('//*[@id="article"]/div[1]/ul[1]/li[@class="std-social date-box"]/span[1]/text()').extract_first().replace('\n','')
        # publish_date = publish_date_year + unformatted_date
        # item['publish_date'] = publish_date
        # if publish_date:
        #     item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date, "%Y%B %d"))

        item['publish_date'] = unformatted_year+"/"+unformatted_month+"/"+unformatted_day+" "+unformatted_hour+":"+unformatted_minute+":"+unformatted_second
        raw_sentences = response.xpath('//*[@id="pcl-full-content"]/p/text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip()
        return item
