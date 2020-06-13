import json

import requests
import execjs
import re

"""
请求城市和车的品牌信息
"""

from lxml import etree
from guazi_scrapy_project.guazi_scrapy_project.handle_mongodb import mongo

url = "https://www.guazi.com/www/buy"

# cookie值要删掉，否则对方根据这个值发现我们，并屏蔽我们
header = {
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding":"gzip, deflate, br",
        "Accept-Language":"zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control":"no-cache",
        "Connection":"keep-alive",
        "Host":"www.guazi.com",
        "Pragma":"no-cache",
        # "Cookie":"uuid=d08bf34b-52c0-4c02-e9f5-40d68f062661; cityDomain=www; clueSourceCode=%2A%2300; user_city_id=-1; ganji_uuid=4156626611117910190228; sessionid=a4aebf2d-9838-4e84-dbe3-e3a85e7e9a43; lg=1; antipas=748t06q8921582099B29597e; cainfo=%7B%22ca_a%22%3A%22-%22%2C%22ca_b%22%3A%22-%22%2C%22ca_s%22%3A%22self%22%2C%22ca_n%22%3A%22self%22%2C%22ca_medium%22%3A%22-%22%2C%22ca_term%22%3A%22-%22%2C%22ca_content%22%3A%22-%22%2C%22ca_campaign%22%3A%22-%22%2C%22ca_kw%22%3A%22-%22%2C%22ca_i%22%3A%22-%22%2C%22scode%22%3A%22-%22%2C%22keyword%22%3A%22-%22%2C%22ca_keywordid%22%3A%22-%22%2C%22display_finance_flag%22%3A%22-%22%2C%22platform%22%3A%221%22%2C%22version%22%3A1%2C%22client_ab%22%3A%22-%22%2C%22guid%22%3A%22d08bf34b-52c0-4c02-e9f5-40d68f062661%22%2C%22ca_city%22%3A%22sz%22%2C%22sessionid%22%3A%22a4aebf2d-9838-4e84-dbe3-e3a85e7e9a43%22%7D; preTime=%7B%22last%22%3A1590298374%2C%22this%22%3A1590295527%2C%22pre%22%3A1590295527%7D",
        "Referer":"https://www.guazi.com/www/buy",
        "Sec-Fetch-Dest":"document",
        "Sec-Fetch-Mode":"navigate",
        "Sec-Fetch-Site":"same-origin",
        "Upgrade-Insecure-Requests":"1",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
}


response = requests.get(url=url,headers=header)
response.encoding="utf-8"
print(response.text)
print(response.status_code)
if "正在打开中,请稍后..." in response.text:
        value_search = re.compile(r"anti\('(.*?)','(.*?)'\);")
        string = value_search.search(response.text).group(1)
        key = value_search.search(response.text).group(2)
        # 读取破解的js文件
        with open("guazi.js",'r') as f:
                f_read = f.read()
        # 使用execjs包封装这段js
        js = execjs.compile(f_read)
        js_return = js.call('anti',string,key)
        # print(js_return)
        cookie_value = "antipas="+js_return
        print(cookie_value)
        # 将获取的cookie传给头部信息
        header['Cookie'] = cookie_value
        # print(header)
        # 获取的html数据
        response_second = requests.get(url=url,headers=header)
        # print(response_second.text)
        guazi_html = etree.HTML(response_second.text)
        script_js = guazi_html.xpath("//script[3]/text()")[0]
        city_search = re.compile(r'({.*?});')
        city = city_search.findall(script_js)
        # print(city)
        # cityLeft获取城市的中文和英文名
        # json.loads是将json数据转换成字典格式
        cityOne = json.loads(city[0])
        cityTwo = json.loads(city[1])
        A_N = [chr(i) for i in range(65, 78)]
        M_Z = [chr(i) for i in range(78, 91)]
        all_city = []
        for i in A_N:
                # 根据获取相同首字母的城市列表
                each_list1 = cityOne.get(i)
                if each_list1:
                        all_city.append(each_list1)
        for i in M_Z:
                each_list2 = cityTwo.get(i)
                if each_list2:
                        all_city.append(each_list2)
        # print(all_city)
        for each_list in all_city:
                # print(each_list)
                # 获取到城市名称信息
                for city in each_list:
                        # print(city)
                        # city_list = city['domain']
                        # cityname = city['name']
                        if city["name"] =="深圳":
                                brand_search = re.compile(r'href="\/www\/(.*?)\/c-1\/#bread"\s+>(.*?)</a>')
                                # 获取车品牌信息
                                brand_list = brand_search.findall(response_second.text)
                                for brand in brand_list:
                                        info = {}
                                        # https://www.guazi.com/anji/buy
                                        # https://www.guazi.com/anji/dazhong/#bread
                                        # https://www.guazi.com/anji/dazhong/o3i7/#bread
                                        # 获取每个城市每个品牌的每页数据的url
                                        info['task_url'] = "https://www.guazi.com/"+city["domain"]+"/"+brand[0]+"/"+"o1i7"
                                        info['city_name'] = city["name"]
                                        info['brand_name'] = brand[1]
                                        info['item_type'] = 'list_item'
                                        # 保存到mongodb
                                        # print(info)
                                        if info['brand_name'] =="奥迪":
                                                mongo.save_task("guazi_task",info)
