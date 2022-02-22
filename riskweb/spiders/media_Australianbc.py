"""
澳大利亚广播公司 爬虫
"""

import scrapy
import time
import logging
import re
import json
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaAftenpostenSpider(scrapy.Spider):
    name = 'media_Australianbc'
    allowed_domains = ['abc.net.au']
    #网页话题太多，采用4层结构
    #start_requests    和   parse_catalogue  用于定位每个话题的id ，约5000多个话题，新闻总数估计有几百万

    def start_requests(self):
        BASEURLS=["https://www.abc.net.au/news/topics/",
                "https://www.abc.net.au/news/topics/subject/",
                "https://www.abc.net.au/news/topics/location/"]
        catalogues = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        # 发送请求
        for BASEURL in BASEURLS:
            for catalogue in catalogues:
                yield scrapy.Request(BASEURL+catalogue, self.parse_catalogue, dont_filter=True)
    
    #此函数进入每个目录页，获取话题的id
    def parse_catalogue(self, response):
        #网站为异步加载，点击加载更多，会get一个json文件
        #链接格式为   ...&offset=10&size=20&total=250   包含10条新闻，偏移为10
        #尝试更改为   ...&offset=0&size=250&total=250之后  发现json文件显示了250条新闻内容，但将total和size数值改的更大就没有更多的新闻
        #测试发现     size最大为1000 ,一次获取太多会很慢，决定一次获取200条 
        #通过构造 xhr 请求链接 获取每个板块能获得的所有新闻的json数据
        #total对获取的数量无影响  
        BASEURL = "https://www.abc.net.au/news-web/api/loader/topicstories?name=PaginationArticles&documentId={0[0]}&prepareParams=%7B%22timestampFormat%22:%22relativeLong%22,%22imagePosition%22:%7B%22mobile%22:%22right%22,%22tablet%22:%22right%22,%22desktop%22:%22right%22%7D%7D&offset={0[1]}&size={0[2]}&total=99999"
        ids = response.xpath('//ul[@class="Udcbj"]/li/@data-uri').extract()
        for id in ids:
            url = BASEURL.format([id,'0','200'])
            yield scrapy.Request(url, self.parse_dictionary,meta={'id':id,'start':0,'end':200}, dont_filter=True)
     

    #scrapy crawl media_Australianbc
    def parse_dictionary(self, response):
        B = "https://www.abc.net.au/news-web/api/loader/topicstories?name=PaginationArticles&documentId={0[0]}&prepareParams=%7B%22timestampFormat%22:%22relativeLong%22,%22imagePosition%22:%7B%22mobile%22:%22right%22,%22tablet%22:%22right%22,%22desktop%22:%22right%22%7D%7D&offset={0[1]}&size={0[2]}&total=99999"
        rs = json.loads(response.text)
        id = response.meta['id']
        start = response.meta['start']
        end = response.meta['end']
        BASEURL = "https://www.abc.net.au"

        article_urls = []
        for i in rs['collection']:
            article_urls.append(i['link']['to'])

        for article_url in article_urls:
            yield scrapy.Request(BASEURL+article_url, self.parse_article, dont_filter=False)
        
        if len(article_urls) == 200:
            url = B.format([id,str(start+200),str(end+200)])
            yield scrapy.Request(url, self.parse_dictionary,meta={'id':id,'start':start+200,'end':end+200}, dont_filter=True)

    def parse_article(self, response):
        #调取参数
        if not response.xpath('//div[@class="_2OCMV"]'):  #含有这个说明新闻下架了，不让看
            item = ArticleItem()
            item['media_name'] = '澳大利亚广播公司'
            item['url'] = response.url
            item['topic'] = '|'.join(response.xpath('//ul[@class="_3G3E6"]/li/a/text()').extract())
            #进入每篇文章获取标题

            item['title'] = ''.join(response.xpath('//div[@class="_3ANn5"]/h1/text() | //div[@class="article section"]/h1/text() | //header[@class="_3sI2v"]/h1/text()').extract())
            
            author = response.xpath('//div[@class="_3ANn5"]//a[contains(@data-component,"Link")]/text()').extract()

            if author:
                for i in author:
                    if re.search(r'ABC',i):
                        author.remove(i)
                item['author'] = '|'.join(author).strip()
            else:
                item['author'] = ''

            publish_date = response.xpath('//div[@class="_3ANn5"]/div[@data-component="PublishedDate"]/time/@datetime').extract()
            if publish_date:
                # 匹配文章的发布时间
                item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date[-1].split('.')[0], "%Y-%m-%dT%H:%M:%S")) #2021-07-28T13:31:41.000Z
            else:
                publish_date = response.xpath('//span[@class="timestamp"]/time/@datetime').extract() 
                if publish_date:
                    item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(' '.join(publish_date[0].split(' ')[1:-2])[0], "%b %d %Y %H:%M:%S")) #Nov 30 2020 21:23:52


            raw_sentences = response.xpath('//div[@class="ZN39J"]/div/p | //div[@class="ZN39J"]/div/h2').xpath('string(.)').extract()
            if not raw_sentences:
                raw_sentences = response.xpath('//div[@class="article section"]/p').xpath('string(.)').extract()
            for i in range(len(raw_sentences)):
                raw_sentences[i]=raw_sentences[i].strip()
            raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
            item['content'] = '\n'.join(raw_sentences).strip().replace('/xa0','')
            if not item['content']:
                item['content'] = "这是一条音频或视频新闻"
            return item