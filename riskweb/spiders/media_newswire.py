"""
韩国新闻社 爬虫
"""

import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaAftenpostenSpider(scrapy.Spider):
    name = 'media_newswire'
    allowed_domains = ['newswire.co.kr']
    def start_requests(self):
        #此页为全部新闻 共计35874页 约90万则新闻
        BASEURL = "https://www.newswire.co.kr/?md=A00"  
        # 发送请求
        yield scrapy.Request(BASEURL, self.parse_dictionary, dont_filter=False)

    def parse_dictionary(self, response):

        #文章详情链接 此网页每次获取25条
        article_urls = response.xpath('//section[@class="news-list"]/div/div[@class="news"]/h5/a/@href').extract()

        for article_url in article_urls:
            yield scrapy.Request(article_url, self.parse_article, dont_filter=False)

        next_page_path = response.xpath('//ul[@class="pagination"]/li[last()]/a/@href').extract_first()
        # 增加参数中的start值
        if next_page_path is not None:
            yield scrapy.Request(next_page_path, self.parse_dictionary, dont_filter=False)


    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = '|'.join(response.xpath('//div[@class="news-release"]/section/h1//text()').extract())
        item['media_name'] = '韩国新闻社'
        item['url'] = response.url
        item['topic'] ="|".join(response.xpath('//section[@class="related-fields-news"]/ul/li/a//text()').extract())
        author = response.xpath('//div[@class="meta"]/a//text()').extract()
       

        item['author'] = '|'.join(author).strip()

        publish_date = response.xpath('//div[@class="release-time"]//text()').extract_first()

        # 匹配文章的发布时间
        if re.search( r'-', publish_date):
            item['publish_date'] = time.strftime("%Y/%m/%d %H:%M", time.strptime(publish_date, "%Y-%m-%d %H:%M")) #2021-07-09 09:39
        else:
            item['publish_date'] = time.strftime("%Y/%m/%d %H:%M", time.strptime(publish_date, "%B %d, %Y %H:%M")) #July 09, 2021 15:30
        
        raw_sentences = response.xpath('//section[@class="release-story"]/p[1]//text()').extract()

        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))

        #Html格式：
        #<trans>首尔--(</trans>
        #<a><trans>新闻连线</trans></a>
        #<trans> ){第一段剩下的内容}</trans>   
        if re.match(r"\)",raw_sentences[2]):
            raw_sentences[0] = raw_sentences[0] +raw_sentences[1] +raw_sentences[2]
            raw_sentences.pop(1)
            raw_sentences.pop(2)

        item['content'] = '\n'.join(raw_sentences).strip()
        return item





