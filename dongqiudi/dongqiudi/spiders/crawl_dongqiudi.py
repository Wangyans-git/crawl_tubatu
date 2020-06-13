# -*- coding: utf-8 -*-
import datetime
import json
import time
import scrapy

from dongqiudi.items import DongqiudiItem

class CrawlDongqiudiSpider(scrapy.Spider):
    name = 'crawl_dongqiudi'
    allowed_domains = ['dongqiudi.com']
    start_urls = ['https://www.dongqiudi.com/news']

    def start_requests(self,time_value=None):
        # https://www.dongqiudi.com/api/app/tabs/web/3.json?after=1590521979&page=1
        if time_value == None:
            time_value = int(time.time())
        # 获取url
        for item_value in [56]:
            page_url = "https://www.dongqiudi.com/api/app/tabs/web/%s.json?after=%s&page=1"%(item_value,time_value)
            # print(page_url)
            yield scrapy.Request(url=page_url,callback=self.handle_page_response,dont_filter=True)

    # 处理页码请求的返回
    def handle_page_response(self,response):
        response_dict = json.loads(response.text)
        next_url = response_dict.get("next")
        if next_url:
            # 请求下一页
            yield scrapy.Request(url=next_url,callback=self.handle_page_response,dont_filter=True)
        news_list = response_dict.get('articles')
        if news_list:
            for item in news_list:
                info = {}
                info['from_url'] = item.get('url')
                # info['from_url'] = item['share']
                info['title'] = item.get('title')
                info['release_time'] = item.get("published_at")
                # print(info)
                yield scrapy.Request(url=info['from_url'],callback=self.handle_info_response,dont_filter=True,meta=info)

    def handle_info_response(self,response):
        news_info = DongqiudiItem()
        # 抓取URL
        news_info['from_url'] = response.request.meta['from_url']
        # 新闻标题
        news_info['title'] = response.request.meta['title']
        # 发表时间
        news_info['release_time'] = response.request.meta['release_time']
        # 作者
        news_info['author'] = response.xpath("//h2/writer/text()|//p[@class='tips']/span/text()|//h2/a/text()")\
            .extract_first().strip()
        # 新闻内容
        news_info['content'] = ''.join(response.xpath("//div[@class='con']//p//text()").extract()).replace('\n','')
        # 抓取时间
        news_info['crawl_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 图片信息
        news_info['images'] = response.xpath("//div[@class='con']/h2/text()").extract_first()
        news_info['image_urls'] = response.xpath("//div[@class='con']//img/@src|//div[@class='con']//img/@data-src").extract()
        yield news_info
        # print(news_info)