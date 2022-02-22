"""
利比亚新闻社 爬虫
"""
import scrapy
import logging
import time
from riskweb.items import ArticleItem
import re
logger = logging.getLogger(__name__)

class MediaLananewsSpider(scrapy.Spider):
    name = 'media_lananews'
    allowed_domains = ['lana-news.ly']

    def start_requests(self):
        # 开始爬取网址
        start_urls = [
            'https://lana-news.ly/index.php?lang=ar',
            'https://lana-news.ly/categories.php?lang=ar&ctg_id=5',
            'https://lana-news.ly/categories.php?lang=ar&ctg_id=6',
            'https://lana-news.ly/categories.php?lang=ar&ctg_id=11',
            'https://lana-news.ly/categories.php?lang=ar&ctg_id=14',
            'https://lana-news.ly/categories.php?lang=ar&ctg_id=13',
            'https://lana-news.ly/categories.php?lang=ar&ctg_id=18',
            'https://lana-news.ly/categories.php?lang=ar&ctg_id=21',
            'https://lana-news.ly/categories.php?lang=ar&ctg_id=8',
            'https://lana-news.ly/categories.php?lang=ar&ctg_id=9',
            'https://lana-news.ly/categories.php?lang=ar&ctg_id=10',
            'https://lana-news.ly/categories.php?lang=ar&ctg_id=20',
            'https://lana-news.ly/categories.php?lang=ar&ctg_id=19',
            'https://lana-news.ly/categories.php?lang=ar&ctg_id=22',
        ]
        # 发送请求
        for i in range(0, len(start_urls)):
            yield scrapy.Request(start_urls[i], self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):
        # 基础网址
        BASEURL = 'https://lana-news.ly/'
        # 文章主题
        topic = response.xpath('//div[@class="left-side"]/h3/text()[2]').extract()
        # 文章详情链接
        article_paths = response.xpath('//div[@class="news-content"]/h4/a/@href').extract()
        for article_path in article_paths:
            yield scrapy.Request(BASEURL + article_path, self.parse_article, meta={'topic':topic})

        # 分页链接
        next_page_path = response.xpath('//div[@class="left-side"]/a[contains(@title,"Next page is")]/@href').extract_first()
        # 如果存在下一页，继续请求
        if next_page_path is not None:
            yield scrapy.Request(BASEURL + next_page_path, self.parse_dictionary, dont_filter=True)

    def parse_article(self, response):
        # 调取参数
        item = ArticleItem()
        # 进入每篇文章获取标题
        item['title'] = response.xpath('//div[@class="artical"]/h2/text()').extract_first()
        item['media_name'] = '利比亚新闻社'
        item['url'] = response.url
        item['topic'] = response.meta['topic']

        # 获取文章的发布时间
        publish_date = response.xpath('//span[@class="publish_date"]/span/text()').extract_first()
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S",
                                             time.strptime(publish_date, "%Y-%m-%d %H:%M:%S"))  # 2021-01-03 10:18:21

        raw_sentences = response.xpath('//div[@class="main_post"]/p//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).replace(r'\xa0', '')

        return item
