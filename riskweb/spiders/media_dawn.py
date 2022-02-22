import scrapy
import datetime
from scrapy.http.request import Request
import time
from riskweb.items import ArticleItem
import logging

months = ['0','January','February','March',' April','May',' June','July','August',' September','October','November','December']

logger = logging.getLogger(__name__)
class DawnSpider(scrapy.Spider):
    name = 'media_dawn'
    allowed_domains = ['dawn.com']
    def start_requests(self):
        date = datetime.date(2021,7,16)
        #网站按时间分页，规定起始时间，然后时间上递减爬取最近的新闻，递减单位为天 
        datedelta = datetime.timedelta(days = 1)
        for i in range(5):
            yield Request(url = 'https://www.dawn.com/newspaper/' + date.isoformat(),callback = self.parse_page)
            date = date - datedelta
            time.sleep(1)
    def parse_page(self, response):
        items = response.xpath("//a[@class = 'p-1']/@href|//a[@class = 'w-full']/@href").extract()#获取每个页面的各个子版块
        del(items[-1])
        del(items[13:19])
        base_url = 'https://www.dawn.com'
        for item in items:
            yield Request(url = base_url + item,callback = self.parse_index)
            time.sleep(1)
    def parse_index(self,response):
        items = response.xpath("//h2[@data-layout = 'story']/a/@href").extract()#获取新闻链接
        if items != []:
            for item in items:
                yield Request(url = item,callback = self.parse_article)
                time.sleep(1)
    def parse_article(self,response):
        title = response.xpath("//h2[@data-layout='story']/a/text()").extract()[0]
        editor = response.xpath("//span[@dir='auto']/a[@class='story__byline__link']/text()").extract()[0]
        time = response.xpath("//span[@class = 'timestamp--date']/text()").extract()[0].split()
        
        month = '0' + str(months.index(time[0])) if months.index(time[0])<10 else str(months.index(time[0]))
        time = time[2]+'/'+month +'/'+ time[1][:-1] +' 00:00:00'
        raw_sentences = response.xpath("//div[@dir='auto']//p/text()").extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item = ArticleItem()
        item['content'] = '\n'.join(raw_sentences).strip()
        item['media_name'] = '巴基斯坦黎明报'
        item['url'] = response.url
        item['author'] = editor
        item['publish_date'] = time
        
        item['title'] = title
        item['topic'] = ''
        return item