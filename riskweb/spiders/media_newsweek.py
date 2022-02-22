"""
新闻周刊 爬虫
"""
import scrapy
import time
import scrapy
import logging
from riskweb.items import ArticleItem

logger = logging.getLogger(__name__)

class NewsweekSpider(scrapy.Spider):
    name = 'media_newsweek'
    allowed_domains = ['newsweek.com']

    def start_requests(self):
        #开始爬取网址
        start_urls = [
            'https://www.newsweek.com/us',
            'https://www.newsweek.com/world',
            'https://www.newsweek.com/business',
            'https://www.newsweek.com/tech-science',
            'https://www.newsweek.com/sports',
            'https://www.newsweek.com/health',
        ]
        # 发送请求
        for i in range(0, len(start_urls)):
            yield scrapy.Request(start_urls[i], self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):
        #基础网址
        BASEURL = "https://www.newsweek.com/"
        #文章详情链接
        article_urls = response.xpath(
            '//*[@id="block-nw-nw-archive"]/div/div[3]/article/div[@class="inner"]/h3/a/@href').extract()

        for article_url in article_urls:
            article_url = f'{BASEURL}{article_url}'
            yield scrapy.Request(article_url, self.parse_article)

        #分页链接
        next_page_url = response.xpath(
            '//*[@id="block-nw-nw-archive"]/div/div[@class="item-list"]/ul/li[@class="pager-next last"]/a/@href').extract_first()
        #如果存在下一页，继续请求
        if next_page_url is not None:
            next_page_url = f'{BASEURL}{next_page_url}'
            yield scrapy.Request(next_page_url, self.parse_dictionary, dont_filter=True)

    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = response.xpath('//*[@id="block-system-main"]/div/article/header/h1/text()').extract_first()
        item['media_name'] = '新闻周刊'
        item['url'] = response.url
        item['topic'] = response.xpath('//*[@id="v_article"]/div[3]/a/span/text()').extract_first().replace('\n', '')

        item['author'] = response.xpath('//*[@id="block-system-main"]/div/article/header/div[@class="byline"]/span/a/text()').extract_first().replace('\n', '')

        publish_date_list = response.xpath('//*[@id="block-system-main"]/div/article/header/div[@class="byline"]/time/text()').extract()
        publish_date = ''.join(publish_date_list).replace('On', '').replace('at', '').replace('EDT', '').replace('EST', '').replace(' ', '').strip()
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date, "%m/%d/%y%I:%M%p"))

        raw_sentences = response.xpath('//*[@id="v_article"]/div[@class="article-body v_text paywall"]/p/text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip()

        return item