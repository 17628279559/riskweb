"""
thehindu新闻 爬虫
"""
import time
import scrapy
import logging
from riskweb.items import ArticleItem

logger = logging.getLogger(__name__)

class ThehinduSpider(scrapy.Spider):
    name = 'media_thehindu'
    allowed_domains = ['thehindu.com']
    def start_requests(self):
        #开始爬取网址
        start_urls = [
            'https://www.thehindu.com/news/international/',
            'https://www.thehindu.com/news/national/',

            # 'https://www.thehindu.com/news/national/andhra-pradesh/',
            # 'https://www.thehindu.com/news/national/karnataka/',
            # 'https://www.thehindu.com/news/national/kerala/',
            # 'https://www.thehindu.com/news/national/tamil-nadu/',
            # 'https://www.thehindu.com/news/national/telangana/',
            # 'https://www.thehindu.com/news/national/other-states/'
            
            # 'https://www.thehindu.com/news/cities/bangalore/',
            # 'https://www.thehindu.com/news/cities/chennai/',
            # 'https://www.thehindu.com/news/cities/Coimbatore/',
            # 'https://www.thehindu.com/news/cities/Delhi/',
            # 'https://www.thehindu.com/news/cities/Hyderabad/',
            # 'https://www.thehindu.com/news/cities/Kochi/',
            # 'https://www.thehindu.com/news/cities/kolkata/',

            # 'https://www.thehindu.com/opinion/editorial/',
            # 'https://www.thehindu.com/opinion/interview/',
            # 'https://www.thehindu.com/opinion/lead/',
            # 'https://www.thehindu.com/opinion/Readers-Editor/',
            # 'https://www.thehindu.com/opinion/op-ed/',

            # 'https://www.thehindu.com/business/',

            # 'https://www.thehindu.com/sport/',

            # 'https://www.thehindu.com/entertainment/art/',
            # 'https://www.thehindu.com/entertainment/dance/',
            # 'https://www.thehindu.com/entertainment/movies/',
            # 'https://www.thehindu.com/entertainment/music/',
            # 'https://www.thehindu.com/entertainment/reviews/',
            # 'https://www.thehindu.com/entertainment/theatre/',

            # 'https://www.thehindu.com/sci-tech/science/',
        ]

        #发送请求
        for i in range(0, len(start_urls)):
            yield scrapy.Request(start_urls[i], self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):
        #基础网址
        #文章详情链接
        article_urls = response.xpath(
            '/html/body/div[2]/section/section/div[2]/div/div[2]/div/div/div/div/span/a[2]/@href').extract()
        print('number of article:')
        print(len(article_urls))
        for article_url in article_urls:
            yield scrapy.Request(article_url, self.parse_article)

        article_urls = response.xpath(
            '/html/body/div[2]/section/section/div[2]/div/div[2]/div/div/div/h3/a/@href').extract()
        print('number of article:')
        print(len(article_urls))
        for article_url in article_urls:
            yield scrapy.Request(article_url, self.parse_article)

        nextpage_url = response.xpath(
            '/html/body/div[2]/section/section/div[2]/div/div[1]/ul/li[23]/a/@href').extract_first()
        print(nextpage_url)
        if nextpage_url is not None:
            yield scrapy.Request(nextpage_url, self.parse_dictionary)

    def parse_article(self, response):
        # 调取参数
        item = ArticleItem()
        # 进入每篇文章获取标题

        item['title'] = response.xpath('/html/body/div[2]/div[2]/div/div/div/section/div/div/div/div[1]/h1/text()').extract_first()
        item['media_name'] = 'Thehindu新闻'
        item['url'] = response.url
        item['topic'] = response.xpath('/html/body/div[2]/div[2]/div/div/div/section/div/div/div/div[1]/div[1]/a/text()').extract_first()
        item['author'] = response.xpath('/html/body/div[2]/div[2]/div/div/div/section/div/div/div/div[1]/div[2]/span/a[2]/text()').extract_first()

        month_spec = {
            'January': '01',
            'February': '02',
            'March': '03',
            'April': '04',
            'May': '05',
            'June': '06',
            'July': '07',
            'August': '08',
            'September': '09',
            'October': '10',
            'November': '11',
            'December': '12'
        }

        unformatted_date = response.xpath('/html/body/div[2]/div[2]/div/div/div/section/div/div/div/div[1]/div[2]/div/div/span/none/text()').extract_first()
        # '\nJuly 13, 2021 19:51 IST\n'
        unformatted_date = unformatted_date.replace('\\n','')
        print(unformatted_date)
        unformatted_month = unformatted_date.split()[0]
        unformatted_month = month_spec[unformatted_month]
        unformatted_day = unformatted_date.split()[1].replace(',','')
        unformatted_year = unformatted_date.split()[2]
        unformatted_time = unformatted_date.split()[3]
        unformatted_hour = unformatted_time.split(":")[0]
        unformatted_minute = unformatted_time.split(":")[1]
        print(unformatted_day, unformatted_month, unformatted_year, unformatted_time)
        # publish_date = publish_date_year + unformatted_date
        # item['publish_date'] = publish_date
        # if publish_date:
        #     item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(publish_date, "%Y%B %d"))
        item['publish_date'] = unformatted_year+"/"+unformatted_month+"/"+unformatted_day+" "+unformatted_hour+":"+unformatted_minute+":00"



        raw_sentences = response.xpath('/html/body/div[2]/div[2]/div/div/div/section/div/div/div/div[3]/div[3]/p/text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip()
        return item
