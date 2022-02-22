"""
东京产经新闻 爬虫
"""
import scrapy
import time
import logging
from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)
import json

class MediaSankeiSpider(scrapy.Spider):
    name = 'media_sankei'
    allowed_domains = ['sankei.com']
    start_urls = ['http://sankei.com/']
    count = 0
    def start_requests(self):
        # 可能出现的字段
        content_topic_list = ["affairs", "politics", "world", "economy", "sports", "entertainments", "life", "tokyo2020",
                              "gqjapan", "wired", "premium", "column", "west", "region", "photos", "nyushi", "etc"]

        for content_topic in content_topic_list:
            url = 'https://www.sankei.com/pf/api/v3/content/fetch/story-feed-by-sections?query={"feedOffset":0,"feedSize":100,"includeSections":"/'+content_topic +'","paywallTypes":"free,free_members,paid_members"}&filter={content_elements{_id,additional_properties{pressrelease_company_name},content_restrictions{content_code},description{basic},display_date,headlines{basic},promo_items{basic{additional_properties{focal_point},alt_text,caption,focal_point,height,resizedUrls{storyCardExtraLarge,storyCardHeadline,storyCardLarge,storyCardMedium,storyCardSmall},type,url,width}},subtype,taxonomy{sections{_id,_website,name,parent_id,path}},website_url,websites{iza{website_section{_id},website_url},sankei{website_section{_id},website_url}}},count}&d=87&_website=sankei'
            yield scrapy.Request(url, self.parse_json, meta={'topic':content_topic, 'offset':100}, dont_filter=True) # 每次最多请求100条

    def parse_json(self,response): # 解析json格式的返回内容
        data = json.JSONDecoder().decode(response.text)
        content_elements = data['content_elements']

        for content_element in content_elements: # 解析文章信息
            url = "https://www.sankei.com" + content_element['websites']['sankei']['website_url']
            yield scrapy.Request(url, self.parse_article, dont_filter=False)

        count = data['count'] # 该topic下的总文章数目
        offset = response.meta['offset']
        topic = response.meta['topic']
        if offset < count:
            if offset + 100 < count:
                feedSize = 100
            else:
                feedSize = count - offset
            url = 'https://www.sankei.com/pf/api/v3/content/fetch/story-feed-by-sections?query={"feedOffset":'+ str(offset) +',"feedSize":'+str(feedSize)+',"includeSections":"/'+topic +'","paywallTypes":"free,free_members,paid_members"}&filter={content_elements{_id,additional_properties{pressrelease_company_name},content_restrictions{content_code},description{basic},display_date,headlines{basic},promo_items{basic{additional_properties{focal_point},alt_text,caption,focal_point,height,resizedUrls{storyCardExtraLarge,storyCardHeadline,storyCardLarge,storyCardMedium,storyCardSmall},type,url,width}},subtype,taxonomy{sections{_id,_website,name,parent_id,path}},website_url,websites{iza{website_section{_id},website_url},sankei{website_section{_id},website_url}}},count}&d=87&_website=sankei'
            yield scrapy.Request(url, self.parse_json, meta={'topic':topic, 'offset': offset + feedSize}, dont_filter=True)

    def parse_article(self, response):
        #调取参数
        item = ArticleItem()
        pre_info = response.xpath('//div[@class="article-header "]')
        #进入每篇文章获取标题
        item['title'] = pre_info.xpath('//*[@class="article-headline"]/text()').extract_first()
        item['media_name'] = '东京产经新闻'
        item['url'] = response.url
        labels = pre_info.xpath('//ul//text()').extract()
        if len(labels) > 0:
            item['topic'] = '|'.join(labels)
        elif len(labels) == 1:
            item['topic'] = labels[0]
        else:
            item['topic'] = ''

        item['author'] = ''

        publish_date = pre_info.xpath('//time/text()').extract_first()

        item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date, "%Y/%m/%d %H:%M")) # 2021/7/21 15:58

        raw_sentences = response.xpath('//div[contains(@class,"article-body")]/p//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip()
        self.count += 1
        print(self.count)
        return item

