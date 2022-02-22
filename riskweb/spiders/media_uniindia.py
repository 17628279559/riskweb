"""
uniindia新闻 爬虫
"""
import time
import scrapy
from riskweb.items import ArticleItem
import logging
logger = logging.getLogger(__name__)

class UniindiaSpider(scrapy.Spider):
    name = 'media_uniindia'
    allowed_domains = ['uniindia.com']
    def start_requests(self):
        #开始爬取网址
        start_urls = [
            'http://www.uniindia.com/news/india/',
            'http://www.uniindia.com/news/states/',
            'http://www.uniindia.com/news/world/',
            'http://www.uniindia.com/news/sports/',
            'http://www.uniindia.com/news/business-economy/'
        ]
        #发送请求
        for i in range(0, len(start_urls)):
            yield scrapy.Request(start_urls[i], self.parse_all_pages, dont_filter=False)

    def parse_all_pages(self,response):
        nextpage_urls = response.xpath(
            '//*[@id="ctl00_ContentPlaceHolder1_catnewsid"]/div[16]/a/@href').extract()
        for nextpage_url in nextpage_urls:
            nextpage_url = response.url + nextpage_url.replace('..', '')
            print(nextpage_url)
            yield scrapy.Request(nextpage_url, self.parse_dictionary, dont_filter=False)

    def parse_dictionary(self, response):
        #基础网址
        BASEURL = 'http://www.uniindia.com'
        #文章详情链接
        article_urls = response.xpath(
            '//*[@id="ctl00_ContentPlaceHolder1_catnewsid"]/div/h1/a/@href').extract()
        print("number of articles:")
        print(len(article_urls))
        for article_url in article_urls:
            article_url = f'{BASEURL}{article_url}'
            yield scrapy.Request(article_url,self.parse_article)

    def parse_article(self, response):
        # 调取参数
        item = ArticleItem()
        # 进入每篇文章获取标题

        item['title'] = response.xpath(
            '//*[@id="ctl00_ContentPlaceHolder1_storyContainer"]/h1/text()').extract_first()
        item['media_name'] = 'uniindia新闻'
        item['url'] = response.url
        item['topic'] = response.xpath(
            '//*[@id="ctl00_ContentPlaceHolder1_storyContainer"]/span[1]/a/text()').extract_first()

        item['author'] = ''

        month_spec = {
            'Jan': '01',
            'Feb': '02',
            'Mar': 'March',
            'Apr': 'April',
            'May': 'May',
            'Jun': 'June',
            'Jul': 'July',
            'Aug': 'August',
            'Sep': 'September',
            'Oct': 'October',
            'Nov': 'November',
            'Dec': 'December'
        }

        unformatted_date = response.xpath(
            '//*[@id="ctl00_ContentPlaceHolder1_storyContainer"]/span[2]/text()').extract_first()
        unformatted_month = unformatted_date.split()[2]
        # 'Posted at: Jul 23 2021 11:07AM'
        unformatted_month = month_spec[unformatted_month]
        unformatted_day = unformatted_date.split()[3]  # 01
        unformatted_year = unformatted_date.split()[4]  # 2021
        unformatted_time = unformatted_date.split()[5]  # 14:43
        unformatted_hour = unformatted_time.split(":")[0]
        unformatted_minute = unformatted_time.split(":")[1]
        if unformatted_minute[2:] == 'PM':
            unformatted_hour = str(int(unformatted_hour) + 12)
        unformatted_minute = unformatted_minute[:2]

        item['publish_date'] = unformatted_year+"/"+unformatted_month+"/"+unformatted_day+" "+unformatted_hour+":"+unformatted_minute+":00"
        raw_sentences = response.xpath(
            '//*[@id="ctl00_ContentPlaceHolder1_storyContainer"]/span[4]//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip()
        return item
