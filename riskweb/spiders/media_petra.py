"""
约旦通讯社 爬虫
"""
import scrapy
import datetime
from riskweb.items import ArticleItem
import logging
import time
import re
logger = logging.getLogger(__name__)

# 按日期请求 API接口 ：
# today = datetime.date.today()
# tomorrow = today + datetime.timedelta(days=-1)
# https://petra.gov.jo/Ajax/NewsWeekAjax.jsp?date=' + tomorrow.strftime('%d/%m/%Y') + '&lang=ar&name=news&Slug=

class MediaPetraSpider(scrapy.Spider):
    name = 'media_petra'
    allowed_domains = ['petra.gov.jo']
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    start_urls = ['https://petra.gov.jo/Ajax/NewsWeekAjax.jsp?date=' + today.strftime('%d/%m/%Y') + '&lang=ar&name=news&Slug=']

    # 直接按ID访问每篇文章
    def parse(self, response, **kwargs):
        latest_news_id = response.xpath(
            '//ul[@id="NNewsList"]/li/i/@data-id').extract_first()
        if latest_news_id is None:
            self.today  = self.today - self.oneday
            yield scrapy.Request('https://petra.gov.jo/Ajax/NewsWeekAjax.jsp?date=' + self.today.strftime('%d/%m/%Y') + '&lang=ar&name=news&Slug=',
                                 self.parse, dont_filter=True)
        else:
            for id in range(77669,int(latest_news_id) + 1): #77669 第一篇发刊id
                yield scrapy.Request('https://petra.gov.jo/Include/InnerPage.jsp?ID=' + str(id) + '&lang=ar&name=news', self.parse_article, dont_filter=True)

    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        #进入每篇文章获取标题
        item['title'] = response.xpath('//div[contains(@class,"TittleArtical")]/*/text()').extract_first()
        item['media_name'] = '约旦通讯社'
        item['url'] = response.url
        item['topic'] = 'News'

        # 发布时间、作者在文章主体内容 最后一个P段落中
        raw_sentences = response.xpath('//div[@id="BodyArtical"]/p/text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        content = '\n'.join(raw_sentences).strip()
        item['content'] = content

        author_pattern = re.compile(r'(.*)\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}')
        author = re.findall(author_pattern, content)
        if len(author) > 0 and len(author[0])>0:
            item['author'] = author[0]
        else:
            item['author'] = 'petra'

        # 正则匹配文章的发布时间 # ح م/ب ط01/10/2018 07:55:21
        publish_date_pattern = re.compile(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}')
        publish_date = re.findall(publish_date_pattern, content)[0]  # 01/10/2018 07:55:21
        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S",
                                             time.strptime(publish_date,
                                                           "%d/%m/%Y %H:%M:%S"))  # June 11, 2021 at 9:51 p.m. EDT

        return item


