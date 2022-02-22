"""
实时金融新闻 爬虫
"""
import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem

logger = logging.getLogger(__name__)


class RttnewsSpider(scrapy.Spider):
    name = 'media_rttnews'
    allowed_domains = ['rttnews.com']

    def start_requests(self):
        start_urls = []
        WORDS = ['top-story', 'breaking-news', 'earnings', 'ipos', 'mergers', 'canadian-news', 'uk-top-story', 'ws-events',
                 'us-economic-news', 'european-economic-news', 'asian-economic-news', 'global-economic-news', 'us-commentary',
                 'european-commentary', 'asian-commentary', 'canadian-commentary', 'indian-commentary', 'commodities',
                 'us-treasury-markets', 'forex-commentary', 'us-political-news', 'white-house', 'general-news', 'forex-top-story',
                 'currency-markets', 'coronavirus', 'diet-nutrition-fitness', 'kids-health', 'mens-health', 'womens-health',
                 'drug-development', 'mental-health', 'music', 'blockchain', 'cryptocurrency', 'stock-alerts']
        for word in WORDS:
            start_url = f"https://www.rttnews.com/list/{word}.aspx"
            start_urls.append(start_url)
        # 发送请求
        for i in range(0, len(start_urls)):
            yield scrapy.Request(start_urls[i], self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):
        BASEURL = "https://www.rttnews.com"
        #文章详情链接
        article_urls = response.xpath(
            '//*[@id="mainlayout"]/div[@class="contentPage"]/div[@class="leftColumn"]/div/div/div/h2/a/@href').extract()

        for article_url in article_urls:
            yield scrapy.Request(article_url, self.parse_article)

        #分页链接
        next_page_url = response.xpath('//*[@id="ctl00_CPI_lnkNext"]/@href').extract_first()
        #如果存在下一页，继续请求
        if next_page_url is not None:
            next_page_url = f'{BASEURL}{next_page_url}'
            yield scrapy.Request(next_page_url, self.parse_dictionary, dont_filter=True)

    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = response.xpath('//*[@id="ctl00_CPI_divStoryHeadline"]/h1/text()').extract_first()
        item['media_name'] = '实时金融新闻'
        item['url'] = response.url
        item['topic'] = ''
        item['author'] = response.xpath('//*[@id="ctl00_CPI_spnAuthor"]/a/text()').extract_first()

        publish_date = response.xpath('//*[@id="ctl00_CPI_spnEnteredDate"]/span/time/text()').extract_first().replace('ET','').replace(' ','')
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date, "%m/%d/%Y%I:%M%p")) #5/28/2021 8:38 AM ET

        raw_sentences = response.xpath('//*[@id="ctl00_CPI_dvBody"]/p/text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip()

        return item