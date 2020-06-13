# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import base64
import random
import re

import execjs
from scrapy import signals


class GuaziScrapyProjectSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class GuaziScrapyProjectDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    # 发送请求之前
    # request参数就是一个request对象，就是当前被处理的request
    # spider 就是一个spider对象，当前request对应的spider
    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # ---------------------------------------------------------------
        # 返回是None的时候，scrapy将继续处理该request，得到的response的时候才结束
        # - return None: continue processing this request
        # ---------------------------------------------------------------
        # 返回的是response时，不会去调用更低优先等级的DownloaderMiddleware里的process_request和process_exception
        # 转而会去调用process的process_response，然后发送给spider
        # - or return a Response object
        # ---------------------------------------------------------------
        # 返回的是request时，更低优先级的DownloaderMiddleware里的process_request方法会停止执行
        # 会重新放入调度器去
        # - or return a Request object
        # ---------------------------------------------------------------
        # 如果返回有异常，所有process_exception会被依次执行
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    # 当下载器返回response到spider
    # request对象，当前response对应的request
    # response，当前被处理的response
    # spider,当前response对应的spider
    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # ---------------------------------------------------------------
        # - return a Response object
        # 更低优先级里面的process_response方法会被继续调用
        # ---------------------------------------------------------------
        # - return a Request object
        # 更低优先级的process_response方法不会继续被调用
        # 重新放到调度器队列中
        # 会被process_request方法顺次处理
        # ---------------------------------------------------------------
        # - or raise IgnoreRequest
        # 触发异常会被调用到解析器中的errback回调，如果仍未处理，就会被忽略
        # 不会进入process_exception中
        return response

    # request对象，残生异常的request
    # exception,就是当前抛出的异常
    # spider对象，当前request对应的spider
    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # 放返回值为None,更低优先级的process_exception会被调用
        # ---------------------------------------------------------------
        # - return a Response object: stops process_exception() chain
        # 更低优先级的process_exception方法不再被调用
        # process_response则开始调用
        # ---------------------------------------------------------------
        # - return a Request object: stops process_exception() chain
        # 更低优先级的process_exception方法不再被调用
        # 放到调度器里
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class guazi_downloader_middleware(object):

    def __init__(self):
        # 读取破解的js文件
        with open("guazi.js", 'r') as f:
            self.f_read = f.read()

    def process_response(self,request,response,spider):
        if "正在打开中,请稍后..." in response.text:
            value_search = re.compile(r"anti\('(.*?)','(.*?)'\);")
            string = value_search.search(response.text).group(1)
            key = value_search.search(response.text).group(2)

            # 使用execjs包封装这段js
            js = execjs.compile(self.f_read)
            js_return = js.call('anti', string, key)
            cookie_value = {'antipas':js_return}
            print("当前所使用的cookie为:%s"%cookie_value)
            # 将获取的cookie传给头部信息
            request.cookies = cookie_value
            # 把这个请求重新放回调度器
            return request
        elif response.status == 200:
            # 正常返回
            return response
        elif '客官请求太频繁啦' in response.text:
            return request


# 要在setting中设置
# 自定义随机user-agent中间件
class my_useragent(object):

    def process_request(self,request,spider):
        user_agent_list=[
            # "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            # "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            # "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            # "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            # "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            # "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            # "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            # "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            # "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            # "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            # "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            # "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            # "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            # "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            # "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            # "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]
        # 随机选取user-agent
        agent = random.choice(user_agent_list)
        request.headers['User-Agent'] = agent


# 自定义代理
# class my_proxy(object):
#     def process_request(self,request,spider):
#         request.meta['proxy'] = 'http-dyn.abuyun.com:9020'
#         # 用户名密码
#         proxy_name_pass = 'H612J2AG15833D3D:DB46DFBC33AB69AC'.encode("utf-8")
#         encode_pass_name = base64.b64encode(proxy_name_pass)
#         # 将代理信息设置到头部去
#         # Basic后面又空格
#         request.headers['Proxy-Authorization'] = 'Basic '+encode_pass_name.decode()