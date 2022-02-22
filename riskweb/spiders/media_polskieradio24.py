"""
波兰广播电台 爬虫
"""

import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaAftenpostenSpider(scrapy.Spider):
    name = 'media_polskieradio24'
    allowed_domains = ['polskieradio24.pl']
    start_urls = ["https://polskieradio24.pl/321/6722"]

    #此新闻网站的新闻,作者都在文章内容结尾部分

    def parse(self, response, **kwargs): # 从主页找到所有的话题路径
        # 基础网址
        BASEURL = "https://polskieradio24.pl"
        topic_paths = response.xpath('//ul[@class="pr24-submenu"]/li/a/@href').extract()[0:53] #普通新闻
        topic_paths.extend(response.xpath('//article[@class="article"]/a[1]/@href').extract()) #广播新闻
        topic_paths.append('/321/7090')
        for topic_path in topic_paths:
            yield scrapy.Request(BASEURL + topic_path, self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):
        BASEURL = "https://polskieradio24.pl"
        #文章详情链接

        article_urls = response.xpath('//article/a/@href').extract()
        rem = response.xpath('//div[@class="articles-box recommended-box"]//article/a/@href').extract()
        for i in rem:
            article_urls.remove(i)


        for article_url in article_urls:
            if re.search(r'http',article_url):
                yield scrapy.Request(article_url, self.parse_article, dont_filter=False)
            else:
                yield scrapy.Request(BASEURL+article_url, self.parse_article, dont_filter=False)

        next_url = response.xpath('//div[@class="next"]/a/@href').extract_first()
        if next_url:
            yield scrapy.Request(BASEURL+next_url, self.parse_dictionary, dont_filter=True)

        #scrapy crawl media_polskieradio24
    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = response.xpath('//*[@class="art-body"]//h1//text()').extract_first().replace('\xa0','').strip()
        item['media_name'] = '波兰广播电台'
        item['url'] = response.url

        
        topic = response.xpath('//div[@class="art-body"]//div[@class="tags"]/span/a/text()').extract()
        for i in range(len(topic)):
            topic[i] = topic[i].strip()
        item['topic'] = '|'.join(topic)
        #普通新闻大多数没有作者，广播新闻都有
        author = response.xpath('//div[@class="art-body"]//strong[contains(text(),"Prowa")]/following-sibling::*[@href]').extract()
        if author:
            item['author'] = '|'.join(author).strip()
        else:
           item['author'] =''

        # 匹配文章的发布时间
        publish_date = response.xpath('//div[@class="art-body"]//div[@class="article-time"]/span[last()]/text()').extract_first()
        #13.08.2021 09:50
        if publish_date:
            publish_date = publish_date.strip()
            item['publish_date'] = time.strftime("%Y/%m/%d %H:%M", time.strptime(publish_date, "%d.%m.%Y %H:%M")) #13.08.2021 09:50
        else:
            item['publish_date'] = ""

        raw_sentences = response.xpath('//div[@class="art-body"]//div[@class="content"]//p').xpath('string(.)').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip().replace('\xa0','')

        return item


