import scrapy
from scrapy.http.request import Request
from scrapy.http import HtmlResponse
import scrapy
from scrapy import Request
import json
import logging
import time
import re
import datetime
from selenium import webdriver
from riskweb.items import ArticleItem

logger = logging.getLogger(__name__)
months = ['0','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
class BnaSpider(scrapy.Spider):
    name = 'media_bna'
    allowed_domains = ['bna.bh']

    def start_requests(self):
        CategoryId = [153,21812,155,181,177,179,176,180]
        limit_page = [182,28,6,69,45,5,33,4]# 每个板块新闻的最多页数
        base_url = 'https://www.bna.bh/en/bnaWebService.aspx/fnGetNews'
        header= {'content-type': 'application/json'} #是以payload形式存在的post连接请求，需要对首部作出一些要求
        for i in range(len(CategoryId)): 
            data = {'RowNumber':'0','CategoryId':str(CategoryId[i]),'NewsKeyword':'','NewsStartDate':'','NewsEndDate':'','pageIndex':1,'pagesize':12}
            while data['pageIndex'] <= 3 and data['pageIndex'] <= limit_page[i]:
                yield Request(url = base_url,method ='POST',body = json.dumps(data),headers = header,callback = self.parse_page)
                time.sleep(1) 
                data['pageIndex'] = data['pageIndex'] + 1#通过post请求中的字典控制分页数
    def parse_page(self, response):
        base_url = 'https://www.bna.bh/en/'
        resp = json.loads(response.text)#将获得的json数据转化为HTMLresponse对象
        temp = HtmlResponse(url = 'https://www.bna.bh/en/bnaWebService.aspx/fnGetNews',encoding = 'utf-8',body = resp['d'][0])
        items = temp.xpath("//h2//a/@href").extract()#获取新闻文章链接
        for item in items:
            yield Request(url = base_url+item,callback = self.parse_article)
            time.sleep(1)
    def parse_article(self,response):
        date = response.xpath('//dd[@class="createdby"]/text()|//dd[@class="category-name"][last()]/text()').extract()
        big = date[1].strip().split()
        small = date[3].strip().split()
        month = '0' + str(months.index(big[1])) if months.index(big[1])<10 else str(months.index(big[1]))
        date = big[2]+'/'+month+'/'+big[0]+' '+small[2]+':00'
        title = response.xpath('//h1[@class="h2 title"]/text()').extract()[0]
        raw_sentences = response.xpath('//section//p/text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item = ArticleItem()
        item['content'] = '\n'.join(raw_sentences).strip()
        item['media_name'] = '巴林新闻社'
        item['url'] = response.url
        item['author'] = ''
        item['publish_date'] = date
        item['title'] = title
        item['topic'] = ''
        return item
        
            
