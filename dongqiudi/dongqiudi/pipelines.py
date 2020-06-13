# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from mongodb import mongo
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline

# 数据存储
class DongqiudiPipeline:
    def process_item(self, item, spider):
        mongo.save_data('dongqiudi_data',item)
        return item

# 图片下载
class DongiudiPipeline(ImagesPipeline):
    # def get_media_requests(self, item, info):
    #     # 根据image_urls中指定url进行爬取,不需要重写

    def item_completed(self, results, item, info):
        # 处理图片结果
        image_path = []
        for ok,x in results:
            print(x,'--------------------------------------')
            if ok:
                image_path.append(x['path'])
        if not image_path:
            raise DropItem('Item contains no images')
        return item
    def file_path(self, request, response=None, info=None):
        # 给图片设置名称
        url = request.url
        file_name = url.split('/')[-1]
        return file_name

