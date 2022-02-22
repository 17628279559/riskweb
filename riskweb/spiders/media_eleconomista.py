"""
经济学家报 爬虫
"""

import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaAftenpostenSpider(scrapy.Spider):
    name = 'media_eleconomista'
    allowed_domains = ['eleconomista.com.mx']

    def start_requests(self):
        BASEURL = "https://www.eleconomista.com.mx"
        start_paths = [
            ['/ajax/get_section.html?viewmore=%2Fajax%2Fget_section.html&page={}&banner=Empresas&section=empresas&position={}',1,0],
            ['/ajax/get_section.html?viewmore=%2Fajax%2Fget_section.html&page={}&banner=Sector+Financiero&section=sectorfinanciero&position={}',1,0],
            ['/ajax/get_section.html?viewmore=%2Fajax%2Fget_section.html&page={}&banner=Internacionales&section=internacionales&position={}',1,0],
            ['/ajax/get_section.html?viewmore=%2Fajax%2Fget_section.html&page={}&banner=Tecnolog%C3%ADa&section=tecnologia&position={}',1,0],
            ['/ajax/get_opinion.html?viewmore=%2Fajax%2Fget_opinion.html&banner=Opini%C3%B3n&page={}',1],
            ['/ajax/rio_portadas_capital_humano.html?viewmore=%2Fajax%2Frio_portadas_capital_humano.html&page={}&section=capital_humano&tag=Capital+Humano',1],
            ['/ajax/rio_revistaimef.html?viewmore=%2Fajax%2Frio_revistaimef.html&page={}&section=',1],
            ['/ajax/get_mercados.html?viewmore=%2Fajax%2Fget_mercados.html&banner=Mercados&section=Mercados&page={}&numaleatorioporquesi=0',1],
            ['/ajax/get_section.html?viewmore=%2Fajax%2Fget_section.html&page={}&banner=Estados&section=estados&position={}',1,0],
            ['/ajax/get_section.html?viewmore=%2Fajax%2Fget_section.html&page={}&banner=Finanzas+Personales&section=finanzaspersonales&position={}',1,0],
            ['/ajax/get_section.html?viewmore=%2Fajax%2Fget_section.html&page={}&banner=Arte+e+Ideas&section=arteseideas&position={}',1,0],
            ['/ajax/get_section.html?viewmore=%2Fajax%2Fget_section.html&page={}&banner=Cartones&section=cartones&position={}',1,0],
            ['/ajax/get_tags.html?viewmore=%2Fajax%2Fget_tags.html&banner=Tag&tag=autos&palabra=&page_a={}&position={}',1,0],
            ['/ajax/get_section.html?viewmore=%2Fajax%2Fget_section.html&page={}&banner=Econom%C3%ADa&section=economia&position={}',1,0],
            ['/ajax/get_section.html?viewmore=%2Fajax%2Fget_section.html&page={}&banner=Pol%C3%ADtica&section=politica&position={}',1,0],
            ['/ajax/rio_olimpiadastokio.html?viewmore=%2Fajax%2Frio_olimpiadastokio.html&page={}&section=&tag=Juegos+Ol%C3%ADmpicos+Tokio+2020',1],
            ['/ajax/get_section.html?viewmore=%2Fajax%2Fget_section.html&page={}&banner=Deportes&section=deportes&position={}',1,0],
            ['/ajax/get_tags.html?viewmore=%2Fajax%2Fget_tags.html&banner=Tag&tag=Laboratorio%2Bde%2BSoluciones&palabra=&page_a={}&position={}',1,0],
            ['/ajax/get_tags.html?viewmore=%2Fajax%2Fget_tags.html&banner=Tag&tag=Coronavirus&palabra=&page_a={}&position={}',1,0]
        ]
        # 发送请求
        for start_path in start_paths:
            if len(start_path) == 2:
                yield scrapy.Request(BASEURL+start_path[0].format(str(start_path[1])), self.parse_dictionary,meta = {'url':start_path[0],'num':1,'x1':0}, dont_filter=True)
            else:
                yield scrapy.Request(BASEURL+start_path[0].format(str(start_path[1]),str(start_path[2])), self.parse_dictionary,meta = {'url':start_path[0],'num':2,'x1':1,'x2':0}, dont_filter=True)


    def parse_dictionary(self, response):
        BASEURL = "https://www.eleconomista.com.mx"
        #文章详情链接

        article_urls = response.xpath('//div[@class="entry-box-overlay"]/a/@href | //article/a/@href').extract()
        if article_urls:
            for article_url in article_urls:
                yield scrapy.Request(BASEURL+article_url, self.parse_article, dont_filter=False)

            if response.meta['num'] == 1:
                x1 = response.meta['x1']+1
                next_url = response.meta['url'].format(str(x1))
                yield scrapy.Request(BASEURL+next_url, self.parse_dictionary,meta = {'url':response.meta['url'],'num':1,'x1':x1}, dont_filter=True)
            else:
                x1 = response.meta['x1']+2
                x2 = response.meta['x2']+1
                next_url = response.meta['url'].format(str(x1),str(x2))
                yield scrapy.Request(BASEURL+next_url, self.parse_dictionary,meta = {'url':response.meta['url'],'num':2,'x1':x1,'x2':x2}, dont_filter=True)

        #scrapy crawl media_eleconomista
    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = response.xpath('//div[@class="title"]/h1/text()').extract_first().replace('\xa0','').strip()
        item['media_name'] = '经济学家报'
        item['url'] = response.url

        
        topic = response.xpath('//div[@class="entry-tags"]/a/text()').extract()
        item['topic'] = '|'.join(topic).strip()

        author = response.xpath('//div[@class="author-data"]/text() | //div[@class="author-data"]/a/text()').extract()
        author = list(filter(lambda i: i.strip(), author))
        author = [i.strip() for i in author]

        if author:
            item['author'] = '|'.join(author)
        else:
           item['author'] =''

        # 匹配文章的发布时间
        publish_date = response.xpath('//div[@class="author-data"]//time/@datetime').extract_first()
        #19/08/2021 13:19
        if publish_date:
            item['publish_date'] = time.strftime("%Y/%m/%d %H:%M", time.strptime(publish_date.strip(), "%d/%m/%Y %H:%M")) #19/08/2021 13:19
        else:
            item['publish_date'] = ""
        
        raw_sentences = response.xpath('//div[@class="entry-body"]//p').xpath('string(.)').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        raw_sentences = [i.strip() for i in raw_sentences]
        item['content'] = '\n'.join(raw_sentences).strip().replace('\xa0','')

        return item


