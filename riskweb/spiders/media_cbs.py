"""
CBS新闻 爬虫
"""
import time
import scrapy
import logging
from riskweb.items import ArticleItem

logger = logging.getLogger(__name__)

class CbsSpider(scrapy.Spider):
    name = 'media_cbs'
    allowed_domains = ['cbsnews.com']
    def start_requests(self):
        #开始爬取网址
        start_urls = [
            'http://www.cbsnews.com/48-hours/']
        #发送请求
        yield scrapy.Request(start_urls[0], self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):
        #基础网址
        BASEURL = "http://www.cbsnews.com"
        #文章详情链接
        article_urls = response.xpath(
            '//*[@id="module-"]/li/div/a[2]/@href').extract()

        for article_url in article_urls:
            article_url = f'{BASEURL}{article_url}'
            yield scrapy.Request(article_url, self.parse_article)

    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = response.xpath('//*[@id="article"]/header/h1/text()').extract_first()
        item['media_name'] = 'CBS新闻'
        item['url'] = response.url
        item['topic'] = ''

        item['author'] = response.xpath('//*[@id="article"]/div[1]/ul[1]/li[@class="std-social correspondent-box"]/span[@class="sharebar-text"]/text()').extract_first()

        month_spec = {
            'Jan': 'January',
            'Feb': 'February',
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
        unformatted_date = response.xpath('//*[@id="article"]/div[1]/ul[1]/li[@class="std-social date-box"]/span[2]/text()').extract_first().replace('\n','')
        unformatted_month = unformatted_date.split()[0]

        fomattted_month = month_spec[unformatted_month]
        unformatted_date = unformatted_date.replace(unformatted_month, fomattted_month)

        publish_date_year = response.xpath('//*[@id="article"]/div[1]/ul[1]/li[@class="std-social date-box"]/span[1]/text()').extract_first().replace('\n','')
        publish_date = publish_date_year + unformatted_date
        item['publish_date'] = publish_date
        if publish_date:
            item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date, "%Y%B %d"))

        raw_sentences = response.xpath('//*[@id="article-entry"]/div//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip()
        return item
