"""
24小时实时新闻 爬虫
"""
import scrapy
import time
import logging
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)


class MediaIlsole24oreSpider(scrapy.Spider):
    name = 'media_ilsole24ore'
    allowed_domains = ['ilsole24ore.com']
    start_urls = ['http://ilsole24ore.com/']

    def start_requests(self):
        # 基础网址
        BASEURL = 'https://www.ilsole24ore.com'
        #开始爬取网址
        start_urls = [
            '/sez/economia',
            '/sez/italia',
            '/sez/mondo',
            '/sez/finanza',
            '/sez/risparmio',
            '/sez/norme-e-tributi',
            '/sez/commenti',
            '/sez/management',
            '/sez/salute',
            '/sez/how-to-spend-it',
            '/sez/tecnologia',
            '/sez/cultura',
            '/sez/motori',
            '/sez/moda',
            '/sez/casa',
            '/sez/viaggi',
            '/sez/food',
            '/sez/sport24',
            '/sez/arteconomy',
            '/sez/sostenibilita',
        ]
        for i in range(0, len(start_urls)):
            yield scrapy.Request(BASEURL + start_urls[i], self.parse_paths, dont_filter=True)

    def parse_paths(self, response): # 从各话题主页面找到所有的子级话题页面路径
        # 基础网址
        BASEURL = 'https://www.ilsole24ore.com'

        # 子级页面路径
        topic_paths = response.xpath('//div[contains(@class,"htop-wrap")]/div[2]//a/@href').extract()
        for topic_path in topic_paths:
            if '/sez' in topic_path:
                yield scrapy.Request(BASEURL + topic_path, self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):# 从各子级话题页面找到 所有的文章路径 与 唯一话题分页阅读页面路径
        # 基础网址
        BASEURL = 'https://www.ilsole24ore.com'

        # 文章详情链接
        article_urls = response.xpath(
            '//div[@class="col-lg-8"]//li[@class="list-lined-item"]//*[contains(@class,"aprev-title")]/a/@href').extract()

        for article_url in article_urls:
            yield scrapy.Request(BASEURL + article_url, self.parse_article, dont_filter=False)

        pagination_path = response.xpath('//div[@class="collapse"]/div[@class="text-right"]/a/@href').extract_first()
        if pagination_path is not None:
            yield scrapy.Request(BASEURL + pagination_path, self.parse_pagination, dont_filter=True)

    def parse_pagination(self, response): # 从各话题分页阅读页面找到所有的 文章路径 与 下一页路径
        # 基础网址
        BASEURL = 'https://www.ilsole24ore.com'

        # 文章详情链接
        article_urls = response.xpath(
            '//div[@class="col-lg-8"]//li[@class="list-lined-item"]//*[contains(@class,"aprev-title")]/a/@href').extract()
        for article_url in article_urls:
            yield scrapy.Request(BASEURL + article_url, self.parse_article, dont_filter=False)

        # 分页链接
        next_page_url = response.xpath('//nav[contains(@class,"pager")]/ul/li[last()]/a')
        statue = next_page_url.xpath('./@class').extract_first()
        # 如果存在下一页，继续请求
        if statue is not None and 'disabled' not in statue:
            next_page_url = next_page_url.xpath('./@href').extract_first()
            yield scrapy.Request(BASEURL + next_page_url, self.parse_pagination, dont_filter=True)

    def parse_article(self, response):
        # 调取参数
        item = ArticleItem()
        # 进入每篇文章header部分
        header = response.xpath('//div[contains(@class,"ahead")]')
        item['title'] = header.xpath('./*[contains(@class,"atitle")]/text()').extract_first()
        item['media_name'] = '24小时实时新闻'
        item['url'] = response.url
        item['topic'] = header.xpath('./*[@class="meta"]/span/text()').extract_first()
        author = header.xpath('./*[@class="auth"]/text()').extract_first()
        if author is not None:
            item['author'] = author.strip()
        else:
            item['author'] = 'ilsole24ore'
        publish_date = header.xpath('./*[@class="meta"]/time/text()').extract_first().strip()
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
                                             time.strptime(publish_date, "%d %B %Y"))  # 12 luglio 2021

        raw_sentences = response.xpath('//p[@class="atext"]/text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences)

        return item