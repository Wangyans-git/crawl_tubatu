import os
from multiprocessing import Process

from scrapy import cmdline
# 在scrapy项目里，方便运行项目

def crawl():
    cmdline.execute("scrapy crawl crawl_dongqiudi".split())

crawl()

