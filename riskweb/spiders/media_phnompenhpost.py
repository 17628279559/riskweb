"""
金边邮报 爬虫
"""
import scrapy
import json
from riskweb.items import ArticleItem
import logging
import time
import re
logger = logging.getLogger(__name__)


class MediaPhnompenhpostSpider(scrapy.Spider):
    name = 'media_phnompenhpost'
    allowed_domains = ['phnompenhpost.com']

    def start_requests(self):
        # 基础网址
        BASEURL = 'https://www.phnompenhpost.com'
        #开始爬取网址
        topic_paths = [
            '/national',
            '/business',
            '/lifestyle',
            '/special-reports',
            '/travel',
            '/sport',
            '/opinion',
            '/international',
        ]
        # 发送请求
        for topic_path in topic_paths:
            yield scrapy.Request(BASEURL + topic_path, self.parse_dictionary, meta={'topic':topic_path.replace('/','')},dont_filter=False)

    def parse_dictionary(self, response):
        # 基础网址
        BASEURL = 'https://www.phnompenhpost.com'
        # 文章详情链接
        article_urls = response.xpath('//div[@class="view-content"]/div/ul/li/h3/a/@href').extract()

        for article_url in article_urls:
            yield scrapy.Request(BASEURL + article_url, self.parse_article, meta= response.meta)

        # 分页链接
        next_page_url = response.xpath('//li[contains(@class,"pager-next")]/a/@href').extract_first()
        # 如果存在下一页，继续请求
        if next_page_url is not None:
            yield scrapy.Request(BASEURL + next_page_url, self.parse_dictionary, meta= response.meta, dont_filter=False)

    def parse_article(self, response):
        # 调取参数
        item = ArticleItem()
        # 进入每篇文章获取标题
        item['title'] = response.xpath('//div[contains(@class,"single-article-header")]/h2/text()').extract_first().replace(r'\xa0','').replace('\t','').replace('\n','').strip()
        item['media_name'] = '金边邮报'
        item['url'] = response.url
        item['topic'] = response.meta['topic']

        item['author'] = response.xpath('//div[@class="article-author-wrapper"]/p/a/span/text()').extract_first()
        publish_date = response.xpath('//div[@class="article-author-wrapper"]/p/text()').extract()
        if len(publish_date) == 2:
            publish_date = publish_date[1]
        else:
            publish_date = publish_date[0]
        publish_date_pattern = re.compile(r"Publication date (\d+ .+ \d{4} \| \d{2}:\d{2})")
        publish_date = re.findall(publish_date_pattern, publish_date)[0]
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S",
                                             time.strptime(publish_date, "%d %B %Y | %H:%M"))  # 27.01.2021 à 13h09

        raw_sentences = response.xpath('//div[@id="ArticleBody"]/p/text()').extract()
        if len(raw_sentences) == 0:
            raw_sentences = response.xpath('// article[ @ itemprop = "video"] / div / p / text()').extract()

        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences)

        return item
