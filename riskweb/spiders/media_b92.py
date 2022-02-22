"""
B92新闻网 爬虫
"""
import scrapy
import time
import logging
import re
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)


class MediaB92Spider(scrapy.Spider):
    name = 'media_b92'
    allowed_domains = ['b92.net']
    count = 0
    def start_requests(self):
        start_urls = [
            'https://www.b92.net/info/vesti/naslovi.php?start=0',
            'https://www.b92.net/sport/vesti.php?start=0',
            'https://www.b92.net/sport/euro2020/vesti.php?start=0',
            'https://www.b92.net/sport/wimbledon2021/vesti.php?start=0',
            'https://www.b92.net/biz/vesti/vesti.php?start=0',
            'https://www.b92.net/zivot/vesti.php?start=0',
            'https://www.b92.net/zdravlje/vesti.php?start=0',
            'https://www.b92.net/putovanja/vesti.php?start=0',
            'https://www.b92.net/bbc/index.php?start=0',
            'https://www.b92.net/automobili/vesti.php?start=0',
            'https://www.b92.net/tehnopolis/vesti.php?start=0',
            'https://www.b92.net/info/koronavirus/index.php?start=0',
            'https://www.b92.net/kultura/vesti.php?start=0',
            'https://www.b92.net/esports/dota2.php?start=0',
            'https://www.b92.net/esports/lol.php?start=0',
            'https://www.b92.net/esports/csgo.php?start=0',
            'https://www.b92.net/esports/wot.php?start=0',
            'https://www.b92.net/esports/hots.php?start=0',
            'https://www.b92.net/esports/hearthstone.php?start=0',
            'https://www.b92.net/esports/overwatch.php?start=0',
            'https://www.b92.net/esports/fgc.php?start=0',
            'https://www.b92.net/esports/starcraft2.php?start=0',
            'https://www.b92.net/esports/ostalo.php?start=0',
        ]
        # 发送请求
        for i in range(0, len(start_urls)):
            yield scrapy.Request(start_urls[i], self.parse_dictionary, dont_filter=False)

    def parse_dictionary(self, response):
        BASEURL = "https://www.b92.net"

        #文章详情链接
        article_paths = response.xpath(
            '//article//h2/a/@href').extract()

        # 单页新闻条数
        # page_action = response.xpath('//form[@name="navigation_form1"]/@onsubmit').extract_first()
        # author_pattern = re.compile(r'value = (\d+) * ')
        # item_count = re.findall(author_pattern, page_action)[0]
        item_count = len(article_paths)
        if item_count == 0:
            # 处理特殊页面
            article_paths = response.xpath(
                '//article//h3/a/@href').extract()
            item_count = len(article_paths)
            if item_count == 0:
                pass

        for article_path in article_paths:
            yield scrapy.Request(BASEURL+article_path, self.parse_article, dont_filter=False)

        # 下一页地址
        next_page = response.xpath(
            '//table[@class="pages-navigation-form-child"]/tr/td[3]/a').extract_first()

        # 增加参数中的start值
        if next_page is not None:

            item_start_pattern = re.compile('start=(?P<number>\d+)')

            def _add(matched):
                intStr = matched.group("number")
                intValue = int(intStr)
                addedValue = intValue + item_count
                addedValueStr = str(addedValue)
                return 'start='+addedValueStr

            load_url = re.sub(item_start_pattern, _add, response.url)
            yield scrapy.Request(load_url, self.parse_dictionary, dont_filter=False)

    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = response.xpath('//div[@class="article-header"]/h1/text()').extract_first()
        item['media_name'] = 'B92新闻网'
        item['url'] = response.url
        item['topic'] = response.xpath('//span[@class="category"]/a/text()').extract_first()
        item['author'] = response.xpath('//div[@class="article-header"]/small/span/text()').extract_first()

        publish_date = response.xpath('//div[@class="article-header"]/small/time/text()').extract_first()

        # 正则匹配文章的发布时间
        publish_date_pattern = re.compile(r'\d+.\d{2}.\d{4}. \| \d{2}:\d{2}') #nedelja, 4.07.2021. | 13:14 ->
        publish_date = re.findall(publish_date_pattern, publish_date)[0]
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date, "%d.%m.%Y. | %H:%M")) #1.04.2021. | 06:40

        raw_sentences = response.xpath('//article[@class="item-page"]/p/text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip()
        #统计能获取多少文章
        self.count = self.count + 1
        logger.debug(self.count)
        return item
