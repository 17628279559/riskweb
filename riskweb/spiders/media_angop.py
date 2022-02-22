"""
安哥拉新闻社 爬虫
葡萄牙语

"""
import time
import scrapy
import logging

from riskweb.items import ArticleItem
logger = logging.getLogger(__name__)

class MediaAngopSpider(scrapy.Spider):
    name = 'media_angop'
    allowed_domains = ['angop.ao']
    def start_requests(self):
        #开始爬取网址
        start_urls = [
            'https://www.angop.ao/angola/noticias/',
            'https://www.angop.ao/edt/provincias/']
        #发送请求
        for i in range(0, len(start_urls)):
            yield scrapy.Request(start_urls[i], self.parse_dictionary, dont_filter=True)

    def parse_dictionary(self, response):
        #基础网址
        BASEURL = "https://www.angop.ao"
        #文章详情链接
        article_urls = response.xpath(
            '//*[@id="content-section"]/div/div[@class="row"]/div[@class="col-lg-8"]/div[1]/div[2]/div/div/h2/a/@href').extract()

        for article_url in article_urls:
            article_url = f'{BASEURL}{article_url}'
            yield scrapy.Request(article_url, self.parse_article)

        # 分页链接
        next_page_url = response.xpath(
            '//*[@id="content-section"]/div/div[2]/div[1]/div[1]/ul[@class="MarkupPagerNav"]/li[@class="MarkupPagerNavNext MarkupPagerNavLast"]/a/@href').extract_first()
        # 如果存在下一页，继续请求
        if next_page_url is not None:
            next_page_url = f'{BASEURL}{next_page_url}'
            yield scrapy.Request(next_page_url, self.parse_dictionary, dont_filter=True)

    def parse_article(self, response):
        # 调取参数
        item = ArticleItem()
        # 进入每篇文章获取标题
        item['title'] = response.xpath('//*[@id="content-section"]/div/div[@class="row"]/div[@class="col-lg-8"]/div[@class="single-post"]/h1/text()').extract_first()
        item['media_name'] = '安哥拉新闻社'
        item['url'] = response.url
        item['topic'] = response.xpath(
            '//*[@id="content-section"]/div/div[2]/div[1]/div[1]/ul[1]/div/div[@class="col"]/span[@class="lista_noticias"]/a/text()').extract_first().replace(' ', '').replace('\xa0', '')

        item['author'] = response.xpath('//*[@id="content-section"]/div/div[2]/div[1]/div[1]/ul[1]/div/div[2]/span[@class="lista_noticias"]/li/i[1]/text()').extract_first()

        month_spec = {
            'Janeiro': 'January',
            'Fevereiro': 'February',
            'Março': 'March',
            'Abril': 'April',
            'Maio': 'May',
            'Junho': 'June',
            'Julho': 'July',
            'Agosto': 'August',
            'Setembro': 'September',
            'Outubro': 'October',
            'Novembro': 'November',
            'Dezembro': 'December'
        }
        unformatted_date = response.xpath(
            '//*[@id="content-section"]/div/div[2]/div[1]/div[1]/ul[1]/div/div[2]/span[2]/li/text()').extract()
        unformatted_date = ''.join(unformatted_date).replace('\n', '').replace('\xa0', '').strip()
        # 删除星期和逗号
        index = unformatted_date.find(",")
        indexs = unformatted_date[:index]
        unformatted_date = unformatted_date.replace(indexs, '').replace(',', '').strip()

        # 将葡萄牙语的月份替换为英文月份
        unformatted_month = unformatted_date.split()[1]
        formatted_month = month_spec[unformatted_month]
        unformatted_date = unformatted_date.replace(unformatted_month, formatted_month)

        #时间格式转换
        if unformatted_date:
            item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(unformatted_date, "%d %B De %Y%Hh%M"))

        raw_sentences = response.xpath('//*[@id="content-section"]/div/div[2]/div[1]/div[1]/div[3]//text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip().replace('\n', '').replace('\xa0', '')

        return item
