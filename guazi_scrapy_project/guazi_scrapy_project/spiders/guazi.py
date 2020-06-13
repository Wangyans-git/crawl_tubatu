# -*- coding: utf-8 -*-
import re
import time

import scrapy

from guazi_scrapy_project.handle_mongodb import mongo
from guazi_scrapy_project.items import GuaziScrapyProjectItem


class GuaziSpider(scrapy.Spider):
    name = 'guazi'
    allowed_domains = ['guazi.com']
    # start_urls = ['http://guazi.com/']

    def start_requests(self):
        while True:
            task = mongo.get_task("guazi_task")
            # 当数据库中没有task时，停止运行
            if not task:
                break
            if "_id" in task:
                task.pop("_id")
            print("当前获取到的task为：",task)
            if task['item_type'] == 'list_item':
                # 这个request对象代表一个http的请求
                # 会尽头downloder去执行，从而产生一个response
                yield scrapy.Request(
                    # 发送请求的url
                    url=task['task_url'],
                    dont_filter=True,  # 这个是否被过滤,True为过滤，避免重复的request请求
                    # 调用回调函数，默认调用parse
                    callback=self.handle_car_item,
                    # 从mongodb重新取出的task
                    meta=task,
                    errback=self.handle_err,  # 当程序处理请求返回有错误的时候
                    # method="GET",
                    # 请求头信息
                    # headers=
                    # body=请求体
                    # cookies =要携带的cookie信息
                    # meta 是字典信息，向其他方法里传递信息
                    # encoding="utf-8"  字符编码
                    # priority=0请求的优先级
                )
            elif task['item_type'] == 'car_info_item':
                yield scrapy.Request(url=task['car_url'], callback=self.handle_car_info, dont_filter=True,
                                     meta=task, errback=self.handle_err)
                # 发送post表单请求
                # yield scrapy.FormRequest()

    # failure接受请求失败的request请求
    # 报错的回调方法
    def handle_err(self,failure):
        # failure.request.meta,来获取失败的task
        # 把失败的请求扔回task库
        print(failure)
        mongo.save_task("guazi_task",failure.request.meta)

    # def parse(self, response):
    #     print(response.text)

    # 自定义解析方法,获取当前页面所展示的二手车
    def handle_car_item(self,response):
        # 当前页面所展示的二手车，item
        if "中为您找到0辆好车" in response.text:
            print("在该城市中没有发现您想要的车型...")
            return
        car_item_list = response.xpath("//ul[@class='carlist clearfix js-top']/li")
        for car_item in car_item_list:
            # 创建一个字典用于存储二手车的名称和详情页url
            car_list_info = {}
            # 因为scrapy在中xpath返回的是一个列表，所以要使用extract_first来获取索引为0的值
            car_list_info['car_name'] = car_item.xpath("./a/h2/text()").extract_first()
            car_list_info['car_url'] = 'https://www.guazi.com'+car_item.xpath("./a/@href").extract_first()
            car_list_info['item_type'] = 'car_info_item'
            # 请求每一个二手车的链接(callback回调的函数，dont_filter过滤重复的url，meta供下一个方法使用的数据)
            yield scrapy.Request(url=car_list_info['car_url'],callback=self.handle_car_info,dont_filter=True,
                                 meta=car_list_info,errback=self.handle_err)
            # print(car_list_info)
        # 判断是否有下一页数据
        if response.xpath("//ul[@class='pageLink clearfix']/li[last()]//span/text()").extract_first() == '下一页':
            # https://www.guazi.com/sz/benz/o3i7/
            value_search = re.compile(r'https://www.guazi.com/(.*?)/(.*?)/o(\d+)i7/')
            try:
                value = value_search.findall(response.url)[0]
                # print(value)
            except:
                pass
            print("-----------------下一页--------------------",response.url)
            # 获取到下一页的url
            response.request.meta['task_url'] = "https://www.guazi.com/%s/%s/o%si7/"%(value[0],value[1],str(int(value[2])+1))
            # 发送request请求，回调到handle_car_item
            yield scrapy.Request(url=response.request.meta['task_url'],callback=self.handle_car_item,
                                 meta=response.request.meta,dont_filter=True,errback=self.handle_err)


    # 解析详情页
    def handle_car_info(self,response):
        # 获取列表页里面的二手车名称，以及二手车的URL
        # 通过车源号进行去重，通过正则表达式，车源号：HC-96308352
        car_id_search = re.compile(r'车源号：(.*?)\s')
        # 创建items的GuaziScrapyProjectItem实例
        car_info = GuaziScrapyProjectItem()
        car_info['car_id'] = car_id_search.search(response.text).group(1)
        car_info['car_name'] = response.request.meta['car_name']
        # 从哪个链接抓取过来的数据
        car_info['from_url'] = response.request.meta['car_url']
        car_info['car_price'] = response.xpath("//div[@class='price-main']/span/text()").extract_first().strip()  # 如果后面存在空格就去除
        car_info['license_time'] = response.xpath("//ul[@class='assort clearfix']//span/img/@src").extract_first().strip()
        car_info['km_info'] = response.xpath("//ul[@class='assort clearfix']/li[@class='two']/span/text()").extract_first().strip()
        # 上牌地
        # license = scrapy.Field()
        # 排量信息
        car_info['displacement_info'] = response.xpath("//ul[@class='assort clearfix']/li[@class='three']/span/text()").extract_first().strip()
        # 变速箱，手动挡还是自动挡 extract()[1]
        car_info['transmission_info'] = response.xpath("//div[@class='product-textbox']//li[@class='last']/span/text()").extract_first().strip()
        # print(car_info)
        yield car_info
