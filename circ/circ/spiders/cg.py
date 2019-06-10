# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import re

class CgSpider(CrawlSpider):
    name = 'cg'
    allowed_domains = ['circ.gov.cn']
    start_urls = ['http://circ.gov.cn/']
    #这里是定义提取url地址规则
    #callback 提取出来的url地址的response会交给callback处理
    #follow 当前url地址的响应重新进入rules来提取url地址
    rules = (
        Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        item = {}
        #i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        #i['name'] = response.xpath('//div[@id="name"]').extract()
        #i['description'] = response.xpath('//div[@id="description"]').extract()
        item["title"] = re.findall("<!--TitleStart-->(.*?)<!---TitleEnd-->",response.body.decode())[0]
        item["publish_date"] = re.findall("发布时间:(20\d{2}-\d{2}-\d{2})",response.body.decode())[0]

