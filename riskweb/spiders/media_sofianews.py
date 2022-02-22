'''
索菲亚新闻社 爬虫
完成
'''
import scrapy
import logging
import time
from riskweb.items import ArticleItem
import re
logger = logging.getLogger(__name__)

class MediaSofianewsSpider(scrapy.Spider):
    name = 'media_sofianews'
    allowed_domains = ['novinite.com']
     
    def start_requests(self):
        start_url = 'https://www.novinite.com/articles/category/'
        category = 157    #总类别数
        # 开始爬取网址
        start_urls = [ start_url + str(x) for x in range(1,category+1) ]
        # 发送请求
        for i in range(0, len(start_urls)):
            yield scrapy.Request(start_urls[i], self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):
        # 文章详情链接
        base_url = 'https://www.novinite.com/'
        article_urls = response.xpath("//div[@class='item']/a/@href").extract()

        for article_url in article_urls:
            yield scrapy.Request(base_url+article_url, self.parse_article)

        # 分页链接
        next_page_url = response.xpath('//li[@class="btn next"]/a/@href').extract_first()
        # 如果存在下一页，继续请求
        if next_page_url:
            yield scrapy.Request(base_url + next_page_url, self.parse_dictionary, dont_filter=True)

    def parse_article(self, response):
        # 调取参数
        item = ArticleItem()
        # 进入每篇文章获取相关信息
        item['title'] = response.xpath('//div[@id="content"]/h1/text()').extract_first()
        item['media_name'] = '索菲亚新闻社'
        item['url'] = response.url
        # 文章作者都是'Novinite.com (Sofia News Agency)'
        item['author'] = 'Novinite.com (Sofia News Agency)'
        # 清洗标签内容
        topics = response.xpath('//div[@id="article_tags"]/a/text()').extract()
        item['topic'] = ''.join(topics).strip()
        # 清洗文章内容
        raw_sentences = response.xpath('//div[@class="article__text text text--bigger"]/p').xpath('string(.)').extract()
        if raw_sentences:
            item['content'] = ''.join(raw_sentences).replace('\xa0', ' ').strip()
        else:
            raw_sentences = response.xpath('//div[@id="textsize"]/p//text()').extract() 
            raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
            item['content'] = ''.join(raw_sentences).replace('\xa0', ' ')
        # 转换时间格式
        publish_date = response.xpath('//div[@class="date"]/text()').extract()[-1]
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date, " %B %d, %Y, %A // %H:%M"))
        # 使用datetime库的时候是这样用的，注意：使用time库的时候不能将变量命名为time
        # struct_time=datetime.datetime.strptime(time," %B %d, %Y, %A // %H:%M")
        # item['publish_date'] = struct_time.strftime("%Y/%m/%d %H:%M:%S")
        return item

    
