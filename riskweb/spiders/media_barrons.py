"""
巴伦周刊 爬虫
"""
import scrapy
from riskweb.items import ArticleItem
import logging
import time
import re
logger = logging.getLogger(__name__)

class MediaBarronsSpider(scrapy.Spider):
    name = 'media_barrons'
    allowed_domains = ['barrons.com']
    start_urls = ['https://www.barrons.com/topics?mod=BOL_TOPNAV']
    count = 0

    def parse(self, response, **kwargs):
        # 基础网址
        BASEURL = 'https://www.barrons.com/'
        topics = response.xpath('//div/ul/li/a/text()').extract()
        for topic in topics:
            # 转到话题搜索页面地址：BASEURL + 'search?keyword=' + topic + '&page=1'
            yield scrapy.Request(BASEURL+'search?keyword='+topic+'&page=1', self.parse_dictionary, meta={'topic':topic}, dont_filter=False)

    def parse_dictionary(self, response):
        # 基础网址
        BASEURL = 'https://www.barrons.com/'
        # 文章详情链接
        article_urls = response.xpath('//span[@class="headline"]/parent::div/parent::a/@href').extract()
        for article_url in article_urls:
            yield scrapy.Request(article_url, self.parse_article, meta=response.meta, dont_filter=False)

        statue = response.xpath('//a[contains(@class,"pull-right")]/@style').extract_first()
        # 如果存在下一页，继续请求
        if statue is None or 'display:none;' not in statue:
            # 分页链接
            url = response.xpath('//a[contains(@class,"pull-right")]/@href').extract_first()
            yield scrapy.Request(BASEURL + url, self.parse_dictionary, meta=response.meta,  dont_filter=False)

    def parse_article(self,response):
        # 调取参数
        item = ArticleItem()
        # 进入每篇文章获取标题
        item['title'] = response.xpath('//h1[contains(@class,"article__headline")]/text()').extract_first()
        item['media_name'] = '巴伦周刊'
        item['url'] = response.url
        item['topic'] = response.meta['topic']

        pre_article_info = response.xpath('//div[@id="article_sector"]')
        author = pre_article_info.xpath('//div[contains(@class,"byline")]//a/span/text()').extract_first()
        if author is None:
            try:
                author = pre_article_info.xpath('//div[contains(@class,"byline")]//span/text()').extract_first().replace('By', '').strip()
            except AttributeError:
                author = ''
        item['author'] = author

        publish_date = pre_article_info.xpath('//time/text()').extract_first().replace('\t','').replace('\n','').replace('Sept','Sep').replace(' ET','').strip()
        if 'Updated' in publish_date:
            # 正则匹配文章的发布时间
            publish_date_pattern = re.compile(r'Updated (.+ \d{1,2}, \d{4} \d{1,2}:\d{1,2} .+) /')  #  Updated Nov. 6, 2019 5:00 am / Original Nov. 6, 2019 4:16 am
            publish_date_matched = re.findall(publish_date_pattern, publish_date)
            if len(publish_date_matched) == 0:
                publish_date_pattern = re.compile(r'Updated (.+ \d{1,2}, \d{4}) /')  # Updated June 28, 2021 / Original June 25, 2021
                publish_date_matched = re.findall(publish_date_pattern, publish_date)[0] + ' 00:00 am'
            else:
                publish_date_matched = publish_date_matched[0]
        else:
            # 正则匹配文章的发布时间
            publish_date_pattern = re.compile(r'.+ \d{1,2}, \d{4} \d{1,2}:\d{1,2} .+')  # June 29, 2021 10:30 am
            publish_date_matched = re.findall(publish_date_pattern, publish_date)[0]

        try:
            item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S",
                                             time.strptime(publish_date_matched, "%B %d, %Y %H:%M %p"))  # June 29, 2021 10:30 am
        except ValueError:
            item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S",
                                                 time.strptime(publish_date_matched,
                                                               "%b. %d, %Y %H:%M %p"))  # June 29, 2021 10:30 am

        article = response.xpath('//div[@id="article_sector"]/article/div[contains(@class,"article__body ")]')
        raw_sentences = article.xpath('/p/text()').extract()+\
                        article.xpath('/div[@class="paywall"]/*[self::p or self::h6]//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip()
        return item
