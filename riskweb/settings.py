# Scrapy settings for riskweb project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

#scrapy项目名字，用来构造默认的User-Agent，同时也用来log
BOT_NAME = 'riskweb'

# Scrapy搜索spider的模块列表。
SPIDER_MODULES = ['riskweb.spiders']
#使用 genspider 命令创建新spider的模块。
NEWSPIDER_MODULE = 'riskweb.spiders'

# 设置User-Agent（常用）
# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3493.3 Safari/537.36'

# 设置是否遵守robot协议（常用而且一般是不遵守的）
# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Scrapy downloader设置最大并发数（默认是16个，可以自己设置更多。但是要注意电脑的性能）
# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs

# 设置延迟 （批量的）例如有16个线程，那是16个请求之后休息一段时间。而不是每一个休息一段时间
# 下载器在下载同一个网站下一个页面前需要等待的时间,该选项可以用来限制爬取速度,减轻服务器压力。同时也支持小数:0.25 以秒为单位
#DOWNLOAD_DELAY = 3

# 和上方设置最大并发数是一样功能的设置，只能有一个起作用（下载延迟设置只能有一个有效）
# The download delay setting will honor only one of:
# 对单个网站进行并发请求的最大值。
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
# 对单个IP进行并发请求的最大值。如果非0,则忽略 CONCURRENT_REQUESTS_PER_DOMAIN 设定,使用该设定。
# 也就是说,并发限制将针对IP,而不是网站。该设定也影响 DOWNLOAD_DELAY: 如果 CONCURRENT_REQUESTS_PER_IP 非0,下载延迟应用在IP而不是网站上
#CONCURRENT_REQUESTS_PER_IP = 16

# 禁用cookie(默认是启用)
# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# 禁用telnet控制台（默认启用）
# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# 覆盖默认的请求头
# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# 爬虫中间件
# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'riskweb.middlewares.RiskwebSpiderMiddleware': 543,
#}

# 下载中间件
# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#   'riskweb.middlewares.RiskwebDownloaderMiddleware': 543,
#}

# 启用或者禁用扩展
# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# 管道
# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'riskweb.pipelines.RiskwebPipeline': 300,
}

# 启用和配置AutoThrottle扩展（默认情况下禁用）
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True

# 初始下载延迟
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# 在高延迟情况下设置的最大下载延迟
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# Scrapy平均请求数应与每个远程服务器并行发送
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# 启用显示收到的每个响应的限制状态：
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# 启用和配置HTTP缓存（默认情况下禁用）
# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
HTTPERROR_ALLOWED_CODES = [403]
HTTPERROR_ALLOWED_CODES = [301]