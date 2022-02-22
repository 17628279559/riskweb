"""
爱民众新闻 爬虫
"""
import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class IcrowdSpider(scrapy.Spider):
    name = 'media_icrowd'
    allowed_domains = ['icrowdnewswire.com']

    def start_requests(self):
        #开始爬取网址
        start_urls = [
            'https://icrowdnewswire.com/newsroom/']
        #发送请求
        yield scrapy.Request(start_urls[0], self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):
        #文章详情链接
        article_urls = response.xpath(
            '//section[@class="container mt-3 mb-5"]/div[@class="container"]/div[@class="newsroom_posts"]/div/div/div/div[2]/h3/a/@href').extract()

        for article_url in article_urls:
            yield scrapy.Request(article_url, self.parse_article)

        #分页链接
        next_page_url = response.xpath(
            '//section[@class="container mt-3 mb-5"]/div[@class="container"]/div[@class="newsroom_posts"]/div[@class="row text-center pb-2 pt-3"]/div/div/a[@class="nextpostslink"]/@href').extract_first()
        #如果存在下一页，继续请求
        if next_page_url is not None:
            yield scrapy.Request(next_page_url, self.parse_dictionary, dont_filter=True)

    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = response.xpath('//section[@class="legal_detailinfo"]/div/div[@class="row col-md-12 single_release_info"]/h1/text()').extract_first()
        item['media_name'] = '爱民众新闻'
        item['url'] = response.url
        item['topic'] = ''

        item['author'] = ''

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
        unformatted_date = response.xpath(
            '//section/div/div[@class="row col-md-12 single_release_info"]/div/span/text()').extract_first().replace('ET', '')
        unformatted_month = unformatted_date.split()[0]
        fomattted_month = month_spec[unformatted_month]
        unformatted_date = unformatted_date.replace(unformatted_month, fomattted_month).replace(' ', '')
        if unformatted_date:
            item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(unformatted_date, "%B%d,%Y%I:%M%p"))#May25,20217:09AM


        raw_sentences = response.xpath('//section[@class="legal_detailinfo"]/div/div[@class="mt-5"]//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip()

        return item
