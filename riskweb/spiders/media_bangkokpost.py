"""
曼谷邮报 爬虫
"""
import scrapy
import json
from riskweb.items import ArticleItem
import logging
import time
import re
import random
logger = logging.getLogger(__name__)


user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
        "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 "
        "(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 "
        "(KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 "
        "(KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 "
        "(KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 "
        "(KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 "
        "(KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 "
        "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 "
        "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
]

class MediaMarketwatchSpider(scrapy.Spider):
    name = 'media_bangkokpost'
    allowed_domains = ['bangkokpost.com']

    def start_requests(self):
        # 基础网址
        BASEURL = 'https://www.bangkokpost.com'
        #起始爬取网址
        topic_paths = [
            '/thailand/',
            '/world/',
            '/business/',
            '/opinion/',
            '/auto/',
            '/life/',
            #'/learning/', 全为视频
            '/vdo/',
            '/sports/',
            '/travel/',
            '/tech/',
            '/property/',
            '/photo/',
            '/asiafocus/'
        ]

        # 发送请求
        for topic_path in topic_paths:
            yield scrapy.Request(BASEURL + topic_path, self.parse_dictionary,
                                headers = {
                                    'User-Agent':random.choice(user_agent_list)
                                    },
                                meta={
                                'topicPath':topic_path
            }, dont_filter=False)


    def parse_dictionary(self, response):
        # 基础网址
        BASEURL = 'https://www.bangkokpost.com'
        # 话题路径
        topicPath = response.meta['topicPath']
        midPath = '/list_content'


        # 解析动态请求的页面
        #为空说明 网页无内容
        if response.xpath('//div').extract():
            pageNumber = 1
            if re.search(r"page",str(response.url)):
                article_urls = response.xpath('//div[@class="listnews-text"]/h3/a/@href').extract()

                for article_url in article_urls:
                    yield scrapy.Request(BASEURL+article_url, self.parse_article, 
                                         headers = {
                                            'User-Agent':random.choice(user_agent_list)
                                            },
                                         meta={
                                            'topic':topicPath[1:-1]
                                            },
                                         dont_filter=False)
                pageNumber = response.meta['pageNumber'] + 1

            next_request_url = BASEURL + midPath + topicPath + '?page=' + str(pageNumber)
            href= response.urljoin(next_request_url)
            yield scrapy.Request(
                href,
                self.parse_dictionary,
                headers = {
                                    'User-Agent':random.choice(user_agent_list)
                                    },
                meta={
                    'topicPath': topicPath,
                    'pageNumber':pageNumber,
                },
                dont_filter=False)
    #scrapy crawl media_bangkokpost
    def parse_article(self, response):
        # 调取参数
        item = ArticleItem()
        item['media_name'] = '曼谷邮报'
        item['url'] = response.url

        title = response.xpath('//div[@class="article-headline"]/h2//text()').extract_first()
        if title == None:
            item['title'] = response.xpath('//div[@class="media-headline"]/h2//text()').extract_first()
        else:
            item['title'] = title.strip()


        item['topic'] =response.meta['topic']

        item['author'] = '|'.join(response.xpath('//div[@class="article-info"]/div/div[2]/p/a//text()').extract()).strip().replace('\n','').replace('\t','')
        publish_date = ''.join(response.xpath('//div[@class="article-info"]/div/div[1]//text()').extract())
        publish_date = publish_date.replace(' ','').replace('\n','').replace('\t','')
        if re.match(r"published:",publish_date):
            publish_date = publish_date[10:]
        else:
            publish_date = ''.join(response.xpath('//div[@class="article-info"]/div/div[2]//text()').extract())
            publish_date = publish_date.replace(' ','').replace('\n','').replace('\t','')
            if re.match(r"published:",publish_date):
                publish_date = publish_date[10:]


        #published : 12Jul2021at20:18 
        # 匹配文章的发布时间
        item['publish_date'] =time.strftime("%Y/%m/%d %H:%M", time.strptime(publish_date, "%d%b%Yat%H:%M")) #12Jul2021at20:18
        
        raw_sentences = response.xpath('//div[@class="articl-content"]/p//text()').extract()
        if raw_sentences == None:
            raw_sentences = ['media']
        else:
            raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))

        item['content'] = '\n'.join(raw_sentences).strip()
        return item




