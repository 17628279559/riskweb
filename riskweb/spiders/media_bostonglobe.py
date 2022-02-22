"""
波士顿环球报 爬虫
"""
import scrapy
import json
from riskweb.items import ArticleItem
import logging
import time
logger = logging.getLogger(__name__)
from scrapy.selector import Selector
import re

class MediaBostonglobeSpider(scrapy.Spider):
    name = 'media_bostonglobe'
    allowed_domains = ['bostonglobe.com']

    # //div[contains(@class,"card")]/a/@href
    #
    def start_requests(self):
        # 主题分类路径
        topic_paths = [
            '/metro',
            '/sports',
            '/business',
            '/opinion',
            '/nation',
            '/world',
            '/lifestyle',
            '/marijuana',
            '/arts',
        ]
        # 发送请求
        # https://www.bostonglobe.com/pf/api/v3/content/fetch/content-feed?query={"elasticSearchQuery":"true","offset":"6","query":"{\"query\":{\"prefix\":{\"taxonomy.primary_section._id\":\"/metro/globelocal\"}}}","size":"32"}&filter={_id,content_elements{_id,canonical_url,content_restrictions{content_code},credits{by{image{url},name,slug}},description{basic},display_date,duration,headlines{basic,native},label{ampexclude{text},appexclude{text},basic{text,url},storycard{text,url}},last_updated_date,promo_items{basic{additional_properties{focal_point{min}},alt_text,caption,credits{by{name}},type,url,width},storycard_override{additional_properties{focal_point{min}},alt_text,caption,credits{by{name}},type,url,width}},publicationPitches{currentStatus,publicationName},publish_date,related_content{basic{_id}},revision{revision_id},taxonomy{primary_section{name}},type,website_url},content_restrictions{content_code},revision{revision_id},subtype,type}&d=276&_website=bostonglobe
        for topic_path in topic_paths:
            for i in range(0, 100):
                offset = 0 + i * 100 # 每个类型最多取20条
                yield scrapy.Request('https://www.bostonglobe.com/pf/api/v3/content/fetch/content-feed?query={"elasticSearchQuery":"true","offset":"' + str(offset) + '","query":"{\\"query\\":{\\"prefix\\":{\\"taxonomy.primary_section._id\\":\\"' + topic_path+ '\\"}}}","size":"100"}&filter={_id,content_elements{_id,canonical_url,content_restrictions{content_code},credits{by{image{url},name,slug}},description{basic},display_date,duration,headlines{basic,native},label{ampexclude{text},appexclude{text},basic{text,url},storycard{text,url}},last_updated_date,promo_items{basic{additional_properties{focal_point{min}},alt_text,caption,credits{by{name}},type,url,width},storycard_override{additional_properties{focal_point{min}},alt_text,caption,credits{by{name}},type,url,width}},publicationPitches{currentStatus,publicationName},publish_date,related_content{basic{_id}},revision{revision_id},taxonomy{primary_section{name}},type,website_url},content_restrictions{content_code},revision{revision_id},subtype,type}&d=276&_website=bostonglobe', self.parse_json, meta={
                    'topic': topic_path.replace('/','')
                }, dont_filter=False)

    def parse_json(self,response):
        # 基础网址
        BASEURL = 'https://www.bostonglobe.com/'
        data = json.JSONDecoder().decode(response.text)
        content_elements = data['content_elements']
        # 从获取的json中取title url datetime content_topic
        for content_element in content_elements:
            article_url = BASEURL + content_element['canonical_url']
            yield scrapy.Request(article_url, self.parse_article, meta=response.meta, dont_filter=False)

    def parse_article(self,response):
        # 调取参数
        item = ArticleItem()
        # 进入每篇文章获取标题
        article = response.xpath('//div[contains(@class,"article")]')
        item['title'] = article.xpath('./*[contains(@class,"headline")]/text()').extract_first()
        item['media_name'] = '波士顿环球报'
        item['url'] = response.url
        item['topic'] = response.meta['topic']
        item['author'] = article.xpath('.//*[contains(@class,"author")]/span/text()').extract_first()

        publish_date = ''.join(article.xpath('.//*[contains(@class,"datetime")]/span/text()').extract()) # Updated July 2, 2021, 1:52 p.m.
        # 正则匹配文章的发布时间
        publish_date_pattern = re.compile(
            r'Updated (.+ \d+, \d{4}, \d+:\d+ .\.m\.)') #  Updated July 2, 2021, 1:52 p.m.
        publish_date_matched = re.findall(publish_date_pattern, publish_date)[0]

        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S",
                                             time.strptime(publish_date_matched.replace('a.m.', 'am').replace('p.m.', 'pm'),
                                                           "%B %d, %Y, %H:%M %p"))  # July 2, 2021, 1:52 p.m.

        raw_sentences = response.xpath('//p[contains(@class,"paragraph")]/span/text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip()
        return item