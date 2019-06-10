# -*- coding: utf-8 -*-
import scrapy
import re
from copy import deepcopy
class SuningSpider(scrapy.Spider):
    name = 'suning'
    allowed_domains = ['suning.com']
    start_urls = ['http://snbook.suning.com/web/trd-fl/999999/0.htm']

    def parse(self, response):
        #获取大分类
        li_list = response.xpath("//ul[@class='ulwrap']/li")
        for li in li_list:
            item = {}
            #这是获取大分类的文本数据
            item["b_cate"] = li.xpath("./div[1]/a/text()").extract_first()
            #小分类分组
            a_list = li.xpath("./div[2]/a")
            for a in a_list:
                #获取小分类的url
                item["s_href"] = a.xpath("./@href").extract_first()
                #获取小分类的文本数据
                item["s_cate"] = a.xpath("./@text()").extract_first()
                if item["s_href"] is not None:
                    item["s_href"] = "http://snbood.suning.com/"+item["s_href"]
                    yield scrapy.Request(
                        item["s_href"],
                        callback=self.parse_book_list,
                        meta={"item":deepcopy(item)}
                    )
    def parse_book_list(self,response):
        #这里是为了保持代码的翻页item的纯净
        item = deepcopy(response.meta["item"])
        #图书列表分组
        li_list  = response.xpath("//div[@class='filtrate-book list-filtrate-books']/ul/li")
        for li in li_list:
            item["book_name"] = li.xpath(".//div[@class='book-title']/a/@title").extract_first()
            item["book_img"] = li.xpath(".//div[@class='book-img']//img/@src").extract_first()
            if item["book_img"] is None:
                item["book_img"] = li.xpath(".//div[@class='book-img']//img/@src2").extract_first()
            item["book_author"] = li.xpath(".//div[@class='book-author']/a/text()").extract_first()
            item["book_press"] = li.xpath(".//div[@class='book-publish']/a/text()")
            item["book_desc"]  = li.xpath(".//div[@class='book_descrip c6']/text()")
            item["book_href"] = li.xpath(".//div[@class='book-title']/a/@href").extract_first()
            yield scrapy.Request(
                item["book_href"],
                callback=self.parse_book_detail,
                meta={"item":deepcopy(item)}
            )
        #开始翻页：
        page_count = int(re.findall("var pagecount=(.*?)",response.body.decode())[0])
        current_page = int(re.findall("var currentPage=(.*?);",response.body.decode())[0])
        if current_page<page_count:
            next_url  = item["s_href"]+"?pageNumber={}&fort=0".format(current_page+1)
            yield scrapy.Request(
                next_url,
                callback=self.parse_book_list,
                meta={"item":response.meta["item"]}
            )
    def parse_book_detail(self,response):
        item= response.meta["item"]
        item["book_price"] = re.findall("\"bp\":'(.*?)',",response.body.decode())
        item["book_price"] = item["book_price"][0] if len(item["book_price"])>0 else None
        print(item)