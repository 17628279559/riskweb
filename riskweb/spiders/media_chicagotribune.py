"""
芝加哥论坛报 爬虫
"""
import scrapy
from riskweb.items import ArticleItem
import logging
import time
logger = logging.getLogger(__name__)
import re


class MeidaChicagotribuneSpider(scrapy.Spider):
    name = 'media_chicagotribune'
    allowed_domains = ['chicagotribune.com']
    start_urls = ['http://chicagotribune.com/']

    def start_requests(self):
        start_urls = [
            'https://www.chicagotribune.com/autos/',
            'https://www.chicagotribune.com/news/breaking/',
            'https://www.chicagotribune.com/news/obituaries/',
            'https://www.chicagotribune.com/midwest/',
            'https://www.chicagotribune.com/nation-world/',
            'https://www.chicagotribune.com/investigations/',
            'https://www.chicagotribune.com/suburbs/',
            'https://www.chicagotribune.com/suburbs/aurora-beacon-news/',
            'https://www.chicagotribune.com/suburbs/elgin-courier-news/',
            'https://www.chicagotribune.com/suburbs/naperville-sun/',
            'https://www.chicagotribune.com/suburbs/lake-county-news-sun/',
            'https://www.chicagotribune.com/suburbs/post-tribune/',
            'https://www.chicagotribune.com/suburbs/daily-southtown/',
            'https://www.chicagotribune.com/news/criminal-justice/',
            'https://www.chicagotribune.com/news/environment/',
            'https://www.chicagotribune.com/business/transportation/',
            'https://www.chicagotribune.com/business/career-finance/',
            'https://www.chicagotribune.com/business/careers/top-workplaces/',
            'https://www.chicagotribune.com/coronavirus/',
            'https://www.chicagotribune.com/dining/',
            'https://www.chicagotribune.com/dining/craving/',
            'https://www.chicagotribune.com/dining/recipes/',
            'https://www.chicagotribune.com/dining/reviews/',
            'https://www.chicagotribune.com/espanol/',
            'https://www.chicagotribune.com/espanol/deportes/',
            'https://www.chicagotribune.com/espanol/entretenimiento/',
            'https://www.chicagotribune.com/entertainment/what-to-watch/',
            'https://www.chicagotribune.com/entertainment/things-to-do/',
            'https://www.chicagotribune.com/entertainment/music/',
            'https://www.chicagotribune.com/entertainment/theater/',
            'https://www.chicagotribune.com/entertainment/theater/broadway/',
            'https://www.chicagotribune.com/entertainment/theater/chris-jones/',
            'https://www.chicagotribune.com/entertainment/theater/reviews/',
            'https://www.chicagotribune.com/horoscopes/',
            'https://www.chicagotribune.com/travel/',
            'https://www.chicagotribune.com/lifestyles/ask-amy/',
            'https://www.chicagotribune.com/people/',
            'https://www.chicagotribune.com/lifestyles/health/',
            'https://www.chicagotribune.com/lifestyles/parenting/',
            'https://www.chicagotribune.com/lifestyles/home-and-garden/',
            'https://www.chicagotribune.com/lifestyles/fashion/',
            'https://www.chicagotribune.com/columns/',
            'https://www.chicagotribune.com/opinion/editorials/',
            'https://www.chicagotribune.com/opinion/',
            'https://www.chicagotribune.com/opinion/commentary/',
            'https://www.chicagotribune.com/opinion/letters/',
            'https://www.chicagotribune.com/opinion/chicago-forward/',
            'https://www.chicagotribune.com/politics/',
            'https://www.chicagotribune.com/real-estate/',
            'https://www.chicagotribune.com/sports/',
            'https://www.chicagotribune.com/sports/bears/',
            'https://www.chicagotribune.com/sports/cubs/',
            'https://www.chicagotribune.com/sports/white-sox/',
            'https://www.chicagotribune.com/sports/olympics/',
            'https://www.chicagotribune.com/sports/bulls/',
            'https://www.chicagotribune.com/sports/blackhawks/',
            'https://www.chicagotribune.com/sports/sky/',
            'https://www.chicagotribune.com/sports/soccer/',
            'https://www.chicagotribune.com/sports/blackhawks/',
        ]
        # 发送请求
        for i in range(0, len(start_urls)):
            yield scrapy.Request(start_urls[i], self.parse_page, dont_filter=False)

        yield  scrapy.Request('https://www.chicagotribune.com/paid-posts/?ntv_adpz=1568&ntv_pg=1', self.parse_dictionary, dont_filter=False)

    def parse_dictionary(self, response):
        article_urls = response.xpath('//a[contains(@class,"ntv-headline")]/@href').extract()
        for article_url in article_urls:
            yield scrapy.Request(article_url,self.parse_article,dont_filter=False)

        next_page = response.xpath('//a[@class="prx_pagination_next"]/@href').extract_first()
        if next_page is not None:
            yield scrapy.Request(next_page, self.parse_article, dont_filter=False)

    def parse_page(self, response):
        # 基础网址
        BASEURL = 'https://www.chicagotribune.com'
        article_urls = response.xpath('//a[@data-tr-content-id]/@href').extract()
        for article_url in article_urls:
            if BASEURL in article_url:
                next_request_url = article_url
            else:
                next_request_url = BASEURL + article_url
            yield scrapy.Request(next_request_url,self.parse_article,dont_filter=False)

    def parse_article(self,response):
        # 调取参数
        item = ArticleItem()
        # 进入每篇文章的文章信息节点
        pre_info = response.xpath('//div[contains(@data-pb-name,"Article Header")]')
        # 进入每篇文章获取标题
        item['title'] = pre_info.xpath('//h1/text()').extract_first()
        item['media_name'] = '芝加哥论坛报'
        item['url'] = response.url
        item['topic'] = ''.join(pre_info.xpath('//a[contains(@class,"tag")]/text()').extract())
        author = pre_info.xpath('//a[@rel="author"]/span/text()').extract_first()
        if author is None:
            author = pre_info.xpath('//span[contains(@class,"byline-article")]/span/text()').extract_first()
        item['author'] = author
        publish_date = ''.join(pre_info.xpath('//div[contains(@class,"timestamp-wrapper")]/div[2]/span/text()').extract()) #  Jul 18, 2021 at 12:05 AM
        # 正则匹配文章的发布时间
        publish_date_pattern = re.compile(
            r'.+ \d+, \d{4} at \d+:\d+ ..') #  Jul 18, 2021 at 12:05 AM
        publish_date_matched = re.findall(publish_date_pattern, publish_date.strip())[0]

        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S",
                                             time.strptime(publish_date_matched,
                                                           "%b %d, %Y at %H:%M %p"))  # Jul 18, 2021 at 12:05 AM

        raw_sentences = response.xpath('//div[@data-type="text"]//p//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip()
        return item