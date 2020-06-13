# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TubatuScrapyProjectItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 装修名称
    content_name = scrapy.Field()
    # 装修id
    content_id = scrapy.Field()
    # 请求url
    content_url = scrapy.Field()
    # 昵称
    nick_name = scrapy.Field()
    # 图片的url,必须定义成image_urls
    # pic_url = scrapy.Field()
    image_urls = scrapy.Field()
    # 图片的名称
    pic_name = scrapy.Field()


