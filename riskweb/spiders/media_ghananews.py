'''
加纳通讯社 爬虫
完成
'''
import scrapy
import logging
import time
from riskweb.items import ArticleItem
import re
logger = logging.getLogger(__name__)

class MediaGhananewsSpider(scrapy.Spider):
    name = 'media_ghananews'
    allowed_domains = ['gna.org.gh']

    def start_requests(self):
        #开始爬取网址
        start_urls = [
            'https://www.gna.org.gh/news/social/',
            'https://www.gna.org.gh/news/social/crime/',
            'https://www.gna.org.gh/news/social/human-interest/',
            'https://www.gna.org.gh/news/business/'
            'https://www.gna.org.gh/news/business/economics',
            'https://www.gna.org.gh/news/education/',
            'https://www.gna.org.gh/news/entertainment/',
            'https://www.gna.org.gh/news/science/',
            'https://www.gna.org.gh/news/science/environment/',
            'https://www.gna.org.gh/news/science/health/',
            'https://www.gna.org.gh/news/features/',
            'https://www.gna.org.gh/news/politics/',
            'https://www.gna.org.gh/news/sports/',
            'https://www.gna.org.gh/news/world/',
            'https://www.gna.org.gh/news/world/africa/',          
        ]
        # 发送请求
        for i in range(0, len(start_urls)):
            yield scrapy.Request(start_urls[i], self.parse_dictionary, dont_filter=True,meta={'topic':start_urls[i].split('/')[-2]})

    def parse_dictionary(self, response):
        # 第一页的结构和其他不一样，所以需要特别处理
        # 文章详情链接
        base_url = 'https://www.gna.org.gh'
        article_urls = response.xpath('//article[@class="_top_story_sng"]/div[@class="_m_content"]/a/@href').extract()
        more_urls = response.xpath('//div[@class="col-md-4"]/article/a/@href').extract()
        if more_urls:
            article_urls += more_urls
        for article_url in article_urls:
            # 有时候在下一行会出现KeyError: 'topic'的错误，还可改进
            tp=response.meta['topic']
            yield scrapy.Request(base_url+article_url, self.parse_article,meta={'topic':tp})

        # 分页链接,如果存在下一页，继续请求
        first_page_button = response.xpath('//div[@class="_view_more_button mb-4"]/a/@href').extract()[0]
        if first_page_button:
            tp=response.meta['topic']
            yield scrapy.Request(base_url+first_page_button, self.parse_dictionary, dont_filter=True,meta={'topic':tp})
        
        next_page_url = response.xpath('//div[@class="paginate"]//a[4]/@href').extract_first()
        if next_page_url:
            tp=response.meta['topic']
            yield scrapy.Request(base_url+next_page_url, self.parse_dictionary, dont_filter=True,meta={'topic':tp})

    def parse_article(self, response):
        # 调取参数
        item = ArticleItem()
        # 进入每篇文章获取标题
        item['title'] = response.xpath('//h1[@class="_open_article_title"]/text()').extract_first().replace(r'\xa0','')
        item['media_name'] = '加纳通讯社'
        item['url'] = response.url
        # 文章时间
        publish_date = response.xpath('//span[@class="_article_date_posted"]/text()').extract()[0]
        publish_date_pattern = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
        publish_date = re.findall(publish_date_pattern, publish_date)[0].replace('-','/')
        item['publish_date'] = publish_date
        # 文章话题
        item['topic'] = response.meta['topic']
        # 文章作者
        author = response.xpath('//span[@class="_article_by"]/a/text()').extract()
        if author:
            item['author'] = author[0].replace('By ','')
        else:
            item['author'] = ''
        # 文章内容
        raw_sentences = response.xpath('//div[@class="_article_body_wrap"]//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = ''.join(raw_sentences).replace('\xa0','').strip().replace('\n','').replace('\r','')
        
        return item