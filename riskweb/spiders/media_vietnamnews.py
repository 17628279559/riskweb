"""
越南新闻简报社 爬虫
"""

import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaAftenpostenSpider(scrapy.Spider):
    name = 'media_vietnamnews'
    allowed_domains = ['vietnamnews.vn']

    def start_requests(self):
        BASEURL = "https://vietnamnews.vn"
        start_paths = [
            '/politics-laws',
            '/society',
            '/economy',
            '/life-style',
            '/sports',
            '/environment' 
        ]
        # 发送请求
        for start_path in start_paths:
            yield scrapy.Request(BASEURL+start_path, self.parse_dictionary,meta={'topic': start_path,'p':1}, dont_filter=False)

    def parse_dictionary(self, response):
        if response.xpath('//div[@class="vnnews-bot-list-news"]').extract() != []:
            BASEURL = "https://vietnamnews.vn"
            #文章详情链接

            urls = response.xpath('//div[@class="vnnews-list-news"]/ul/li/a/@href').extract()
            if not re.search(r'p=',response.url): #突出强调的新闻,每一页的强调新闻都一样，共5条
                url1 = response.xpath('//div[@class="vnnews-big-list-news"]/a/@href').extract()
                url2 = response.xpath('//div[@class="vnnews-col-mini-cate"]/ul/li/a/@href').extract()
                urls.extend(url1)
                urls.extend(url2)

            for article_url in urls:
                yield scrapy.Request(BASEURL+article_url, self.parse_article,meta={'topic': response.meta["topic"]}, dont_filter=False)



            yield scrapy.Request(BASEURL+response.meta['topic']+'?p='+str(response.meta['p']+1), self.parse_dictionary,meta={'topic': response.meta["topic"],'p':response.meta['p']+1}, dont_filter=False)

        #scrapy crawl media_vietnamnews
    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题  /xa0
        item['title'] = ''.join(response.xpath('//div[@class = "vnnews-ct-post"]/h3/text()').extract()).strip().replace('\xa0',' ')
        item['media_name'] = '越南新闻简报社'
        item['url'] = response.url
        item['topic'] = response.meta["topic"][1:]
        item['author'] = "无"
        publish_date = response.xpath('//div[@class="vnnews-time-post"]/span/text()').extract_first().strip()

        # 匹配文章的发布时间  July, 20/2021 - 08:25
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M", time.strptime(publish_date, "%B, %d/%Y - %H:%M")) #July, 20/2021 - 08:25
        
        raw_sentences = response.xpath('//div[@class="vnnews-text-post"]/p//text()').extract()
        for i in range(len(raw_sentences)):
            raw_sentences[i] = raw_sentences[i].strip().replace('\xa0',' ')

        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip()
        return item
