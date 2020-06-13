# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy.exceptions import DropItem

from scrapy.pipelines.images import ImagesPipeline

# 需要去setting中打开此功能
class TubatuScrapyProjectPipeline:
    def __init__(self):
        myclient = pymongo.MongoClient("mongodb://localhost:27017")
        myclient.admin.authenticate("admin", "admin123")
        mydb = myclient["db_tubatu"]
        self.my_collections = mydb["collection_tubatu"]

    def process_item(self, item, spider):
        data = dict(item)
        self.my_collections.insert_one(data)
        return item


# 自定义图片下载类
class TubatuImagePipeline(ImagesPipeline):
    # 根据image_urls 中指定的url进行爬取，可以直接调用父类的方法，不需要重写
    # def get_media_requests(self, item, info):
    #     pass

    # 图片下载完毕后，处理结果的，返回一个二元组
    # success,image_info_or_failure
    def item_completed(self, results, item, info):
        print("开始下载图片----------------------------------------------------")
        image_paths = [x["path"] for ok,x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        return item

    # 给下载的图片文件设置文件名称
    def file_path(self, request, response=None, info=None):
        url = request.url
        file_name = url.split('/')[-1]
        return file_name
