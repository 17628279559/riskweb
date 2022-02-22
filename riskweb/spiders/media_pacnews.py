"""
太平洋新闻社 爬虫
"""
import scrapy
import logging
import time
from riskweb.items import ArticleItem
import re
import requests
logger = logging.getLogger(__name__)

class MediaPacnewsSpider(scrapy.Spider):
    name = 'media_pacnews'
    allowed_domains = ['pina.com.fj']
    start_urls = ['http://pina.com.fj/']

    def start_requests(self):
        # 开始爬取网址
        start_urls = [
            'https://pina.com.fj/category/news/',
            'https://pina.com.fj/category/news/election/',
            'https://pina.com.fj/category/news/parliament/',
            'https://pina.com.fj/category/news/politics-news/',
            'https://pina.com.fj/category/news/politics-news/anti-corruption/',
            'https://pina.com.fj/category/breaking-news/',                      
            'https://pina.com.fj/category/environment/',
            'https://pina.com.fj/category/health/',
            'https://pina.com.fj/category/featured/',
            'https://pina.com.fj/category/environment/',
        ]
        special_urls = [
            'https://pina.com.fj/category/business/',
            'https://pina.com.fj/category/sport/',
        ]
        # 发送请求
        for i in range(0, len(start_urls)):
            yield scrapy.Request(start_urls[i], self.parse_dictionary, dont_filter=True)
        for j in range(0, len(special_urls)):
            yield scrapy.Request(special_urls[j], self.parse_special_dictionary, dont_filter=True)    


    def parse_dictionary(self, response):
        # 文章详情链接
        article_urls = response.xpath('//div[@class="td-ss-main-content"]//h3/a/@href').extract()
        for article_url in article_urls:
            yield scrapy.Request(article_url, self.parse_article)

        # 分页链接
        next_page_url = response.xpath('//div[@class="page-nav td-pb-padding-side"]/a/@href').extract()[-1]
        # 如果存在下一页,说明是普通的静态网页结构，继续请求
        if next_page_url:
            yield scrapy.Request(next_page_url, self.parse_dictionary, dont_filter=True)

    def parse_special_dictionary(self, response):
        # 文章详情链接（第一页是通过get方式获取到的）
        article_urls = response.xpath('//div[@class="td-ss-main-content"]//h3/a/@href').extract()
        for article_url in article_urls:
            yield scrapy.Request(article_url, self.parse_article)

        # 接下来需要的请求头
        headers={
            'accept':'*/*',
            'accept-encoding':'gzip, deflate, br',
            'accept-language':'zh-CN,zh;q=0.9,en-CN;q=0.8,en-US;q=0.7,en;q=0.6',
            'cache-control':'no-cache',
            'content-length':'298',
            'content-type':'application/x-www-form-urlencoded; charset=UTF-8',
            'origin':'https://pina.com.fj',
            'pragma':'no-cache',
            'referer':response.url,
            'sec-ch-ua':'" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
            'sec-ch-ua-mobile':'?0',
            'sec-fetch-dest':'empty',
            'sec-fetch-mode':'cors',
            'sec-fetch-site':'same-origin',
            'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
            'x-requested-with':'XMLHttpRequest',
        }
            
        max_num_pages=8
        request_api='https://pina.com.fj/wp-admin/admin-ajax.php?td_theme_name=Newspaper&v=10.4'
        for currentPage in range(2,max_num_pages+1):
            # 要向后台api发送的数据
            params = {
            'action': 'td_ajax_loop',
            'loopState[sidebarPosition]':'',
            'loopState[moduleId]':10,
            'loopState[currentPage]': currentPage,
            'loopState[max_num_pages]': 8,
            'loopState[atts][category_id]': 13,
            'loopState[atts][offset]': 4,
            'loopState[ajax_pagination_infinite_stop]': 3,
            'loopState[server_reply_html_data]':''
            }
            # 使用post向后台发送数据
            yield scrapy.Request(request_api, method='POST',headers=headers,callback=self.parse_special_articles,body=params,encoding='utf-8')
        
    def parse_special_articles(self,response):
        article_url_pattern = re.compile(r'<a href=\"(https://pina.com.fj/\d{4}/\d{2}/\d{2}/.+?/)')
        article_urls=re.findall(article_url_pattern, response.body.decode(response.encoding))
        article_urls=list(set(article_urls))
        for article_url in article_urls:
            yield scrapy.Request(article_url, self.parse_article)

    def parse_article(self, response):
        # 调取参数
        item = ArticleItem()

        item['title'] = response.xpath('//header[@class="td-post-title"]/h1/text()').extract_first() 
        item['media_name'] = '太平洋新闻社'
        item['url'] = response.url
        # 出现多个标签的情况
        topics = response.xpath('//ul[@class="td-tags td-post-small-box clearfix"]/li//a/text()').extract() 
        if not topics:
            topics = response.xpath('//ul[@class="td-category"]/li//a/text()').extract()             
        item['topic'] = ','.join(topics).replace('\t', '').replace('\n', '').strip()
        
        item['author'] = response.xpath('//div[@class="td-post-author-name"]/a/text()').extract()[0]
        #文章发布时间
        publish_date = response.xpath('//span[@class="td-post-date"]/time/@datetime').extract_first()
        # '2021-06-30T16:30:38+12:00'
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S",time.strptime(publish_date,'%Y-%m-%dT%H:%M:%S+12:00'))
        # 提取文章内容
        raw_sentences = response.xpath('//div[@class="td-post-content tagdiv-type"]/p/text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).replace(r'\xa0', '')

        return item

