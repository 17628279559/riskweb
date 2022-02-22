import scrapy
import datetime
from riskweb.items import ArticleItem
import logging
import time
import re
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains  # 引入 ActionChains 类


logger = logging.getLogger(__name__)
class MediaTheWestSpider(scrapy.Spider):
    name = 'media_thewest'  # name of spider
    allowed_domains = ['thewest.com']



    def start_requests(self):  # def parse
        BASEURL = 'https://thewest.com.au'

        topic_paths = [
            '/latest',
            '/news/wa',
            '/news/coronavirus',
            '/business/mining',
            '/business/markets',
            '/business/commercial-property',
            '/business/energy',
            '/business/personal-finance',
            '/business/agriculture',
            '/business/public-companies',
            '/business/west-business-events',
            '/sport/west-coast-eagles',
            '/sport/fremantle-dockers',
            '/sport/wafl',
            '/sport/psa-footy',
            '/opinion/lanai-scarr',
            '/opinion/rangi-hirini',
            '/opinion/kate-emery',
            '/opinion/paul-murray',
            '/opinion/gemma-tognini',
            '/opinion/jenna-clarke',
            '/opinion/peter-law',
            '/opinion/basil-zempilas',
            '/opinion/basil-zempilas',
            '/opinion/mark-riley',
            '/opinion/dean-alston',
            '/politics/federal-politics',
            '/politics/state-politics',
            '/politics/local-government',
            '/news/claremont-serial-killings',
            '/features/gerard-ross',
            '/features/jody-gore',
            '/sport/bush-and-burbs',
            '/news/flashpoint',
            '/features/red-tape-war',
            '/features/shalom-house',
            '/features/footys-most-powerful'

        ]
        # request函数的参数表,yield用来遍历网址表或者通过BASEURL解析得到的类似TOPICS的集合
        # dont_fliter 为真:强制下载。为假:多次提交请求之后后面的请求会被过滤
        # callback为函数名，在parse函数里通常为parse_dictionary，一直传递到parse_article
        for topic_path in topic_paths:
            yield scrapy.Request(BASEURL + topic_path, self.parse_dictionary, meta={
                'topicPath': topic_path
            }, dont_filter=False)


    #parse_dictionary用来迭代页面中文章详情的链接
    #如果能在parse函数内直接迭代文章内容，则省略该函数
    def parse_dictionary(self, response):
        browser = webdriver.Chrome()
        browser.get(response.url)
        # 不存在下一页的总体格式
        # 基础网址
        BASEURL = 'https://www.thewest.com.au'
        topicPath = response.meta['topicPath']
        #从对应的xpath获取文章详情链接的集合article_urls
        while():
            right_click = browser.find_element_by_xpath(
                '//button[@class ="gtm-load-more-button css-1rvdi14-StyledButton ek8wdbw0"]')
            try :
                ActionChains(browser).context_click(right_click).perform()
            except Exception as e:
                break
        article_urls = response.xpath('//*[@id="root"]/div/div/div[1]/div[4]/div[2]/div[2]/div/div//div//a/@href').extract()
        #迭代链接进行request，此时callback为parse_article
        for article_url in article_urls:
            yield scrapy.Request(BASEURL+article_url, self.parse_article,meta={'topicPath':topicPath},dont_filter=True)

        #parse_article 进入文章页面获取信息的函数
    def parse_article(self,response):
        #调取参数
        item = ArticleItem()
        #response.xpath获取标题,媒体名，网址，主题
        item['title'] = response.xpath('//h1[@itemprop="headline"]/text()').extract_first()
        item['media_name'] = '西澳大利亚人报'
        item['url'] = response.url
        item['topic'] = response.meta['topicPath']
        raw_sentences = response.xpath('//div[@id="ArticleContent"]//p//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).replace(r'\xa0', '')
        item['author'] = response.xpath('//span[@itemprop="author name"]').extract_first()
        #匹配文章的发布时间参照具体格式
        update_time = response.xpath('//time/@datetime').extract_first()
        times = []
        for i in update_time:
            if i is not 'T':
                times.append(i)
            if i == '+':
                del times[16]
                break
        times.insert(10, ' ')
        new_time = ''.join(times)
        print(new_time)
        new_time.strip()
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M",
                                             time.strptime(new_time, "%Y-%m-%d %H:%M"))

        #返回item
        return item
