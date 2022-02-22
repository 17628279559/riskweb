# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

#pipelines.py用来进行数据存储，由于这里我们不需要将爬取的数据存入数据库中，在终端可以打印输出即可，所以不用配置
class RiskwebPipeline:
    def process_item(self, item, spider):
        return item
