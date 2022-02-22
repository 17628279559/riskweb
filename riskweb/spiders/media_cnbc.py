"""
全国广播公司财经频道 爬虫
"""

import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaAftenpostenSpider(scrapy.Spider):
    name = 'media_cnbc'
    allowed_domains = ['cnbc.com']
    start_urls = ['https://www.cnbc.com/world/?region=world']
    
    # 网站部分新闻收费，需要登录并充钱

    def parse(self, response, **kwargs):

        BASEURL = "https://www.cnbc.com"  
        # 发送请求
        urls = [
                "/china-markets/",
                "/world-markets/"
            ]
        urls.extend(response.xpath('//div[@class="nav-menu-primaryLink business_news"]/ul/li/a/@href').extract())
        urls.extend(response.xpath('//div[@class="nav-menu-primaryLink investing"]/ul/li/a/@href').extract())
        urls.extend(response.xpath('//div[@class="nav-menu-primaryLink tech"]/ul/li/a/@href').extract())
        urls.extend(response.xpath('//div[@class="nav-menu-primaryLink politics"]/ul/li/a/@href').extract())
        urls.remove("https://buffett.cnbc.com") 
        #主页面总共八个大分类，["markets","business_news","investing","tech","politics","cnbc_tv","watchlist","pro"]
        #只有进入小分类才能看见全部新闻,markets内的小分类只有两个有新闻，其他都是各个股市当日走势
        #"cnbc_tv"是各个电视台的视频片段
        #"watchlist"需要登录才能查看，网上查了是黑名单的意思
        #"pro"里面全是收费的新闻

        for url in urls:
            yield scrapy.Request(BASEURL+url, self.parse_dictionary,meta={'url':url,'page':1}, dont_filter=True)

    #scrapy crawl media_cnbc
    def parse_dictionary(self, response):

        if response.xpath('//div[@class="SectionWrapper-content"]') is not None:
            BASEURL = "https://www.cnbc.com" 
            page = response.meta['page']                            
            article_urls = response.xpath('//div[@class="Card-titleContainer"]//a/@href').extract()
            article_urls.extend(response.xpath('//div[@class="RiverCard-titleContainer"]//a/@href').extract())
            #此处过滤掉了所有的收费新闻

            #每页都有5条固定的最新的新闻，只爬一次
            if not re.search( r'page', response.url):
                article_urls.extend(response.xpath('//li[@class="TrendingNowItem-storyItem"]/div/a/@href').extract())


            for article_url in article_urls:
                yield scrapy.Request(article_url, self.parse_article,meta={'topic':response.meta['url'][1:-1]}, dont_filter=False)

            next_page_path = BASEURL+response.meta['url']+'?page='+str(page+1)
            yield scrapy.Request(next_page_path, self.parse_dictionary,meta={'url':response.meta['url'],'page':page+1}, dont_filter=True)

    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        item['media_name'] = '全国广播公司财经频道'
        item['url'] = response.url
        item['topic'] = response.meta['topic']
        #进入每篇文章获取标题
        if not response.xpath('//div[@class="ClipPlayer-clipPlayerVideo"]'):
            item['title'] = response.xpath('//div[@class="ArticleHeader-headerContentContainer"]//h1/text()').extract_first()

            author = response.xpath('//a[@class="Author-authorName"]//text()').extract()

            item['author'] = '|'.join(author).strip()

            publish_date = response.xpath('//time[@data-testid="lastpublished-timestamp"]/@datetime').extract_first()
            if publish_date is None:
                publish_date = response.xpath('//time[@data-testid="published-timestamp"]/@datetime').extract_first()
            publish_date = publish_date.split('+')[0]
            # 匹配文章的发布时间
            item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date, "%Y-%m-%dT%H:%M:%S")) #2021-07-21T15:29:53+0000

            raw_sentences = []
            p = response.xpath('//div[@class="ArticleBody-articleBody"]/div[@class="group"]/p')
            for i in p:
                raw_sentences.append(i.xpath('string(.)').extract_first())

            raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))

            item['content'] = '\n'.join(raw_sentences).strip().replace('/xa0','').replace('/s','s')
            
        else:
            #视频
            item['title'] = response.xpath('//h1[@class="ClipPlayer-clipPlayerIntroTitle"]/text()').extract_first()
            item['author'] = '|'.join(response.xpath('//div[@class="ClipPlayer-author"]/a/text()').extract()).strip()
            publish_date = response.xpath('//div[@class="ClipPlayer-clipPlayerIntroTime"]').xpath('string(.)').extract_first()
            item['publish_date'] = publish_date
            #item['publish_date'] = time.strftime("%Y/%m/%d %H:%M", time.strptime(publish_date, "Thu, %b %d %Y %I:%M %p EDT")) #Thu, Aug 5 2021 5:39 PM EDT
            raw_sentences = response.xpath('//div[@class="ClipPlayer-clipPlayerIntroSummary"]/text()').extract()
            item['content'] = ('此篇新闻为视频,以下为简介:\n'+'\n'.join(raw_sentences).strip()).replace('\xa0','').replace('\s','s')
        return item