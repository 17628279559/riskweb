"""
意大利安莎社 爬虫
"""
import scrapy
import time
import logging
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MeidaAnsaSpider(scrapy.Spider):
    name = 'media_ansa'
    allowed_domains = ['ansa.it']
    start_urls = ['http://ansa.it/']

    def start_requests(self):
        #开始爬取网址
        start_urls = [
            'https://www.ansa.it/sito/notizie/topnews/index.shtml',
            'https://www.ansa.it/sito/notizie/cronaca/index.shtml',
            'https://www.ansa.it/sito/notizie/politica/index.shtml',
            'https://www.ansa.it/sito/notizie/economia/index.shtml',
            'https://www.ansa.it/professioni/notizie/tutte_le_news.shtml',
            'https://www.ansa.it/sito/notizie/magazine/numeri/magazine.shtml',
            'https://www.ansa.it/industry_4_0/notizie/news/index.shtml',
            'https://www.ansa.it/canale_ambiente/?refresh_ce',

            # 运动
            'https://www.ansa.it/sito/notizie/sport/index.shtml',
            'https://www.ansa.it/sito/notizie/sport/calcio/calcio.shtml',
            'https://www.ansa.it/sito/notizie/sport/f1/f1.shtml',
            'https://www.ansa.it/sito/notizie/sport/moto/moto.shtml',
            'https://www.ansa.it/golf/',
            'https://www.ansa.it/sito/notizie/sport/basket/basket.shtml',
            'https://www.ansa.it/sito/notizie/sport/tennis/tennis.shtml',
            'https://www.ansa.it/sito/notizie/sport/nuoto/nuoto.shtml',
            'https://www.ansa.it/vela/',
            'https://www.ansa.it/sito/notizie/sport/altrisport/altrisport.shtml',
            'https://www.ansa.it/europei_2020/',
            'https://www.ansa.it/olimpiadi_tokyo_2020/',

            # 技术
            'https://www.ansa.it/sito/notizie/tecnologia/index.shtml',
            'https://www.ansa.it/sito/notizie/tecnologia/hitech/hitech.shtml',
            'https://www.ansa.it/sito/notizie/tecnologia/internet_social/internet_social.shtml',
            'https://www.ansa.it/sito/notizie/tecnologia/tlc/tlc.shtml',
            'https://www.ansa.it/sito/notizie/tecnologia/software_app/software_app.shtml',
            'https://www.ansa.it/osservatorio_intelligenza_artificiale/',
            'https://www.ansa.it/innovazione_5g/',

            # 文化
            'https://www.ansa.it/sito/notizie/cultura/index.shtml',
            'https://www.ansa.it/sito/notizie/cultura/cinema/cinema.shtml',
            'https://www.ansa.it/sito/notizie/cultura/moda/moda.shtml',
            'https://www.ansa.it/sito/notizie/cultura/teatro/teatro.shtml',
            'https://www.ansa.it/sito/notizie/cultura/tv/tv.shtml',
            'https://www.ansa.it/sito/notizie/cultura/musica/musica.shtml',
            'https://www.ansa.it/sito/notizie/cultura/libri/libri.shtml',
            'https://www.ansa.it/sito/notizie/cultura/arte/arte.shtml',
            'https://www.ansa.it/sito/notizie/cultura/unlibroalgiorno/unlibroalgiorno.shtml',
            'https://www.ansa.it/sito/notizie/cultura/unfilmalgiorno/unfilmalgiorno.shtml',
            'https://www.ansa.it/sito/notizie/cultura/cinema/cinema_trovacinema.shtml',
            'https://www.ansa.it/canale_lifestyle/',

            # 世界
            'https://www.ansa.it/sito/notizie/mondo/index.shtml',
            'https://www.ansa.it/sito/notizie/mondo/europa/europa.shtml',
            'https://www.ansa.it/sito/notizie/mondo/nordamerica/nordamerica.shtml',
            'https://www.ansa.it/sito/notizie/mondo/americalatina/americalatina.shtml',
            'https://www.ansa.it/sito/notizie/mondo/africa/africa.shtml',
            'https://www.ansa.it/sito/notizie/mondo/mediooriente/mediooriente.shtml',
            'https://www.ansa.it/sito/notizie/mondo/asia/asia.shtml',
            'https://www.ansa.it/sito/notizie/mondo/oceania/oceania.shtml',
            'https://www.ansa.it/sito/notizie/mondo/dalla_cina/index.shtml',
            'https://www.ansa.it/sito/notizie/mondo/dal_kazakhstan/index.shtml',
            'https://www.ansa.it/sito/sito/notizie/mondo/news_qatar/index.shtml'
            
            # 地区
            'https://www.ansa.it/abruzzo/notizie/index.shtml',
            'https://www.ansa.it/basilicata/notizie/index.shtml',
            'https://www.ansa.it/calabria/notizie/index.shtml',
            'https://www.ansa.it/campania/notizie/index.shtml',
            'https://www.ansa.it/emiliaromagna/notizie/index.shtml',
            'https://www.ansa.it/friuliveneziagiulia/notizie/index.shtml',
            'https://www.ansa.it/lazio/notizie/index.shtml',
            'https://www.ansa.it/liguria/notizie/index.shtml',
            'https://www.ansa.it/lombardia/notizie/index.shtml',
            'https://www.ansa.it/marche/notizie/index.shtml',
            'https://www.ansa.it/molise/notizie/index.shtml',
            'https://www.ansa.it/piemonte/notizie/index.shtml',
            'https://www.ansa.it/puglia/notizie/index.shtml',
            'https://www.ansa.it/sardegna/notizie/index.shtml',
            'https://www.ansa.it/sicilia/notizie/index.shtml',
            'https://www.ansa.it/toscana/notizie/index.shtml',
            'https://www.ansa.it/trentino/notizie/index.shtml',
            'https://www.ansa.it/umbria/notizie/index.shtml',
            'https://www.ansa.it/valledaosta/notizie/index.shtml',
            'https://www.ansa.it/veneto/notizie/index.shtml',
        ]
        # 发送请求
        for i in range(0, len(start_urls)):
            yield scrapy.Request(start_urls[i], self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):
        # 基础网址
        BASEURL = 'https://www.ansa.it'
        # 文章详情链接
        article_urls = response.xpath('//article/header//*[contains(@class,"news-title")]/a/@href').extract()

        for article_url in article_urls:
            yield scrapy.Request(BASEURL + article_url, self.parse_article, dont_filter=False)

        # 分页链接
        next_page_url = response.xpath('//li[@class="pg-next"]/a/@href').extract_first()
        # 如果存在下一页，继续请求
        if next_page_url is not None:
            yield scrapy.Request(BASEURL + next_page_url, self.parse_dictionary, dont_filter=True)

    def parse_article(self, response):
        # 调取参数
        item = ArticleItem()
        # 进入每篇文章获取标题
        item['title'] = response.xpath('//article//header/*[@class="news-title"]/text()').extract_first().replace(r'\xa0','')
        item['media_name'] = '意大利安莎社'
        item['url'] = response.url
        topics = response.xpath('//div[@class="pathway hidden-phone"]/ul/li/a/span/text()').extract()
        item['topic'] = '|'.join(topics)

        item['author'] = response.xpath('//article//*[@class="news-author"]/text()').extract_first()
        publish_date = response.xpath('//article//*[@class="news-time"]/time//text()').extract()
        if len(publish_date) == 0:
            publish_date = response.xpath('//article//*[@class="news-date"]/time//text()').extract()
        publish_date = ' '.join(publish_date).strip()
        month_dic = {
            'gennaio' : 'January',
            'febbraio': 'February',
            'marzo': 'March',
            'aprile': 'April',
            'maggio': 'May',
            'giugno': 'June',
            'luglio': 'July ',
            'agosto': 'August',
            'settembre': 'September',
            'ottobre': 'October',
            'novembre': 'November',
            'dicembre': 'December',
        }
        for key in month_dic.keys():
            if key in publish_date:
                publish_date = publish_date.replace(key,month_dic[key])

        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S",
                                             time.strptime(publish_date, "%d %B %Y %H:%M"))  # 21 January 2021 11:40

        raw_sentences = response.xpath('//article//*[@class="news-txt"]/p//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).replace(r'\xa0','')

        return item

