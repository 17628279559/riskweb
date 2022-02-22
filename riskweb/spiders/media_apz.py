import scrapy
from scrapy.http.request import Request
from riskweb.items import ArticleItem
import logging

logger = logging.getLogger(__name__)
months = ['0','janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre']
class ApzSpider(scrapy.Spider):
    name = 'media_apz'
    allowed_domains = ['aps.dz']
    def start_requests(self):
        yield Request(url = 'https://www.aps.dz/',callback = self.parse_page)
    def parse_page(self, response):#获得所爬取的新闻网站的的每个模块链接
        j = 0#j用于控制爬取网页的分页数
        base_url = 'https://www.aps.dz'
        items = response.xpath('//li[@itemprop="name"]/a/@href').extract()
        for i in range(1,9):
            detail_url = base_url + items[i];
            '''yield{
                'detail_url':detail_url
                }'''
            yield Request(url = detail_url, callback = self.parse_mod,meta = {'page':j},dont_filter=True)
    def parse_mod(self,response):
        base_url = 'https://www.aps.dz'
        #print("Successful")
        items = response.xpath('//h3[@class = "catItemTitle"]/a/@href').extract()#获取要爬取文章的网页链接
        hop = response.xpath('//ul[@class="pagination"]//li/a[@title ="Suivant"]/@href').extract()#找到进入到下一页的连接
        response.meta['page'] = response.meta['page']+1#页数加1
        if response.meta['page'] <= 3 and hop != [] :  #meta中的page参数说明了当前在第几分页
        #可以通过page控制爬取分页的数量
            for item in items:
                detail_url = base_url+item
                '''yield{
                    'detail_url':detail_url
                }'''
                yield Request(url = detail_url,callback = self.parse_article,meta = response.meta,dont_filter=True)
            yield Request(url = base_url+hop[0],callback = self.parse_mod,meta = response.meta,dont_filter=True)
    def parse_article(self,response):
        title = response.xpath('//h2[@class = "itemTitle"]/text()').extract()[0]
        date = response.xpath('//span[@class = "itemDateCreated"]/text()').extract()[1][13:].split()
        month = '0' + str(months.index(date[2])) if months.index(date[2])<10 else str(months.index(date[2]))
        date = date[3]+'/'+ month +'/'+date[1]+ ' '+date[4]+':00'
        tags = response.xpath('//ul[@class ="itemTags"]//li/a/text()').extract()
        raw_sentences = response.xpath('//div[@class = "itemIntroText col-xs-hidden "]/p/strong/text()|//div[@class = "itemFullText"]//p/text()|//div[@class ="itemFullText"]//p//strong/text()').extract()
        
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item = ArticleItem()
        item['content'] = '\n'.join(raw_sentences).strip()
        item['media_name'] = '阿尔及利亚新闻社'
        item['url'] = response.url
        item['author'] = ''
        item['publish_date'] = date
        item['title'] = title
        item['topic'] = tags
        return item