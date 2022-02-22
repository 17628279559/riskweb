"""
华盛顿邮报 爬虫
"""
import scrapy
import json
from riskweb.items import ArticleItem
import logging
import time
logger = logging.getLogger(__name__)
from scrapy.selector import Selector
import re
import datetime

class MediaWashingtonpostSpider(scrapy.Spider):
    name = 'media_washingtonpost'
    allowed_domains = ['washingtonpost.com']
    start_urls = ['http://washingtonpost.com/']
    count = 0

    def start_requests(self):
        # 可能出现的字段
        topic_paths = {
            'Politics':'site-articles-only,/politics',
            'Politics/PowerPost': 'site,/politics/powerpost',
            'Politics/Courts & Law': 'site,/politics/courts-law',
            'Politics/The Fix': 'site,/politics/the-fix',
            'Politics/Monkey Cage': 'site,/politics/monkey-cage',
            'Politics/Polling': 'polling-page',
            'Politics/White House': 'white-house-page/',
            'Opinions/The Post\'s View': 'author,the-posts-view',
            'Opinions/Editorial Cartoons': 'site-and-tag,/opinions,cartoon',
            'Opinions/Letters to the Editor':'letters-to-the-editor/',
            'Opinions/The Plum Line':'site,/opinions/plum-line',
            'Investigations': 'site,/national/investigations',
            'Tech': 'site-articles-only,/technology',
            'Tech/Consumer Tech': 'site,/technology/consumer-tech',
            'Tech/Future of Transportation': 'magnet-futuretransportation/',
            'Tech/Innovations': 'site,/technology/innovations',
            'Tech/Internet Culture': 'site,/technology/internet-culture',
            'Tech/Space': 'site,/technology/space',
            'Tech/Tech Policy': 'site,/technology/tech-policy',
            'Tech/Video Gaming': 'site,/sports/launcher',
            'World/Africa': 'site,/world/africa',
            'World/Americas': 'site,/world/americas',
            'World/Asia': 'site,/world/asia-pacific',
            'World/Europe': 'site,/world/europe',
            'World/Middle East': 'site,/world/middle-east',
            'D.C., Md. & Va./The District': 'local-states,/local/dc,/local/dc/dc-politics,DC',
            'D.C., Md. & Va./Maryland': 'local-states,/local/maryland,/local/maryland/md-politics,MD',
            'D.C., Md. & Va./Virginia': 'local-states,/local/virginia,/local/virginia/vapolitics,VA',
            'D.C., Md. & Va./Local Crime & Public Safety': 'site-articles-only,/local/public-safety',
            'D.C., Md. & Va./Local Education': 'site,/local/education',
            'D.C., Md. & Va./Going Out Guide': 'site,/entertainment/going-out-guide',
            'D.C., Md. & Va./Restaurants & Bars': 'site,/entertainment/restaurants',
            'D.C., Md. & Va./Local Transportation': 'site,/local/traffic-commuting',
            'Sports/National Football League': 'site,/sports/nfl',
            'Sports/National Football League/NFL wires': 'ap-articles-by-site-id,/sports/nfl',
            'Sports/Major League Baseball': 'site,/sports/mlb',
            'Sports/Major League Baseball:MLB wires': 'ap-articles-by-site-id,/sports/mlb',
            'Sports/National Basketball Association': 'site,/sports/nba',
            'Sports/National Basketball Association/NBA wires': 'ap-articles-by-site-id,/sports/nba',
            'Sports/National Hockey League': 'site-with-wires,/sports/nhl',
            'Sports/Boxing & MMA': 'site-with-wires,/sports/boxing-mma',
            'Sports/College Sports': 'site,/sports/colleges',
            'Sports/College Sports:College sports wires': 'ap-articles-by-site-id,/sports/colleges',
            'Sports/D.C. Sports Bog': 'site,/sports/dc-sports-bog',
            'Sports/Golf': 'site-with-wires,/sports/golf',
            'Sports/Soccer': 'site,/sports/soccer',
            'Sports/Tennis': 'site-with-wires,/sports/tennis',
            'Sports/WNBA': 'two-sites,/sports/mystics,/sports/wnba',
            'Arts & Entertainment':'entertainment',
            'Arts & Entertainment/Movies': 'site,/entertainment/movies',
            'Arts & Entertainment/Museums': 'site,/entertainment/museums',
            'Arts & Entertainment/Music': 'site,/entertainment/music',
            'Arts & Entertainment/Pop Culture': 'site,/entertainment/pop-culture',
            'Arts & Entertainment/Theater & Dance': 'site,/entertainment/theater-dance',
            'Business/Economic Policy': 'site,/us-policy/economic-policy',
            'Business/Economy': 'site,/business/economy',
            'Business/Energy': 'site,/business/energy',
            'Business/Health Care': 'business-health-care/',
            'Business/Markets': 'business-markets/',
            'Business/Personal Finance': 'personal-finance/',
            'Business/Small Business': 'site-with-wires,/business/on-small-business',
            'Climate & Environment':'site,/climate-environment',
            'Coronavirus/Navigating Your Life/Health & Wellness': 'site,/lifestyle/wellness',
            'Coronavirus/Navigating Your Life/Parenting': 'site,/lifestyle/on-parenting',
            'Coronavirus/Navigating Your Life/Home & Garden': 'site-and-discussions-not-future,/lifestyle/home-garden',
            'Coronavirus/Navigating Your Life/Travel': 'coronavirus-travel-utility/',
            'Coronavirus/Navigating Your Life/Arts & Entertainment': 'entertainment',
            'Coronavirus/Navigating Your Life/Technology': 'site,/technology/consumer-tech',
            'Education': 'two-sites,/education,/local/education',
            'Education/Higher Education': 'site,/education/higher-education',
            'Health':'health-kaiser/',
            'Health/Medical Mysteries': 'author,sandra-g-boodman',
            'Health/Wellness': 'site,/lifestyle/wellness',
            'History': 'site,/history',
            'History/Made by History': 'site,/opinions/made-by-history',
            'Immigration': 'site,/immigration',
            'Lifestyle': 'site-articles-only,/lifestyle',
            'Lifestyle/Fashion': 'site,/lifestyle/fashion',
            'Lifestyle/Home & Garden': 'site-and-discussions-not-future,/lifestyle/home-garden',
            'Lifestyle/Parenting': 'site,/lifestyle/on-parenting',
            'Lifestyle/Relationships': 'site,/lifestyle/relationships',
            'Lifestyle/Travel': 'site,/lifestyle/travel',
            'National Security':'site,/national-security',
            'National Security/Foreign Policy': 'national-security-foreign-policy/',
            'National Security/Justice': 'justice-page/',
            'National Security/Military': 'national-security-military/',
            'Obituaries': 'obits-stream',
            'Outlook': 'site,/opinions/outlook',
            'Outlook/Book Party': 'site,/opinions/book-party',
            'Outlook/Five Myths': 'site-and-tag,/opinions/outlook,fivemyths',
            'Religion': 'site,/religion',
            'Science': 'site,/science',
            'Science:Animals': 'site,/science/animals',
            'Transportation': 'two-sites,/local/traffic-commuting,/transportation',
        }
        topic_paths_of_new = {
            'Politics/Fact Checker': '/politics/fact-checker',
            'Coronavirus/Navigating Your Life/Food': '/lifestyle/food/voraciously',
            'Food/Voraciously':'/lifestyle/food/voraciously',
            'History/Retropolis': '/local/retropolis',
            'Outlook/PostEverything': '/opinions/posteverything',
        }
        topic_paths_variable = {
            'Opinions/Global Opinions': {
                'query': 'global-opinions-english-only',
                'id': 'f00V2ZiUWhyJos',
                'uri': '/global-opinions/'
            },
            'Opinions/Local Opinions/Local Editorials': {
                'query': 'byline-and-tag,the-posts-view,local',
                'id': 'fjUCNf1P6BzPos',
                'uri': '/opinions/local-opinions/'
            },
            'Opinions/Local Opinions/Local Opinions': {
                'query': 'local-opinions/',
                'id': 'f0AxbuxP6BzPos',
                'uri': '/opinions/local-opinions/'
            },
            'Opinions/Local Opinions/Letters to the Editor': {
                'query': 'subtype,Letter',
                'id': 'fyyEPn1P6BzPos',
                'uri': '/opinions/local-opinions/'
            },
            'Opinions/Local Opinions/Free for All': {
                'query': 'site-and-tag,/opinions,opinionsnewsletterffa',
                'id': 'fHKtMh2P6BzPos',
                'uri': '/opinions/local-opinions/'
            },
            'Opinions/The Opinions Essay': {
                'query': 'tag,toe-page-feature',
                'id': 'f00oMyOFZ6thzs',
                'uri': '/the-opinions-essay/'
            },
            'Opinions/Post Opinión': {
                'query': 'spanish-no-opinions/',
                'id': 'fdYDrk2EVfGYBs',
                'uri': '/es/post-opinion/'
            },
            'Opinions/Alexandra Petri': {
                'query': 'author,alexandra-petri',
                'id': 'f0pKxTyyqZqMns',
                'uri': '/people/alexandra-petri/'
            },
            'Opinions/Jennifer Rubin': {
                'query': 'author,jennifer-rubin',
                'id': 'f0pKxTyyqZqMns',
                'uri': '/people/jennifer-rubin/'
            },
            'Opinions/Erik Wemple': {
                'query': 'author,erik-wemple',
                'id': 'f0pKxTyyqZqMns',
                'uri': '/people/erik-wemple/'
            },
            'World': {
                'query': 'site-articles-only,/world/',
                'id': 'fF9qBc1IfLRgts',
                'uri': '/world/'
            },
            'World/From the Wires': {
                'query': 'ap-articles-by-site-id,/world',
                'id': 'fxtSNd2IfLRgts',
                'uri': '/world/'
            },
            'D.C., Md. & Va.':{
                'query': 'local-article-feed/',
                'id': 'f0pBIGj6p4Rvns',
                'uri': '/local/'
            },
            'Sports': {
                'query': 'site-articles-only,/sports',
                'id': 'fsJlkg2vAytaCs',
                'uri': '/sports/'
            },
            'Sports/High School Sports': {
                'query': 'site,/sports/highschools',
                'id': 'fBdHsO1QiFCT3s',
                'uri': '/allmetsports/2020-spring/'
            },
            'Race & Reckoning/Opinions': {
                'query': 'site-and-tag,/opinions,magnet-race',
                'id': 'fTrLok1Xgd4pBs',
                'uri': '/race-america/'
            },
            'Race & Reckoning/Latest News': {
                'query': 'race-reckoning-page',
                'id': 'fUno901Xgd4pBs',
                'uri': '/race-america/'
            },
            'Arts & Entertainment/Books': {
                'query': 'site,/entertainment/books',
                'id': 'f0A81l1QvDwEzs',
                'uri': '/entertainment/books/'
            },
            'Arts & Entertainment/Television': {
                'query': 'site,/entertainment/tv',
                'id': 'f0tqXAfoZj05ts',
                'uri': '/entertainment/tv/'
            },
            'Business':{
                'query': 'site-articles-only,/business',
                'id': 'fAkM8F1wPsgOqs',
                'uri': '/business/'
            },
            'Business/Real Estate': {
                'query': 'site,/realestate',
                'id': 'ftM3Ji21tPCnrs',
                'uri': '/realestate/'
            },
            'Coronavirus/Navigating Your Life/More Coverage': {
                'query': 'tag,virus-utility',
                'id': 'fcxrf32noPehzs',
                'uri': '/coronavirus/living/'
            },
            'Food': {
                'query': 'site,/lifestyle/food',
                'id': 'f0BKJ8XOcUuQcs',
                'uri': '/food/'
            },
            'Lifestyle/Advice': {
                'query': 'author-no-discussions,carolyn-hax',
                'id': 'f0ykPcNEkuFqbs',
                'uri': '/lifestyle/advice/'
            },
            'Lifestyle/KidsPost': {
                'query': 'site-with-wires,/lifestyle/kidspost',
                'id': 'fhtYiH1aHoImAs',
                'uri': '/lifestyle/kidspost/'
            },
            'Magazine': {
                'query': 'magazine-archive/',
                'id': 'fxtXVb1AjYkVBs',
                'uri': '/lifestyle/magazine/'
            },
            'National': {
                'query': 'site-articles-only,/national',
                'id': 'ftvpFY1XAMpFms',
                'uri': '/national/'
            },
        }
        static_page_urls = {
            'Opinions:Voices Across America': 'https://www.washingtonpost.com/opinions/voices-across-america/',
            'Investigations:Policing In America': 'https://www.washingtonpost.com/police-america/',
            'Sports:Tokyo Summer Games': 'https://www.washingtonpost.com/sports/olympics/tokyo-summer-games/',
            'Climate Solutions': 'https://www.washingtonpost.com/climate-solutions',
            'Coronavirus': 'https://www.washingtonpost.com/coronavirus/',
            'Lifestyle:Inspired Life': 'https://www.washingtonpost.com/inspired-life/',
            'The Biden Administration': 'https://www.washingtonpost.com/politics/joe-biden-46th-president/',
            'Weather': 'https://www.washingtonpost.com/local/weather/'
        }
        for topic in topic_paths.keys():
            for i in range(100):        # 每个类型最多取20条
                offset = 0 + i * 20
                # 拼接 url
                load_url = 'https://www.washingtonpost.com/pb/api/v2/render/feature/section/story-list' \
                           '?content_origin=prism-query&url=prism://prism.query/'+topic_paths[topic]+'&offset='+str(offset)+'&limit=20'
                yield scrapy.Request(load_url, self.parse_json, meta={"topic": topic}, dont_filter=False)

        for topic in topic_paths_of_new.keys():
            for i in range(100):        # 每个类型最多取10条
                offset = 0 + i * 10
                # 拼接 url
                load_url = 'https://www.washingtonpost.com/pb/api/v2/render/feature/section/story-list' \
                           '?addtl_config=blog-front&content_origin=content-api-query&size=10&from='+str(offset)+'&primary_node='+topic_paths[topic]
                yield scrapy.Request(load_url, self.parse_json, meta={"topic": topic}, dont_filter=False)

        for topic in topic_paths_variable.keys():
            for i in range(100):        # 每个类型最多取250条
                offset = 0 + i * 250
                # 拼接 url
                load_url = 'https://www.washingtonpost.com/pb/api/v2/render/feature/?service=prism-query' \
                           '&contentConfig={{"url":"prism://prism.query/{query}","offset":{offset},"limit":250}}' \
                           '&customFields={{"isLoadMore":true,"offset":0,"maxToShow":250,"dedup":false}}' \
                           '&id={id}&rid=&uri={uri}' \
                    .format(query=topic_paths_variable[topic]['query'],offset=offset,id=topic_paths_variable[topic]['id'],uri=topic_paths_variable[topic]['uri'])
                yield scrapy.Request(load_url, self.parse_json, meta={"topic": topic}, dont_filter=False)

        for topic in static_page_urls.keys():
            yield scrapy.Request(static_page_urls[topic], self.parse_dictionary, meta={"topic": topic}, dont_filter=False)

    def parse_dictionary(self, response):
        # 文章详情链接
        article_urls = response.xpath('//div[contains(@class,"card")]//h2//a/@href').extract()
        for article_url in article_urls:
            yield scrapy.Request(article_url, self.parse_article, meta=response.meta, dont_filter=False)


    def parse_json(self, response):
        # json
        json_data = json.JSONDecoder().decode(response.text)
        # 从获取的json中取html
        html = json_data['rendering']
        if html is None:
            pass
        # 文章详情链接
        article_urls = Selector(text=html).xpath(
            '//div[@class="story-headline"]/h2/a/@href').extract()

        for article_url in article_urls:
            yield scrapy.Request(article_url, self.parse_article, meta=response.meta )

    def parse_article(self,response):
        # 调取参数
        item = ArticleItem()
        # 进入每篇文章获取标题
        item['title'] = response.xpath('//span[@data-qa="headline-text"]/text()').extract_first()
        item['media_name'] = '华盛顿邮报'
        item['url'] = response.url
        item['topic'] = response.meta['topic']
        item['author'] = ' '.join(response.xpath('//a[@data-qa="author-name"]//text()').extract())

        timestamp = response.xpath('//div[@data-qa="timestamp"]')

        updated_date = timestamp.xpath('./span[@data-qa="updated-date"]/text()').extract_first()
        if updated_date is not None:
            # 正则匹配文章的发布时间
            publish_date_pattern = re.compile(r'(.+ \d+, \d{4} at \d+:\d+ .\.m\.) .+')  # June 11, 2021 at 9:51 p.m. EDT
            publish_date = re.findall(publish_date_pattern, updated_date)
            if len(publish_date) == 0: # 当天新闻
                today = datetime.date.today().strftime('%B %d, %Y')
                publish_date_pattern = re.compile(r'(\d+:\d+ .\.m\.) .+')  # 8:34 p.m. EDT
                publish_date = today + ' at ' + re.findall(publish_date_pattern, updated_date)[0] # June 11, 2021 at 9:51 p.m. EDT
            else:
                publish_date = publish_date[0]
            item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S",
                                                 time.strptime(publish_date.replace('p.m.', 'PM').replace('a.m.', 'AM'),
                                                               "%B %d, %Y at %H:%M %p"))  # June 11, 2021 at 9:51 p.m. EDT
        else:
            publish_date = timestamp.xpath('./span[@data-qa="publish-date"]/text()').extract_first() # June 14, 2021
            item['publish_date'] = time.strftime("%Y/%m/%d %H:%M:%S",
                                                 time.strptime(publish_date,
                                                               "%B %d, %Y"))  # June 14, 2021
        raw_sentences = response.xpath('//div[@class="article-body"]//p/text()').extract()
        raw_sentences = list(filter(lambda sentence: sentence.strip(), raw_sentences))
        item['content'] = '\n'.join(raw_sentences).strip()
        #统计能获取多少文章
        self.count = self.count + 1
        print(self.count)
        return item

