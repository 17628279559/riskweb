"""
市场观察 爬虫
"""
import scrapy
import json
from riskweb.items import ArticleItem
import logging
import time
import re
logger = logging.getLogger(__name__)


class MediaMarketwatchSpider(scrapy.Spider):
    name = 'media_marketwatch'
    allowed_domains = ['marketwatch.com']

    def start_requests(self):
        # 基础网址
        BASEURL = 'https://www.marketwatch.com'
        #起始爬取网址
        topic_paths = [
            '/latest-news',
            '/markets',
            '/investing',
            '/personal-finance',
            '/economy-politics',
            '/economy-politics/federal-reserve',
            '/column/economic-report',
            '/column/capitol-report'
        ]

        # 发送请求
        for topic_path in topic_paths:
            yield scrapy.Request(BASEURL + topic_path, self.parse_dictionary, meta={
                'topicPath':topic_path
            }, dont_filter=False)


    def parse_dictionary(self, response):
        # 基础网址
        BASEURL = 'https://www.marketwatch.com'
        # 话题路径
        topicPath = response.meta['topicPath']

        # 解析动态请求返回的页面
        if 'partial=true' in response.url:
            article_urls = response.xpath('//div[contains(@class,"column")]//h3[@class="article__headline"]//a/@href').extract()
            for article_url in article_urls:
                yield scrapy.Request(article_url, self.parse_article, dont_filter=False)

            # 获取动态请求的参数值
            channelId = response.meta['channelId']
            position = response.meta['position']

            # 解析当前请求的最后一条消息的msgid值
            messageNumber = response.xpath(
                '//div[contains(@class,"column")]/div[contains(@class,"collection__elements")]/div[last()]/@data-msgid').extract_first()

        # 解析每个topic下的初始主页面
        else:
            container = response.xpath('//div[contains(@class,"region--primary")]')
            top_headlines = container.xpath('./div[contains(@class,"component--layout")]')
            more_headlines = container.xpath('./div[contains(@class,"more-headlines")]')
            article_urls = top_headlines.xpath(
                './div[contains(@class,"column")]//h3[@class="article__headline"]//a/@href').extract() \
                           + more_headlines.xpath(
                './div[contains(@class,"column")]//h3[@class="article__headline"]//a/@href').extract()
            for article_url in article_urls:
                yield scrapy.Request(article_url, self.parse_article, dont_filter=False)

            # 解析动态请求的参数值
            channelId = more_headlines.xpath('./div[contains(@class,"column")]/@data-channel-id').extract_first()
            position = more_headlines.xpath('./div[contains(@class,"column")]/@data-layout-position').extract_first()

            # 解析当前请求的最后一条消息的msgid值
            messageNumber = more_headlines.xpath(
                './div[contains(@class,"column")]/div[contains(@class,"collection__elements")]/div[last()]/@data-msgid').extract_first()

        # 特殊页面的请求（动态请求的参数不完全相同）
        if topicPath == '/column/capitol-report':
            pageNumber = 1
            if 'pageNumber' in response.meta.keys():
                pageNumber = response.meta['pageNumber'] + 1
            next_request_url = BASEURL + topicPath + '?pageNumber=' + str(pageNumber) + '&position=3.0&partial=true'

            yield scrapy.Request(
                next_request_url,
                self.parse_dictionary,
                meta={
                    'channelId': channelId,
                    'position': position,
                    'messageNumber': messageNumber,
                    'topicPath': topicPath,
                    'pageNumber':pageNumber,
                },
                dont_filter=False)

        # 生成普通页面的数据动态请求
        else:
            next_request_url = BASEURL + topicPath + '?messageNumber=' + str(messageNumber) + '&channelId=' + str(
                channelId) + '&position=' + str(position) + '&partial=true'

            yield scrapy.Request(
                next_request_url,
                self.parse_dictionary,
                meta={
                    'channelId': channelId,
                    'position': position,
                    'messageNumber': messageNumber,
                    'topicPath': topicPath,
                },
                dont_filter=False)

    def parse_article(self, response):
        # 调取参数
        item = ArticleItem()
        item['media_name'] = '市场观察'
        item['url'] = response.url

        # 特殊文章 video
        if '/video' in response.url:
            video_infos = response.xpath('//div[contains(@class,"video")]')
            item['title'] = video_infos.xpath('./div/h3/text()').extract_first().replace(
                r'\xa0', '').replace('\t', '').replace('\n', '').strip()
            item['topic'] = 'video'
            item['author'] = ''
            publish_date = video_infos.xpath('./div/p[@class="article__timestamp"]/text()').extract_first()

            publish_date_pattern = re.compile(
                r"(.+ \d+, \d{4} at \d+:\d+ ..) ET")  # Jun. 3, 2021 at 6:45 AM ET
            publish_date = re.findall(publish_date_pattern, publish_date)[0]
            item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S",
                                                 time.strptime(publish_date,
                                                               "%b %d, %Y at %H:%M %p"))  # Jun. 3, 2021 at 6:45 AM ET

            raw_sentences = video_infos.xpath('./div/div[contains(@class,"article__description")]/p/text()').extract()
            raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
            item['content'] = '\n'.join(raw_sentences)

        else:
            article_infos = response.xpath('//div[@class="article__masthead"]')
            # 进入每篇文章获取标题
            item['title'] = article_infos.xpath('./h1[@class="article__headline"]/text()').extract_first().replace(
                r'\xa0', '').replace('\t', '').replace('\n', '').strip()
            # topic
            topics = response.xpath('//div[contains(@class,"breadcrumbs")]/ol/li/a/text()').extract()
            if len(topics) == 1:
                item['topic'] = topics[0]
            else:
                item['topic'] = '|'.join(topics)
            # author
            authors = article_infos.xpath('./div[contains(@class,"article__byline")]/div//h4//text()').extract()
            if len(authors) == 1:
                item['author'] = authors[0]
            else:
                item['author'] = ''.join(authors)
            # publish_date
            publish_date = article_infos.xpath('./time/text()').extract_first()
            # 正则匹配发布时间的有效数据
            if 'Updated' in publish_date:
                publish_date_pattern = re.compile(
                    r"Updated: (.+ \d+, \d{4} at \d+:\d+ .\..\.) .+")  # Last Updated: July 7, 2021 at 4:25 p.m. ET
            elif 'Published' in publish_date:
                publish_date_pattern = re.compile(
                    r"Published: (.+ \d+, \d{4} at \d+:\d+ .\..\.) .+")  # Published: July 8, 2021 at 12:04 a.m. ET
            else:
                publish_date.replace('\t', '').replace('\n', '').strip()
                publish_date_pattern = re.compile(
                    r"(.+ \d+, \d{4} at \d+:\d+ .\..\.) .+")  # July 6, 2021 at 7:18 p.m. ET

            publish_date = re.findall(publish_date_pattern, publish_date)[0]
            try:
                item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S",
                                                     time.strptime(publish_date.replace('a.m.', 'am').replace('p.m.', 'pm'),
                                                                   "%B %d, %Y at %H:%M %p"))  # July 8, 2021 at 12:04 am
            except ValueError:
                item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S",
                                                     time.strptime(
                                                         publish_date.replace('a.m.', 'am').replace('p.m.', 'pm'),
                                                         "%b %d, %Y at %H:%M %p"))  # Feb. 1, 2021 at 5:40 pm

            # content
            raw_sentences = response.xpath('//div[contains(@class,"article__body")]/p//text()').extract() \
                            + response.xpath('//div[contains(@class,"article__body ")]/div[contains(@class,"paywall")]//text()').extract()
            raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
            item['content'] = '\n'.join(raw_sentences)
        return item

