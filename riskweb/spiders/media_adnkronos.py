"""
AKI新闻社 爬虫
"""
import scrapy
import time
import logging
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)


class MeidaAdnkronosSpider(scrapy.Spider):
    name = 'media_adnkronos'
    allowed_domains = ['adnkronos.com']
    start_urls = ['https://www.adnkronos.com']

    def parse(self, response, **kwargs): # 从主页找到所有的话题路径
        # 基础网址
        BASEURL = 'https://www.adnkronos.com'
        topic_paths = response.xpath('//li[contains(@class,"link-item")]/a/@href').extract()
        for topic_path in topic_paths:
            if 'www' not in topic_path:
                yield scrapy.Request(BASEURL + topic_path, self.parse_pagination, dont_filter=True)

    def parse_pagination(self, response): # 从各话题页面找到所有的分页路径
        # 基础网址
        BASEURL = 'https://www.adnkronos.com'

        # 分页链接
        next_page_urls = response.xpath('//ul[@class="pagination"][1]/li/a/@href').extract()
        if len(next_page_urls) == 0:
            yield scrapy.Request(response.url, self.parse_dictionary, dont_filter=True)
        else:
            # 如果存在下一页，继续请求
            for next_page_url in next_page_urls:
                yield scrapy.Request(BASEURL + next_page_url, self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):# 从各话题页面找到所有的文章路径
        # 基础网址
        BASEURL = 'https://www.adnkronos.com'

        # 文章详情链接
        article_urls = response.xpath(
            '//section[contains(@class,"cat-main")]/article//*[@class="title"]/a/@href').extract()

        for article_url in article_urls:
            yield scrapy.Request(BASEURL + article_url, self.parse_article, dont_filter=False)

    def parse_article(self, response):
        # 调取参数
        item = ArticleItem()
        # 进入每篇文章header部分
        header = response.xpath('//header[@class="top-head"]')
        item['title'] = header.xpath('.//*[@class="title"]/text()').extract_first().strip()
        item['media_name'] = 'AKI新闻社'
        item['url'] = response.url
        topics = header.xpath('.//ul[@class="bread-list"]/li//text()').extract()
        item['topic'] = '|'.join(topics)

        item['author'] = 'adnkronos'
        publish_date = header.xpath('.//div[@class="left"]/div[1]/span/text()').extract_first() # 01 agosto 2021 | 16.03
        month_dic = {
            'gennaio': 'January',
            'febbraio': 'February',
            'marzo': 'March',
            'aprile': 'April',
            'maggio': 'May',
            'giugno': 'June',
            'luglio': 'July ',
            'agosto': 'August',
            'settembre': 'September',
            'ottobre': 'October',
            'novembre': 'November',
            'dicembre': 'December',
        }
        for key in month_dic.keys():
            if key in publish_date:
                publish_date = publish_date.replace(key,month_dic[key])

        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S",
                                             time.strptime(publish_date, "%d %B %Y | %H.%M"))  # 03 June 2021 | 15.10

        raw_sentences = response.xpath('//div[@class="ar-main"]/p//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences)

        return item