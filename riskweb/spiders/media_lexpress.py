"""
毛里求斯快讯 爬虫
法语

"""
import time
import scrapy
import logging

from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaLexpressSpider(scrapy.Spider):
    name = 'media_lexpress'
    allowed_domains = ['lexpress.mu']

    def start_requests(self):
        #开始爬取网址
        start_urls = []
        words = ['politique', 'societe', 'economie', 'regions', 'idees', 'sport', 'international', 'vous']
        for word in words:
            start_url = f"https://www.lexpress.mu/{word}/1"
            start_urls.append(start_url)

        #发送请求
        for i in range(0, len(start_urls)):
            yield scrapy.Request(start_urls[i], self.page_requests, dont_filter=True)

    def page_requests(self, response):
        # 所有页数
        page_urls = response.xpath(
            '//div[@class="pagination-slide-wrapper"]/a/@href').extract()
        # print(page_urls)
        for page_url in page_urls:
            yield scrapy.Request(page_url, self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):
        #文章详情链接
        article_urls = response.xpath(
            '//div[@class="description-wrapper"]/div[@class="title-wrapper"]/div/a/@href').extract()
        for article_url in article_urls:
            yield scrapy.Request(article_url, self.parse_article)

    def parse_article(self, response):
        # 调取参数
        item = ArticleItem()
        # 进入每篇文章获取标题
        item['title'] = response.xpath('//article/div[@class="lx-block-header"]/h1/text()').extract_first()
        item['media_name'] = '毛里求斯快讯'
        item['url'] = response.url
        item['topic'] = ''
        item['author'] = response.xpath('//div[@class="meta-data-details"]/span/a/text()').extract_first()

        month_spec = {
            'jan': 'January',
            'fév': 'February',
            'mar': 'March',
            'avr': 'April',
            'mai': 'May',
            'jun': 'June',
            'jul': 'July',
            'août': 'August',
            'sep': 'September',
            'oct': 'October',
            'nov': 'November',
            'déc': 'December'
        }
        unformatted_date = response.xpath(
            '//div[@class="meta-data-details"]/div/span[1]/a/text()').extract()
        unformatted_date = ''.join(unformatted_date).replace('\n', '').strip()

        # 将法语的月份替换为英文月份
        unformatted_month = unformatted_date.split()[1]
        formatted_month = month_spec[unformatted_month]
        unformatted_date = unformatted_date.replace(unformatted_month, formatted_month)

        formatted_min = response.xpath('//div[@class="meta-data-details"]/div/span[2]/text()').extract()
        formatted_min = ''.join(formatted_min).replace('\n', '').strip()
        publish_date = unformatted_date + formatted_min

        #时间格式转换
        if publish_date:
            item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date, "%d %B %Y%H:%M"))

        raw_sentences = response.xpath('//div[@class="article-content content"]/p/text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip().replace('\n', '')

        return item


