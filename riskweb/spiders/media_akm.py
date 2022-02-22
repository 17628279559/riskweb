"""
AK&M新闻 爬虫
"""
import time
import scrapy
from riskweb.items import ArticleItem
import logging
logger = logging.getLogger(__name__)

class AKMSpider(scrapy.Spider):
    name = 'media_akm'
    allowed_domains = ['akm.ru']
    def start_requests(self):
        #开始爬取网址
        start_urls = [
            'https://www.akm.ru/news/']
        #发送请求
        yield scrapy.Request(start_urls[0], self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):
        #基础网址
        BASEURL = "https://www.akm.ru"
        #文章详情链接
        article_urls = response.xpath(
            '/html/body/div[2]/div[5]/div/div/div/section/div[1]/div/div/div/div/h3/a/@href').extract()
        for article_url in article_urls:
            article_url = f'{BASEURL}{article_url}'
            yield scrapy.Request(article_url, self.parse_article)

        nextpage_url = response.xpath(
            '//*[@id="section_681133c_loadmore"]/@href').extract_first()
        print("this is nextpage_url")
        print(nextpage_url)
        yield scrapy.Request(BASEURL+nextpage_url, self.parse_dictionary, dont_filter=True)

    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题

        item['title'] = response.xpath(
            '//*[@id="wrapper"]/div[5]/div/div/div/div[1]/div[1]/h1/text()').extract_first()

        item['media_name'] = 'akm新闻'
        item['url'] = response.url
        item['topic'] = ''
        item['author'] = ''

        month_spec = {
            'Январь': '01',
            'Февраль': '02',
            'Март': '03',
            'Апрель': '04',
            'май': '05',
            'июня': '06',
            'июля': '07',
            'Август': '08',
            'Сентябрь': '09',
            'Октябрь': '10',
            'Ноябрь': '11',
            'декабрь': '12'
        }

        unformatted_date = response.xpath(
            '//*[@id="wrapper"]/div[5]/div/div/div/div[1]/div[1]/div/div[1]/time/text()').extract_first()
        # '\r\n                    01 июля 2021 14:43                '
        unformatted_day = unformatted_date.split()[0]  # 01
        unformatted_month = month_spec[unformatted_date.split()[1]]  # июля
        unformatted_year = unformatted_date.split()[2]  # 2021
        unformatted_time = unformatted_date.split()[3]  # 14:43
        unformatted_hour = unformatted_time.split(":")[0]
        unformatted_minute = unformatted_time.split(":")[1]
        print(unformatted_day, unformatted_month, unformatted_year, unformatted_time)
        item['publish_date'] = unformatted_year+"/"+unformatted_month+"/"+unformatted_day+" "+unformatted_hour+":"+unformatted_minute+":00"
        # fomattted_month = month_spec[unformatted_month]
        # unformatted_date = unformatted_date.replace(unformatted_month, fomattted_month)
        # publish_date_year = response.xpath('//*[@id="article"]/div[1]/ul[1]/li[@class="std-social date-box"]/span[1]/text()').extract_first().replace('\n','')
        # publish_date = publish_date_year + unformatted_date
        # item['publish_date'] = publish_date
        # if unformatted_date:
        #     item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(unformatted_date, "%Y%B %d"))
        # item['publish_date']=time.strftime("%Y/%m/%d %H:%M:%S", unformatted_year,unformatted_month,unformatted_day,unformatted_hour,unformatted_minute,0)





        login=response.xpath(
            '//*[@id="wrapper"]/div[5]/div/div/div/div[1]/h2/text()').extract_first()
        if login is not None:
            item['content'] = ''
            return item

        raw_sentences = response.xpath('//*[@id="wrapper"]/div[5]/div/div/div/div[1]/div[2]/p/text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip()

        return item
