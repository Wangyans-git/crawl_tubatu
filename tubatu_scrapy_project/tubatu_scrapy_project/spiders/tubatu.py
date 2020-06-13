 # -*- coding: utf-8 -*-
import scrapy
import re
import json

from tubatu_scrapy_project.items import TubatuScrapyProjectItem

class TubatuSpider(scrapy.Spider):
    name = 'tubatu'
    # 允许爬虫去抓取的域名
    allowed_domains = ['xiaoguotu.to8to.com']
    # 项目启动之后要启动的爬虫文件
    start_urls = ['https://xiaoguotu.to8to.com/tuce/p_1.html']

    # 默认的解析方法
    def parse(self, response):
        print(response.request.headers)
        content_id_search = re.compile(r'(\d+)\.html')
        # response后面可以直接使用xpath方法
        # response就是一个Html对象，不需要实例化
        pic_item_list = response.xpath("//div[@class='item']")
        # print(pic_item_list)
        for item in pic_item_list:
            info = {}
            # 通过extract_first直接获取项目名称，项目的数据
            info['content_name'] = item.xpath(".//div/a/text()").extract_first()
            # 获取项目url
            if item.xpath(".//span/a/@href").extract_first() is None:
                pass
            else:
                content_url = 'https:'+item.xpath(".//span/a/@href").extract_first()
                info['content_id'] = content_id_search.search(content_url).group(1)
                info['content_ajax_url'] = "https://xiaoguotu.to8to.com/case/list?a2=0&a12=&a11="+str(info['content_id'])+"&a1=0&a17=1"
                # 使用yield来发送异步请求，使用scrapy.Request发送请求
                # 回调函数，只写方法名称，不调用
                yield scrapy.Request(url=info['content_ajax_url'],callback=self.handle_pic_parse,meta=info)

                if response.xpath("//a[@id='nextpageid']"):
                    # 当前页
                    now_page = int(response.xpath("//div[@class='pages']/strong/text()").extract_first())
                    next_page_url = "https://xiaoguotu.to8to.com/tuce/p_%d.html"%(now_page+1)
                    yield scrapy.Request(url=next_page_url,callback=self.parse)
                    break



    # 因为前面已经发送request请求，所以这里接受response
    def handle_pic_parse(self,response):
        # print(response.request.meta)
        pic_dict_data = json.loads(response.text)['dataImg']
        print(pic_dict_data)
        for pic_item in pic_dict_data:
            for item in pic_item['album']:
                tubatu_info = TubatuScrapyProjectItem()
                # 昵称
                tubatu_info["nick_name"] = item['l']['n']
                # 图片的url,数据需要改成列表数据
                # tubatu_info["pic_url"] = 'https://pic1.to8to.com/smallcase/'+item['l']['s']
                tubatu_info["image_urls"] = ['https://pic1.to8to.com/smallcase/'+item['l']['s']]
                # 图片的名称
                tubatu_info["pic_name"] = item['l']['t']
                # 装修名称
                tubatu_info["content_name"] = response.request.meta["content_name"]
                # 装修id
                tubatu_info['content_id'] = response.request.meta["content_id"]
                # 请求url
                tubatu_info['content_url'] = response.request.meta["content_ajax_url"]
                print(tubatu_info)
                # yield到pipelines中
                # yield tubatu_info


