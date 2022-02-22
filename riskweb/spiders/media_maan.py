import scrapy
from scrapy.http.request import Request
from riskweb.items import ArticleItem
import logging

logger = logging.getLogger(__name__)
#静态分页结构与media_apz结构类似
class MaanSpider(scrapy.Spider):
    name = 'media_maan'
    allowed_domains = ['maannews.net']

    def start_requests(self):
        yield Request(url = 'https://www.maannews.net/',callback = self.parse_page)
    def parse_page(self, response):
        j = 0
        items = response.xpath('//div[@class="main-menu"]/ul/li/a/@href').extract()#获取网站的各个子模块
        del(items[11])
        del(items[8])
        del(items[0])
        for i in range(1,9):
            detail_url = items[i];
            '''yield{
                'detail_url':detail_url
                }'''
            yield Request(url = detail_url, callback = self.parse_mod,meta = {'page':j},dont_filter=True)
    def parse_mod(self,response):
        #print("Successful")
        base_url = 'https://www.maannews.net'
        items = response.xpath('//div[@class="column is-4"]//a/@href').extract()#获取新闻链接
        hop = response.xpath('//ul[@class="pagination"]//li[last()-1]/a/@href').extract()#获取下一页的链接
        response.meta['page'] = response.meta['page']+1
        if response.meta['page'] <= 3 and hop != ['https://www.maannews.net/#'] :  #meta中的page参数说明了当前在第几分页
        #可以通过page控制爬取分页的数量
            for item in items:
                detail_url = item
                '''yield{
                    'detail_url':detail_url
                }'''
                yield Request(url = detail_url,callback = self.parse_article,meta = response.meta,dont_filter=True)
            yield Request(url = base_url+hop[0],callback = self.parse_mod,meta = response.meta,dont_filter=True)
    def parse_article(self,response):
        title = response.xpath('//h1/text()').extract()[0]
        date = response.xpath('//div[@class="default__item--date"]/text()').extract()[0][45:55]
        date = date[-4:] + '/'+date[-7:-5]+'/'+date[:2]
        time = response.xpath('//div[@class="default__item--date"]/text()').extract()[0].strip()[-7:-2]+':00'
        date = date + ' ' + time
        raw_sentences = response.xpath('//div[@class="default__item--content default__item--default-content"]//p/text()').extract()[:-1]
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item = ArticleItem()
        item['content'] = '\n'.join(raw_sentences).strip()
        item['media_name'] = '马安通讯社'
        item['url'] = response.url
        item['author'] = ''
        item['publish_date'] = date
        
        item['title'] = title
        item['topic'] = ''
        return item
